"""
The Last Signal - Client anti-VPN
=================================
Aucune dependance externe (stdlib uniquement) : simple a inclure dans l'exe.

Utilisation dans le menu tkinter :

    from anti_vpn_client import VpnGuard

    guard = VpnGuard(
        "https://ton-serveur.exemple",
        on_blocked=lambda: root.after(0, show_vpn_error),   # thread-safe pour tkinter
        on_offline=lambda: root.after(0, show_offline_error),
    )
    guard.start()

    # Avant toute action en ligne :
    if guard.wait_ready(timeout=8):
        requests_headers = guard.headers()      # a envoyer dans X-LS-Token
    else:
        ...                                     # bloque / hors ligne
"""

import json
import threading
import time
import urllib.error
import urllib.request

RENEW_EVERY = 240      # secondes (le jeton dure 600 s cote serveur)
TIMEOUT = 6


class VpnGuard:
    def __init__(self, server_url, on_blocked=None, on_offline=None, on_ok=None):
        self.server_url = server_url.rstrip("/")
        self.on_blocked = on_blocked
        self.on_offline = on_offline
        self.on_ok = on_ok
        self._token = None
        self._blocked = False
        self._ready = threading.Event()
        self._stop = threading.Event()
        self._thread = None

    # ---- API publique ------------------------------------------------
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def headers(self):
        """En-tetes a joindre a chaque requete en ligne."""
        return {"X-LS-Token": self._token or ""}

    @property
    def token(self):
        return self._token

    @property
    def blocked(self):
        return self._blocked

    def wait_ready(self, timeout=8):
        """True si un jeton valide est disponible, False sinon (VPN, hors ligne...)."""
        self._ready.wait(timeout)
        return self._token is not None

    # ---- interne -----------------------------------------------------
    def _loop(self):
        while not self._stop.is_set():
            self._renew()
            self._ready.set()
            self._stop.wait(RENEW_EVERY if self._token else 20)

    def _renew(self):
        req = urllib.request.Request(
            f"{self.server_url}/session",
            data=b"",
            method="POST",
            headers={"User-Agent": "TheLastSignal/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = json.loads(r.read().decode("utf-8"))
            self._token = data["token"]
            self._blocked = False
            if self.on_ok:
                self.on_ok()
        except urllib.error.HTTPError as e:
            self._token = None
            if e.code == 403:
                self._blocked = True
                if self.on_blocked:
                    self.on_blocked()
            else:
                if self.on_offline:
                    self.on_offline()
        except Exception:
            self._token = None
            if self.on_offline:
                self.on_offline()


if __name__ == "__main__":
    # Test rapide en console : python anti_vpn_client.py https://ton-serveur.exemple
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    g = VpnGuard(
        url,
        on_blocked=lambda: print("VPN detecte -> acces refuse"),
        on_offline=lambda: print("Serveur injoignable"),
        on_ok=lambda: print("OK : jeton obtenu"),
    )
    g.start()
    print("pret" if g.wait_ready(10) else "pas de jeton")
    time.sleep(1)
