"""
The Last Signal - Client anti-cheat
===================================
Stdlib uniquement. Fonctionne avec anti_vpn_client.py (VpnGuard).

    from anti_vpn_client import VpnGuard
    from anti_cheat_client import AntiCheat

    guard = VpnGuard("https://ton-serveur.exemple", on_blocked=..., on_offline=...)
    guard.start()

    ac = AntiCheat(
        "https://ton-serveur.exemple", guard,
        get_google_token=lambda: mon_id_token_google,      # None si tu n'utilises pas Google
        on_cheat=lambda why: root.after(0, lambda: afficher_et_quitter(why)),
    )
    ac.start()                       # surveillance en arriere-plan

    run_id = ac.start_run()          # debut d'une partie
    ...
    result = ac.finish_run(score, {"kills": 12})    # fin de partie
    if result and result.get("accepted"): ...

    ac.save({"level": 3, "money": 120})              # sauvegarde serveur
    data = ac.load()                                 # chargement

ATTENTION : les verifications locales (debogueur, outils de triche, hash de l'exe)
sont un OBSTACLE, pas une preuve : un tricheur determine peut les contourner.
La vraie protection, c'est le serveur (chronometrage, regles, bans par compte).
"""

import hashlib
import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request

TIMEOUT = 8

# Outils couramment utilises pour tricher ou alterer les echanges reseau
SUSPECT_PROCESSES = (
    "cheatengine", "cheat engine", "x64dbg", "x32dbg", "ollydbg", "ida64", "idaq",
    "processhacker", "artmoney", "gameconqueror", "scanmem", "dnspy", "ghidra",
    "fiddler", "charles", "mitmproxy", "httpdebugger",
)

_exe_hash_cache = None


def exe_hash():
    """SHA-256 de l'exe (vide si le jeu tourne en .py)."""
    global _exe_hash_cache
    if _exe_hash_cache is not None:
        return _exe_hash_cache
    if not getattr(sys, "frozen", False):
        _exe_hash_cache = ""
        return ""
    h = hashlib.sha256()
    try:
        with open(sys.executable, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        _exe_hash_cache = h.hexdigest()
    except Exception:
        _exe_hash_cache = ""
    return _exe_hash_cache


def _process_list():
    try:
        if os.name == "nt":
            out = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"], capture_output=True, timeout=8,
                encoding="utf-8", errors="ignore", creationflags=0x08000000,  # sans fenetre
            ).stdout
        else:
            out = subprocess.run(
                ["ps", "-A", "-o", "comm="], capture_output=True, timeout=8,
                encoding="utf-8", errors="ignore",
            ).stdout
        return out.lower()
    except Exception:
        return ""


def _debugger_attached():
    if sys.gettrace() is not None:
        return True
    if os.name == "nt":
        try:
            import ctypes
            return bool(ctypes.windll.kernel32.IsDebuggerPresent())
        except Exception:
            return False
    return False


def scan():
    """Retourne la liste des anomalies detectees sur la machine."""
    findings = []
    if _debugger_attached():
        findings.append("debugger")
    procs = _process_list()
    for name in SUSPECT_PROCESSES:
        if name in procs:
            findings.append("tool:" + name)
    return findings


class AntiCheat:
    def __init__(self, server_url, guard, get_google_token=None, on_cheat=None, scan_every=60):
        self.server_url = server_url.rstrip("/")
        self.guard = guard
        self.get_google_token = get_google_token
        self.on_cheat = on_cheat
        self.scan_every = scan_every
        self.banned = False
        self._stop = threading.Event()
        self._thread = None

    # ---- surveillance en arriere-plan --------------------------------
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _loop(self):
        self.guard.wait_ready(15)
        first = True
        while not self._stop.is_set():
            findings = scan()
            if findings or first:
                self._call("POST", "/report", {"findings": findings, "exe_hash": exe_hash()})
                first = False
            if findings and self.on_cheat:
                self.on_cheat(",".join(findings))
            self._stop.wait(self.scan_every)

    # ---- parties ----------------------------------------------------
    def start_run(self):
        status, data = self._call("POST", "/run/start", {})
        return data.get("run_id") if status == 200 else None

    def finish_run(self, run_id, score, stats=None):
        status, data = self._call("POST", "/run/finish",
                                  {"run_id": run_id, "score": int(score), "stats": stats or {}})
        return data if status == 200 else None

    # ---- sauvegarde -------------------------------------------------
    def save(self, data):
        status, _ = self._call("PUT", "/save", data)
        return status == 200

    def load(self):
        status, data = self._call("GET", "/save")
        return data.get("data") if status == 200 else None

    # ---- reseau -----------------------------------------------------
    def _call(self, method, path, payload=None):
        body = None
        if method in ("POST", "PUT"):
            body = json.dumps(payload if payload is not None else {}).encode()
        headers = {"User-Agent": "TheLastSignal/1.0", "Content-Type": "application/json"}
        headers.update(self.guard.headers())
        if self.get_google_token:
            tok = self.get_google_token()
            if tok:
                headers["X-LS-Google"] = tok
        req = urllib.request.Request(self.server_url + path, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.status, json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                data = json.loads(e.read().decode() or "{}")
            except Exception:
                data = {}
            if e.code == 403 and data.get("detail") == "banned":
                self.banned = True
                if self.on_cheat:
                    self.on_cheat("banned")
            return e.code, data
        except Exception:
            return 0, {}
