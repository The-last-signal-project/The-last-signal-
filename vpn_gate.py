"""
The Last Signal - Serveur anti-VPN
===================================

Lancement :
    pip install fastapi uvicorn requests
    set LS_SECRET=une_longue_chaine_aleatoire          (Linux : export ...)
    set PROXYCHECK_KEY=ta_cle_proxycheck_io
    set IPQS_KEY=ta_cle_ipqualityscore                 (optionnel, 2e avis)
    uvicorn vpn_gate:app --host 0.0.0.0 --port 8000

Generer un secret :
    python -c "import secrets; print(secrets.token_urlsafe(64))"

Variables optionnelles :
    TRUSTED_PROXIES   IP de ton reverse proxy (nginx...), separees par des virgules.
                      L'en-tete X-Forwarded-For n'est lu QUE si la connexion vient d'eux.
    LS_ALLOW_LOCAL=1  accepte les IP locales/privees (utile pour tester chez toi).
    RISK_LIMIT        score de risque max tolere, 0-100 (defaut 66).
    TOKEN_TTL         duree de vie du jeton en secondes (defaut 600).

IMPORTANT : mets ce serveur derriere HTTPS (nginx, Caddy, Cloudflare...).
"""

import base64
import hashlib
import hmac
import ipaddress
import json
import logging
import os
import threading
import time
from collections import defaultdict, deque

import requests
from fastapi import Depends, FastAPI, HTTPException, Request

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
SECRET = os.environ.get("LS_SECRET", "").encode()
PROXYCHECK_KEY = os.environ.get("PROXYCHECK_KEY", "")
IPQS_KEY = os.environ.get("IPQS_KEY", "")
TRUSTED_PROXIES = {p.strip() for p in os.environ.get("TRUSTED_PROXIES", "").split(",") if p.strip()}
ALLOW_LOCAL = os.environ.get("LS_ALLOW_LOCAL", "0") == "1"
RISK_LIMIT = int(os.environ.get("RISK_LIMIT", "66"))
TOKEN_TTL = int(os.environ.get("TOKEN_TTL", "600"))

CACHE_TTL = 3600          # un resultat d'IP est garde 1 h
CACHE_MAX = 50_000        # taille max du cache
RATE_LIMIT = 20           # requetes /session max ...
RATE_WINDOW = 60          # ... par fenetre de 60 s et par IP
HTTP_TIMEOUT = 4

if len(SECRET) < 32:
    raise RuntimeError("LS_SECRET manquant ou trop court (32 caracteres minimum).")
