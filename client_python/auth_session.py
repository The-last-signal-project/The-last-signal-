# -*- coding: utf-8 -*-
"""
Authentification de The Last Signal (côté client Python), construite sur le Client réseau
et les paquets du projet (LoginPacket, SingupPacket, ...).

Le menu ouvre la connexion au moment où l'on appuie sur « Se connecter » / « S'enregistrer »
puis envoie Login ou SignUp au serveur. Le lanceur de jeu rejoue ensuite login + choix du
compte sur sa propre connexion (le serveur lie le compte à la connexion TCP).
"""
import json
import queue
import socket
import struct
import threading
import time

from .client import Client
from .packet import Packet, PacketType
from .packets.login import LoginPacket
from .packets.singup import SingupPacket
from .packets.Deco import decoPacket

HOST = "127.0.0.1"
PORT = 5000
CONNECT_TIMEOUT = 4.0
REPLY_TIMEOUT = 10.0
CREATE_TIMEOUT = 40.0          # inscription / création de compte : hachage Argon2 + base de données
MAX_FRAME = 10 * 1024 * 1024

# Seuls ces paquets sont des réponses à une requête du menu ; le reste (snapshot des joueurs,
# positions...) est lu puis ignoré pour ne jamais encombrer la socket.
_REPLY_TYPES = {
    PacketType.LoginResponse,
    PacketType.SignUpResponse,
    PacketType.ACCOUNT_LIST_RESPONSE,
    PacketType.ACCOUNT_RESULT,
    PacketType.BAN,
}

# Messages renvoyés par le serveur -> clés de traduction du menu.
_LOGIN_ERRORS = {
    "Identifiants invalides": "err_creds",
    "Compte banni definitivement": "err_banned_perm",
    "Compte temporairement banni": "err_banned_temp",
    "Trop de tentatives. Compte bloque temporairement.": "err_locked",
    "Ce compte est deja connecte": "err_already",
}
_SIGNUP_ERRORS = {
    "Pseudo deja utilise": "err_pseudo_used",
    "Pseudo invalide": "err_pseudo",
    "Email deja utilise": "err_email_used",
    "Mot de passe trop court": "err_pw_short",
    "Email invalide": "err_email",
}


class AuthError(Exception):
    """`key` est une clé de traduction du menu, ou un message déjà rédigé par le serveur
    (le menu affiche tel quel un texte qui n'est pas une clé)."""

    def __init__(self, key):
        super().__init__(key)
        self.key = key


# --------------------------------------------------------------------------- #
#  Lecture des trames : [taille u32][type u16][charge utile]
# --------------------------------------------------------------------------- #
def _recv_exact(sock, size):
    buf = bytearray()
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("connexion fermée")
        buf.extend(chunk)
    return bytes(buf)


def read_body(sock):
    """Lit une trame complète -> octets [type u16][charge utile] (entrée de Packet.decode)."""
    size = struct.unpack(">I", _recv_exact(sock, 4))[0]
    if size < 2 or size > MAX_FRAME:
        raise ConnectionError("trame invalide")
    return _recv_exact(sock, size)


# --------------------------------------------------------------------------- #
#  Réponses du serveur
# --------------------------------------------------------------------------- #
def _text(payload):
    return payload.decode("utf-8", "replace")


def _ban_key(ban):
    # BanPacket : ban_type 2 = définitif, 1 = temporaire.
    return "err_banned_perm" if getattr(ban, "ban_type", 0) == 2 else "err_banned_temp"


def check_login_reply(payload):
    """Retourne le nom à afficher (pseudo, ou e-mail pour un ancien compte) ou lève AuthError."""
    text = _text(payload)
    prefix, suffix = "Utilisateur ", " authentifié"
    if text.startswith(prefix) and text.endswith(suffix) and len(text) > len(prefix) + len(suffix):
        return text[len(prefix):-len(suffix)]
    raise AuthError(_LOGIN_ERRORS.get(text, "srv_error"))


def check_signup_reply(payload):
    text = _text(payload)
    if text == "Utilisateur cree avec succes":
        return
    raise AuthError(_SIGNUP_ERRORS.get(text, "srv_error"))


