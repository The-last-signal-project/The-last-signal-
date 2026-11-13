"""
The Last Signal - Serveur anti-cheat
====================================
S'ajoute a vpn_gate.py : meme serveur, memes jetons, memes routes protegees.

Lancement (a la place de vpn_gate) :
    uvicorn anti_cheat_server:app --host 0.0.0.0 --port 8000

Variables d'environnement (en plus de celles de vpn_gate.py) :
    ADMIN_KEY            cle admin longue pour /admin/* (obligatoire pour bannir a la main)
    GOOGLE_CLIENT_ID     ID client OAuth de ton jeu : active l'identification par compte Google
                         (sans lui, le joueur est identifie par son IP : pour les tests uniquement)
    ALLOWED_EXE_HASHES   SHA-256 de tes .exe officiels, separes par des virgules
    MAX_SCORE_PER_SEC    score max plausible par seconde de jeu   (defaut 50)
    MAX_SCORE            score max plausible par partie           (defaut 10000000)
    MIN_RUN_SECONDS      duree min d'une partie                   (defaut 5)
    MAX_RUN_SECONDS      duree max d'une partie                   (defaut 14400 = 4 h)
    FLAGS_BEFORE_BAN     nombre de signalements avant bannissement auto (defaut 3)
    LS_DB                chemin de la base SQLite                 (defaut lastsignal.db)

PRINCIPE : le client n'est jamais cru sur parole. Le serveur chronometre lui-meme
chaque partie, refuse de rejouer une partie deja validee, et ban le COMPTE (pas l'IP).
"""

import hmac
import json
import os
import secrets
import sqlite3
import threading
import time

import requests
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel, Field

from vpn_gate import app, client_ip, log, require_clean

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
DB_PATH = os.environ.get("LS_DB", "lastsignal.db")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
ALLOWED_EXE_HASHES = {h.strip().lower() for h in os.environ.get("ALLOWED_EXE_HASHES", "").split(",") if h.strip()}
MAX_SCORE_PER_SEC = float(os.environ.get("MAX_SCORE_PER_SEC", "50"))
MAX_SCORE = int(os.environ.get("MAX_SCORE", "10000000"))
MIN_RUN_SECONDS = float(os.environ.get("MIN_RUN_SECONDS", "5"))
MAX_RUN_SECONDS = float(os.environ.get("MAX_RUN_SECONDS", "14400"))
FLAGS_BEFORE_BAN = int(os.environ.get("FLAGS_BEFORE_BAN", "3"))
MAX_OPEN_RUNS = 5
MAX_SAVE_BYTES = 64 * 1024

if not GOOGLE_CLIENT_ID:
    log.warning("GOOGLE_CLIENT_ID absent : joueurs identifies par IP (MODE TEST UNIQUEMENT).")

# --------------------------------------------------------------------------
# Base de donnees (SQLite)
# --------------------------------------------------------------------------
_db = sqlite3.connect(DB_PATH, check_same_thread=False)
_db.row_factory = sqlite3.Row
_dblock = threading.Lock()
with _dblock:
    _db.executescript("""
        CREATE TABLE IF NOT EXISTS bans   (player TEXT PRIMARY KEY, reason TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS flags  (player TEXT, reason TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS runs   (run_id TEXT PRIMARY KEY, player TEXT, start REAL, finished INTEGER);
        CREATE TABLE IF NOT EXISTS scores (player TEXT, score INTEGER, elapsed REAL, ts REAL);
        CREATE TABLE IF NOT EXISTS saves  (player TEXT PRIMARY KEY, data TEXT, ts REAL);
    """)
    _db.commit()


def db(sql, args=(), write=False):
    """Retourne (lignes, nb_lignes_modifiees)."""
    with _dblock:
        cur = _db.execute(sql, args)
        rows = cur.fetchall() if not write else []
        if write:
            _db.commit()
        return rows, cur.rowcount


# --------------------------------------------------------------------------
# Identite du joueur
# --------------------------------------------------------------------------
_google_cache: dict[str, tuple[float, str]] = {}