if not PROXYCHECK_KEY and not IPQS_KEY:
    raise RuntimeError("Il faut au moins PROXYCHECK_KEY ou IPQS_KEY.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("vpn_gate")

app = FastAPI(title="The Last Signal - VPN gate", docs_url=None, redoc_url=None, openapi_url=None)

# --------------------------------------------------------------------------
# IP du client (jamais fournie par le client lui-meme)
# --------------------------------------------------------------------------
def client_ip(request: Request) -> str:
    peer = request.client.host if request.client else ""
    if peer in TRUSTED_PROXIES:
        xff = request.headers.get("x-forwarded-for", "")
        if xff:
            # la derniere entree est celle ajoutee par NOTRE proxy
            return xff.split(",")[-1].strip()
    return peer


# --------------------------------------------------------------------------
# Rate limit simple en memoire
# --------------------------------------------------------------------------
_hits: dict[str, deque] = defaultdict(deque)
_hits_lock = threading.Lock()


def rate_limited(ip: str) -> bool:
    now = time.time()
    with _hits_lock:
        q = _hits[ip]
        while q and now - q[0] > RATE_WINDOW:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return True
        q.append(now)
        if len(_hits) > 100_000:
            _hits.clear()
    return False


# --------------------------------------------------------------------------
# Detection VPN / proxy
# --------------------------------------------------------------------------
_cache: dict[str, tuple[float, bool]] = {}
_cache_lock = threading.Lock()


def _check_proxycheck(ip: str):
    """True = a bloquer, False = propre, None = indisponible."""
    if not PROXYCHECK_KEY:
        return None
    try:
        r = requests.get(
            f"https://proxycheck.io/v2/{ip}",
            params={"key": PROXYCHECK_KEY, "vpn": 3, "risk": 1, "asn": 1},
            timeout=HTTP_TIMEOUT,
        )
        data = r.json()
        if data.get("status") not in ("ok", "warning"):
            log.warning("proxycheck statut inattendu: %s", data.get("status"))
            return None
        info = data.get(ip, {})
        return info.get("proxy") == "yes" or int(info.get("risk", 0)) >= RISK_LIMIT
    except Exception as e:
        log.warning("proxycheck indisponible: %s", e)
        return None


def _check_ipqs(ip: str):
    if not IPQS_KEY:
        return None
    try:
        r = requests.get(
            f"https://ipqualityscore.com/api/json/ip/{IPQS_KEY}/{ip}",
            params={"strictness": 1, "allow_public_access_points": "true"},
            timeout=HTTP_TIMEOUT,
        )
        d = r.json()
        if not d.get("success"):
            log.warning("ipqs echec: %s", d.get("message"))
            return None
        return bool(d.get("vpn") or d.get("tor") or d.get("proxy")
                    or int(d.get("fraud_score", 0)) >= 90)
    except Exception as e:
        log.warning("ipqs indisponible: %s", e)
        return None


def ip_is_blocked(ip: str) -> bool:
    # IP invalide -> refus
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return True

    # IP locale/privee : impossible a analyser
    if addr.is_private or addr.is_loopback or addr.is_link_local:
        return not ALLOW_LOCAL

    now = time.time()
    with _cache_lock:
        hit = _cache.get(ip)
        if hit and now - hit[0] < CACHE_TTL:
            return hit[1]

    results = [_check_proxycheck(ip), _check_ipqs(ip)]
    answers = [r for r in results if r is not None]

    if not answers:
        return True                      # fail-closed : aucun fournisseur n'a repondu

    blocked = any(answers)               # un seul avis negatif suffit
    with _cache_lock:
        if len(_cache) >= CACHE_MAX:
            _cache.clear()
        _cache[ip] = (now, blocked)
    return blocked


# --------------------------------------------------------------------------
# Jetons signes (HMAC-SHA256), lies a l'IP, avec expiration
# --------------------------------------------------------------------------
def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_token(ip: str) -> str:
    payload = json.dumps({"ip": ip, "exp": int(time.time()) + TOKEN_TTL, "v": 1},
                         separators=(",", ":")).encode()
    sig = hmac.new(SECRET, payload, hashlib.sha256).digest()
    return _b64(payload) + "." + _b64(sig)


def verify_token(token: str, ip: str) -> bool:
    try:
        p, s = token.split(".")
        payload = _unb64(p)
        good = hmac.new(SECRET, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(_unb64(s), good):
            return False
        data = json.loads(payload)
        return data["ip"] == ip and data["exp"] > time.time()
    except Exception:
        return False


# --------------------------------------------------------------------------
# Dependance a mettre sur TOUTES les routes sensibles
# --------------------------------------------------------------------------
def require_clean(request: Request):
    token = request.headers.get("X-LS-Token", "")
    if not verify_token(token, client_ip(request)):
        raise HTTPException(status_code=403, detail="invalid_or_expired_token")


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.post("/session")
def session(request: Request):
    """Appelee a la connexion puis toutes les ~4 min pour renouveler le jeton."""
    ip = client_ip(request)
    if rate_limited(ip):
        raise HTTPException(status_code=429, detail="too_many_requests")
    if ip_is_blocked(ip):
        log.info("BLOQUE %s", ip)
        raise HTTPException(status_code=403, detail="vpn_detected")
    return {"token": make_token(ip), "ttl": TOKEN_TTL}


@app.post("/verify", dependencies=[Depends(require_clean)])
def verify():
    """Pour un serveur de jeu separe : il appelle /verify avec le jeton du joueur."""
    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "up"}


# Exemple de route protegee : copie ce modele pour tes vraies routes
@app.post("/multi/join", dependencies=[Depends(require_clean)])
def multi_join():
    return {"joined": True}