def parse_account_list(payload):
    """-> liste de dict {account_id, account_name, role_name, balance}."""
    try:
        accounts = json.loads(payload)
    except ValueError:
        accounts = None
    if isinstance(accounts, list):
        return accounts
    raise AuthError("srv_lost" if _text(payload) == "Utilisateur non authentifie" else "srv_error")


def check_account_result(payload):
    """AccountResult : JSON {"ok": bool, "message": str, ...}. Retourne le dict si ok."""
    try:
        data = json.loads(payload)
    except ValueError:
        raise AuthError("srv_error")
    if not isinstance(data, dict):
        raise AuthError("srv_error")
    if data.get("ok"):
        return data
    message = str(data.get("message") or "srv_error")
    raise AuthError("srv_lost" if message == "Utilisateur non authentifie" else message)


def _credentials_packet(cls, email, password):
    try:
        return cls(email, password)
    except struct.error:                       # champ de plus de 65535 octets
        raise AuthError("err_fill")


# --------------------------------------------------------------------------- #
#  Connexion du menu : un Client + un thread de lecture
# --------------------------------------------------------------------------- #
class Connection:
    """Session du menu auprès du serveur. Les méthodes sont bloquantes : à appeler depuis
    un thread (jamais depuis la boucle d'affichage). Elles lèvent AuthError."""

    def __init__(self, host=HOST, port=PORT):
        self.client = Client(host, port)
        self.alive = False
        self._reader = None
        self._replies = queue.Queue()
        self._lock = threading.Lock()

    @property
    def sock(self):
        return self.client.socket

    def open(self):
        """Connecte le client au serveur (réessaie quelques secondes si besoin)."""
        try:
            self.client.connect(timeout=CONNECT_TIMEOUT)
        except (SystemExit, Exception):        # SystemExit : délai dépassé
            raise AuthError("srv_unreachable")
        self.alive = True
        self._reader = threading.Thread(target=self._read_loop, args=(self.client.socket,), daemon=True)
        self._reader.start()
        return self

    def _read_loop(self, sock):
        try:
            while True:
                try:
                    packet = Packet.decode(read_body(sock))
                except (ConnectionError, OSError):
                    raise
                except Exception:              # paquet inconnu ou mal formé : on l'ignore
                    continue
                if packet.packet_type in _REPLY_TYPES:
                    self._replies.put(packet)
        except Exception:
            pass
        finally:
            self.alive = False
            self._replies.put(None)

    def _drain(self):
        """Jette les anciennes réponses ; un BAN reçu entre-temps est signalé."""
        try:
            while True:
                item = self._replies.get_nowait()
                if item is not None and item.packet_type == PacketType.BAN:
                    raise AuthError(_ban_key(item))
        except queue.Empty:
            pass

    def request(self, packet, reply_type, timeout=REPLY_TIMEOUT):
        """Envoie `packet` avec le Client, attend la réponse `reply_type` -> sa charge utile."""
        with self._lock:
            self._drain()
            if not self.alive or not self.client.connected:
                raise AuthError("srv_lost")
            try:
                self.client.send_packet(packet)
            except Exception:
                self.alive = False
                raise AuthError("srv_lost")
            deadline = time.monotonic() + timeout
            while True:
                left = deadline - time.monotonic()
                if left <= 0:
                    raise AuthError("srv_timeout")
                try:
                    item = self._replies.get(timeout=left)
                except queue.Empty:
                    raise AuthError("srv_timeout")
                if item is None:
                    raise AuthError("srv_lost")
                if item.packet_type == PacketType.BAN:
                    raise AuthError(_ban_key(item))
                if item.packet_type == reply_type:
                    return item.payload

    # ----- requêtes -------------------------------------------------------- #
    def login(self, email, password, retries=0, delay=0.4):
        """Envoie LOGIN et retourne le nom à afficher. `retries` : nouvelles tentatives si le serveur
        répond « déjà connecté » (il n'a pas encore nettoyé la session précédente du même compte)."""
        packet = _credentials_packet(LoginPacket, email, password)
        for attempt in range(retries + 1):
            reply = self.request(packet, PacketType.LoginResponse)
            try:
                return check_login_reply(reply)
            except AuthError as e:
                if e.key != "err_already" or attempt == retries:
                    raise
                time.sleep(delay)

    def signup(self, email, password, pseudo):
        """Envoie SIGNUP (e-mail, mot de passe, pseudo). Le serveur connecte automatiquement le
        nouvel utilisateur."""
        try:
            packet = SingupPacket(email, password, pseudo)
        except struct.error:
            raise AuthError("err_fill")
        check_signup_reply(self.request(packet, PacketType.SignUpResponse, timeout=CREATE_TIMEOUT))

    def list_accounts(self):
        return parse_account_list(
            self.request(Packet(PacketType.ACCOUNT_LIST), PacketType.ACCOUNT_LIST_RESPONSE))

    def create_account(self, name):
        packet = Packet(PacketType.ACCOUNT_CREATE, name.encode("utf-8"))
        data = check_account_result(self.request(packet, PacketType.ACCOUNT_RESULT, timeout=CREATE_TIMEOUT))
        account = data.get("account")
        if not isinstance(account, dict) or "account_id" not in account:
            raise AuthError("srv_error")
        return account

    def select_account(self, account_id):
        packet = Packet(PacketType.ACCOUNT_SELECT, struct.pack("!q", int(account_id)))
        check_account_result(self.request(packet, PacketType.ACCOUNT_RESULT))

    def close(self, wait=3.0):
        """Ferme la session. Avec `wait`, envoie DECO puis attend que le serveur ait nettoyé la
        session (il repasse le compte en DISCONNECTED avant de fermer la socket) : indispensable
        avant de relancer une connexion avec le même compte."""
        client = self.client
        sock = client.socket
        if sock is None:
            return
        if wait and self.alive:
            try:
                client.send_packet(decoPacket("Fermeture du menu"))
            except Exception:
                pass
            if self._reader is not None:
                self._reader.join(wait)
        client.connected = False               # avant la fermeture : Client ne tente plus d'envoyer
        self.alive = False
        client.socket = None
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            sock.close()
        except OSError:
            pass