def get_player(request: Request) -> str:
    if not GOOGLE_CLIENT_ID:
        return "ip:" + client_ip(request)

    token = request.headers.get("X-LS-Google", "")
    if not token:
        raise HTTPException(401, "login_required")

    now = time.time()
    hit = _google_cache.get(token)
    if hit and hit[0] > now:
        return hit[1]

    try:
        r = requests.get("https://oauth2.googleapis.com/tokeninfo",
                         params={"id_token": token}, timeout=4)
        d = r.json()
        if r.status_code != 200 or d.get("aud") != GOOGLE_CLIENT_ID or int(d.get("exp", 0)) <= now:
            raise ValueError("token refuse")
        player = "g:" + d["sub"]
        exp = int(d["exp"])
    except Exception:
        raise HTTPException(401, "invalid_login")

    if len(_google_cache) > 10_000:
        _google_cache.clear()
    _google_cache[token] = (min(now + 300, exp), player)
    return player


def require_player(request: Request, _clean=Depends(require_clean)) -> str:
    """Jeton anti-VPN valide + compte identifie + compte non banni."""
    player = get_player(request)
    rows, _ = db("SELECT 1 FROM bans WHERE player=?", (player,))
    if rows:
        raise HTTPException(403, "banned")
    return player


# --------------------------------------------------------------------------
# Signalements et bannissements
# --------------------------------------------------------------------------
def ban(player: str, reason: str):
    db("INSERT OR REPLACE INTO bans VALUES (?,?,?)", (player, reason[:200], time.time()), write=True)
    log.warning("BAN %s (%s)", player, reason)


def flag(player: str, reason: str):
    db("INSERT INTO flags VALUES (?,?,?)", (player, reason[:200], time.time()), write=True)
    rows, _ = db("SELECT COUNT(*) AS c FROM flags WHERE player=?", (player,))
    log.info("FLAG %s : %s (%d)", player, reason, rows[0]["c"])
    if rows[0]["c"] >= FLAGS_BEFORE_BAN:
        ban(player, "auto: " + reason)


# --------------------------------------------------------------------------
# Parties : le serveur chronometre, le client declare
# --------------------------------------------------------------------------
class RunFinish(BaseModel):
    run_id: str = Field(max_length=64)
    score: int = Field(ge=0, le=2_000_000_000)
    stats: dict = Field(default_factory=dict)


@app.post("/run/start")
def run_start(player: str = Depends(require_player)):
    now = time.time()
    db("DELETE FROM runs WHERE finished=0 AND start<?", (now - MAX_RUN_SECONDS,), write=True)
    rows, _ = db("SELECT COUNT(*) AS c FROM runs WHERE player=? AND finished=0", (player,))
    if rows[0]["c"] >= MAX_OPEN_RUNS:
        raise HTTPException(429, "too_many_open_runs")
    run_id = secrets.token_urlsafe(24)
    db("INSERT INTO runs VALUES (?,?,?,0)", (run_id, player, now), write=True)
    return {"run_id": run_id}


def validate_run(score: int, elapsed: float, stats: dict) -> list[str]:
    """
    Regles de plausibilite. ADAPTE-LES a ton jeu (par ex. verifie stats["kills"],
    stats["items"], etc. par rapport a la duree).
    """
    problems = []
    if elapsed < MIN_RUN_SECONDS:
        problems.append("run_too_short")
    if elapsed > MAX_RUN_SECONDS:
        problems.append("run_too_long")
    if score > MAX_SCORE:
        problems.append("score_over_max")
    if score / max(elapsed, 1.0) > MAX_SCORE_PER_SEC:
        problems.append("score_rate_impossible")
    return problems


@app.post("/run/finish")
def run_finish(body: RunFinish, player: str = Depends(require_player)):
    now = time.time()
    if len(json.dumps(body.stats)) > 4000:
        raise HTTPException(413, "stats_too_large")

    rows, _ = db("SELECT start FROM runs WHERE run_id=? AND player=?", (body.run_id, player))
    if not rows:
        raise HTTPException(404, "unknown_run")

    # Une partie ne se valide qu'une seule fois (anti-rejeu), de facon atomique
    _, changed = db("UPDATE runs SET finished=1 WHERE run_id=? AND player=? AND finished=0",
                    (body.run_id, player), write=True)
    if changed == 0:
        flag(player, "run_replay")
        raise HTTPException(409, "run_already_finished")

    elapsed = now - rows[0]["start"]          # duree mesuree par LE SERVEUR
    problems = validate_run(body.score, elapsed, body.stats)
    if problems:
        flag(player, ",".join(problems))
        return {"accepted": False}

    db("INSERT INTO scores VALUES (?,?,?,?)", (player, body.score, elapsed, now), write=True)
    best, _ = db("SELECT MAX(score) AS b FROM scores WHERE player=?", (player,))
    return {"accepted": True, "best": best[0]["b"]}


