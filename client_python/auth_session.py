# -*- coding: utf-8 -*-
"""
Module d'authentification réseau du client Python pour The Last Signal.
Gère les communications réseau pour l'inscription, la connexion, la liste
et la création de comptes avec sélection de classe.
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
CREATE_TIMEOUT = 40.0          # Inscription / création : hachage Argon2 + base SQLite
MAX_FRAME = 10 * 1024 * 1024
 
# Liste des 13 classes disponibles dans The Last Signal
AVAILABLE_CLASSES = [
    "Mage", "Nécromancien", "Épéiste", "Chevalier lourd", "Chevalier",
    "Soldat d'infanterie", "Soldat de cavalerie", "Gendarme",
    "Force spéciale d'intervention", "Voleur", "Assassin", "Sorcier", "Archer"
]
 
_REPLY_TYPES = {
    PacketType.LoginResponse,
    PacketType.SignUpResponse,
    PacketType.ACCOUNT_LIST_RESPONSE,
    PacketType.ACCOUNT_RESULT,
    PacketType.BAN,
}
 
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
    """Clé de traduction du menu ou message directement rédigé par le serveur."""
    def __init__(self, key):
        super().__init__(key)
        self.key = key
 
def _recv_exact(sock, size):
    buf = bytearray()
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("Connexion fermée")
        buf.extend(chunk)
    return bytes(buf)
 
def read_body(sock):
    """Lit une trame complète -> octets [type u16][charge utile]."""
    size = struct.unpack(">I", _recv_exact(sock, 4))[0]
    if size < 2 or size > MAX_FRAME:
        raise ConnectionError("Trame invalide")
    return _recv_exact(sock, size)
 
def _text(payload):
    return payload.decode("utf-8", "replace")
 
def _ban_key(ban):
    return "err_banned_perm" if getattr(ban, "ban_type", 0) == 2 else "err_banned_temp"
 
def check_login_reply(payload):
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
    """Lit la réponse JSON -> liste de dict {account_id, account_name, class_name, role_name, balance}."""
    try:
        accounts = json.loads(payload)
    except ValueError:
        accounts = None
 
    if isinstance(accounts, list):
        return accounts
    raise AuthError("srv_lost" if _text(payload) == "Utilisateur non authentifie" else "srv_error")
 
def check_account_result(payload):
    """Vérifie le paquet AccountResult JSON {"ok": bool, "message": str, ...}."""
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
    except struct.error:
        raise AuthError("err_fill")
 
class Connection:
    """Session du menu auprès du serveur réseau."""
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
        try:
            self.client.connect(timeout=CONNECT_TIMEOUT)
        except (SystemExit, Exception):
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
                except Exception:
                    continue
 
                if packet.packet_type in _REPLY_TYPES:
                    self._replies.put(packet)
        except Exception:
            pass
        finally:
            self.alive = False
            self._replies.put(None)
 
    def _drain(self):
        try:
            while True:
                item = self._replies.get_nowait()
                if item is not None and item.packet_type == PacketType.BAN:
                    raise AuthError(_ban_key(item))
        except queue.Empty:
            pass
 
    def request(self, packet, reply_type, timeout=REPLY_TIMEOUT):
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
 
    def login(self, email, password, retries=0, delay=0.4):
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
        try:
            packet = SingupPacket(email, password, pseudo)
        except struct.error:
            raise AuthError("err_fill")
        check_signup_reply(self.request(packet, PacketType.SignUpResponse, timeout=CREATE_TIMEOUT))
 
    def list_accounts(self):
        return parse_account_list(
            self.request(Packet(PacketType.ACCOUNT_LIST), PacketType.ACCOUNT_LIST_RESPONSE))
 
    def create_account(self, name, class_name):
        """Transmet au serveur Rust une charge utile JSON contenant account_name et class_name."""
        payload = json.dumps({
            "account_name": name,
            "class_name": class_name
        }).encode("utf-8")
        
        packet = Packet(PacketType.ACCOUNT_CREATE, payload)
        data = check_account_result(self.request(packet, PacketType.ACCOUNT_RESULT, timeout=CREATE_TIMEOUT))
        account = data.get("account")
        if not isinstance(account, dict) or "account_id" not in account:
            raise AuthError("srv_error")
        return account
 
    def select_account(self, account_id):
        packet = Packet(PacketType.ACCOUNT_SELECT, struct.pack("!q", int(account_id)))
        check_account_result(self.request(packet, PacketType.ACCOUNT_RESULT))
 
    def close(self, wait=3.0):
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
 
        client.connected = False
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
 
def authenticate_client(client, email, password, account_id, retries=25, delay=0.4):
    skipped = []
    def wait(reply_type):
        while True:
            try:
                packet = client.receive_packet()
            except SystemExit:
                raise AuthError("err_banned_temp")
            if packet is None:
                raise AuthError("srv_lost")
            if packet.packet_type == reply_type:
                return packet.payload
            if packet.packet_type in (PacketType.PLAYER_STATE, PacketType.PLAYER_REMOVE,
                                      PacketType.ZONE_STATE):
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
    client.send_packet(Packet(PacketType.SPAWN))
 