# --------------------------------------------------------------------------- #
#  Lanceur de jeu : rejoue login + sélection du compte avec le Client du jeu
# --------------------------------------------------------------------------- #
def authenticate_client(client, email, password, account_id, retries=25, delay=0.4):
    """Envoie LOGIN puis ACCOUNT_SELECT avec `client` (déjà connecté, SESSION lu).

    Retourne la liste des paquets PLAYER_STATE / PLAYER_REMOVE reçus pendant l'échange (le
    snapshot que le serveur envoie dès la connexion) : le jeu doit les traiter lui aussi."""
    skipped = []

    def wait(reply_type):
        while True:
            try:
                packet = client.receive_packet()
            except SystemExit:                 # Client quitte sur un paquet BAN
                raise AuthError("err_banned_temp")
            if packet is None:
                raise AuthError("srv_lost")
            if packet.packet_type == reply_type:
                return packet.payload
            if packet.packet_type in (PacketType.PLAYER_STATE, PacketType.PLAYER_REMOVE):
                skipped.append(packet)

    sock = client.socket
    previous = sock.gettimeout()
    sock.settimeout(REPLY_TIMEOUT)
    try:
        login = _credentials_packet(LoginPacket, email, password)
        for attempt in range(retries + 1):
            client.send_packet(login)
            try:
                check_login_reply(wait(PacketType.LoginResponse))
                break
            except AuthError as e:
                if e.key != "err_already" or attempt == retries:
                    raise
                time.sleep(delay)
        client.send_packet(Packet(PacketType.ACCOUNT_SELECT, struct.pack("!q", int(account_id))))
        check_account_result(wait(PacketType.ACCOUNT_RESULT))
    finally:
        try:
            sock.settimeout(previous)
        except OSError:
            pass
    return skipped


def spawn(client):
    """Demande au serveur de faire entrer le joueur dans le monde (il n'apparaît pour les autres
    joueurs qu'à ce moment-là, pas dès la connexion)."""
    client.send_packet(Packet(PacketType.SPAWN))