# --------------------------------------------------------------------------
# Sauvegarde cote serveur (le fichier local n'est plus la reference)
# --------------------------------------------------------------------------
def validate_save(old: dict | None, new: dict) -> bool:
    """
    A ADAPTER. Exemple de regles utiles :
        - new["level"] ne peut pas augmenter de plus de 1 d'un coup
        - new["money"] ne peut pas depasser old["money"] + ce que les parties validees ont rapporte
    Par defaut : tout est accepte (donc un tricheur qui appelle l'API directement peut
    envoyer une fausse sauvegarde : plus tu ajoutes de regles, plus c'est solide).
    """
    return True


@app.put("/save")
async def save_put(request: Request, player: str = Depends(require_player)):
    raw = await request.body()
    if len(raw) > MAX_SAVE_BYTES:
        raise HTTPException(413, "save_too_large")
    try:
        new = json.loads(raw)
        if not isinstance(new, dict):
            raise ValueError
    except Exception:
        raise HTTPException(400, "invalid_json")

    rows, _ = db("SELECT data FROM saves WHERE player=?", (player,))
    old = json.loads(rows[0]["data"]) if rows else None
    if not validate_save(old, new):
        flag(player, "save_rejected")
        raise HTTPException(422, "save_rejected")

    db("INSERT OR REPLACE INTO saves VALUES (?,?,?)",
       (player, json.dumps(new, separators=(",", ":")), time.time()), write=True)
    return {"ok": True}


@app.get("/save")
def save_get(player: str = Depends(require_player)):
    rows, _ = db("SELECT data FROM saves WHERE player=?", (player,))
    return {"data": json.loads(rows[0]["data"]) if rows else None}


# --------------------------------------------------------------------------
# Rapports d'integrite du client (signal supplementaire, jamais une preuve)
# --------------------------------------------------------------------------
class Report(BaseModel):
    findings: list[str] = Field(default_factory=list)
    exe_hash: str = Field(default="", max_length=128)


@app.post("/report")
def report(body: Report, player: str = Depends(require_player)):
    findings = [f[:40] for f in body.findings[:10]]
    if ALLOWED_EXE_HASHES and body.exe_hash.lower() not in ALLOWED_EXE_HASHES:
        findings.append("exe_not_official")
    if findings:
        flag(player, "client:" + ",".join(findings[:5]))
    return {"ok": True}


# --------------------------------------------------------------------------
# Administration (a toi uniquement)
# --------------------------------------------------------------------------
def require_admin(request: Request):
    key = request.headers.get("X-Admin-Key", "")
    if not ADMIN_KEY or not hmac.compare_digest(key.encode(), ADMIN_KEY.encode()):
        raise HTTPException(403, "forbidden")


class AdminTarget(BaseModel):
    player: str = Field(max_length=200)
    reason: str = Field(default="manual", max_length=200)


@app.post("/admin/ban", dependencies=[Depends(require_admin)])
def admin_ban(body: AdminTarget):
    ban(body.player, body.reason)
    return {"ok": True}


@app.post("/admin/unban", dependencies=[Depends(require_admin)])
def admin_unban(body: AdminTarget):
    db("DELETE FROM bans WHERE player=?", (body.player,), write=True)
    db("DELETE FROM flags WHERE player=?", (body.player,), write=True)
    return {"ok": True}


@app.get("/admin/flags/{player}", dependencies=[Depends(require_admin)])
def admin_flags(player: str):
    rows, _ = db("SELECT reason, ts FROM flags WHERE player=? ORDER BY ts DESC LIMIT 100", (player,))
    banned, _ = db("SELECT reason FROM bans WHERE player=?", (player,))
    return {"banned": bool(banned), "flags": [dict(r) for r in rows]}
