#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE LAST SIGNAL - Menu principal  (version vispy)

Installation :   pip install vispy glfw numpy pillow pygame-ce google-auth-oauthlib
(tout s'installe aussi tout seul au premier lancement du script .py)

Le menu est maintenant dessine par vispy (OpenGL) dans une fenetre glfw : meme interface qu'avant,
le texte et les boutons sont rasterises avec Pillow puis affiches comme textures sur le GPU.

Fichiers a garder dans le meme dossier que ce script :
    background.jpg        image de fond (background.png accepte aussi)
    backgrounds/          autres fonds : un fond different a chaque lancement (ajoute une image = un fond de plus)
    locales/              textes du menu : fr.json, en.json, ja.json, es.json (ajoute une langue = copie fr.json)
    sfx/                  petits sons (survol, clic, lancement)
    icon.png / icon.ico   icone de l'application
    music/                playlist d'ambiance horreur / aventure (.ogg/.mp3/.wav, lues en boucle dans le desordre)
    fonts/                polices (Saira Stencil One, Rubik Dirt - licence OFL).
                          Pour changer la police du titre : fonts/titre.ttf
    token.json            (auto) session Google en cache
    client_secret.json    (optionnel) identifiants Google (Application de bureau)

Au premier lancement, un ecran d'installation cree le dossier du jeu, copie les fichiers
et installe les modules manquants. Cree ensuite : saves/solo, saves/multi, accounts.json, settings.json
Pour brancher ton jeu : modifie App.launch_game().
Pour faire un .exe avec l'icone : double-clique sur creer_exe.bat

Controles (Parametres > Controles) : enregistres dans settings.json, cle "controls" :
    {"keyboard": {"up": "W", "jump": "SPACE", "attack": "MOUSE1", ...},
     "gamepad":  {"up": "LS_UP", "jump": "A", "attack": "RT", ...}}
Les noms de touches sont ceux de glfw sans le prefixe KEY_ (W, SPACE, LEFT_SHIFT, F5...), les boutons
souris sont MOUSE1/2/3, la manette utilise A B X Y LB RB LT RT BACK START L3 R3 DPAD_* LS_* RS_*.
Ton jeu n'a qu'a relire settings.json["controls"] (actions : up down left right sprint jump interact
attack aim reload inventory pause).
"""
import os
import sys
import json
import math
import time
import glob
import queue
import io
import random
import socket
import hmac
import shutil
import hashlib
import secrets
import colorsys
import importlib
import threading
import subprocess
import webbrowser
import urllib.request
import tempfile
from datetime import datetime


os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
FROZEN = getattr(sys, "frozen", False)

# --------------------------------------------------------------------------- #
#  Filet de securite : toute erreur est ecrite dans erreur.log (a cote du script / de l'exe)
#  et affichee dans une fenetre sous Windows, au lieu d'un "internal error" sans details.
# --------------------------------------------------------------------------- #
_HERE = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))
CRASH_FILE = os.path.join(_HERE, "erreur.log")


def _report_crash(exc_type, exc, tb):
    import traceback
    txt = "".join(traceback.format_exception(exc_type, exc, tb))
    head = f"[{datetime.now():%d/%m/%Y %H:%M:%S}] Python {sys.version.split()[0]} - {sys.platform}\n"
    try:
        with open(CRASH_FILE, "a", encoding="utf-8") as f:
            f.write(head + txt + "\n")
    except Exception:
        pass
    try:
        if sys.stderr:
            sys.stderr.write(head + txt)
    except Exception:
        pass
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0, f"{head}\n{txt[-1500:]}\nDetails complets : {CRASH_FILE}", "The Last Signal - erreur", 0x10)
        except Exception:
            pass


sys.excepthook = _report_crash
threading.excepthook = lambda a: _report_crash(a.exc_type, a.exc_value, a.exc_traceback)

# Versions minimales qui ont des roues (fichiers precompiles) pour Python 3.14
REQUIRED = (("PIL", "pillow", "12.0"), ("numpy", "numpy", "2.3.4"), ("glfw", "glfw", "2.10"),
            ("vispy", "vispy", "0.16.1"))


def _vtuple(v):
    out = []
    for part in str(v).split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out)


def _pip_install(spec):
    """Installe un module en preferant les roues precompilees (evite toute compilation sous Python 3.14)."""
    last = ""
    for extra in (["--only-binary=:all:"], []):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", *extra, spec],
                           capture_output=True, text=True, timeout=900)
        if r.returncode == 0:
            importlib.invalidate_caches()
            return
        last = (r.stdout or "")[-600:] + (r.stderr or "")[-900:]
    raise RuntimeError(f"Impossible d'installer {spec} avec Python {sys.version.split()[0]} :\n{last}")


def _ensure_modules():
    """Script .py : installe / met a jour tout seul ce qui manque (l'exe, lui, contient deja tout)."""
    from importlib import metadata
    for mod, pipname, minver in REQUIRED:
        ok = True
        try:
            importlib.import_module(mod)
            if sys.version_info >= (3, 14):
                try:
                    ok = _vtuple(metadata.version(pipname)) >= _vtuple(minver)
                except metadata.PackageNotFoundError:
                    ok = True
        except Exception:
            ok = False
        if not ok:
            if FROZEN:
                raise ImportError(f"Module {mod} manquant dans l'exe")
            print(f"Installation de {pipname}>={minver}...")
            _pip_install(f"{pipname}>={minver}")


_ensure_modules()
import numpy as np
import glfw
from vispy import app as vapp, gloo
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFont, ImageFilter, ImageChops

# --------------------------------------------------------------------------- #
#  Chemins (compatible PyInstaller)
# --------------------------------------------------------------------------- #
RES_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
EXE_DIR = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))
APP_NAME = "The Last Signal"
APP_VERSION = "4"


def default_install_dir():
    """Dossier du jeu cree par l'exe (le script .py, lui, reste dans son dossier)."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, APP_NAME)


DATA_DIR = default_install_dir() if FROZEN else EXE_DIR

SAVES_DIR = os.path.join(DATA_DIR, "saves")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")
AVATAR_FILE = os.path.join(DATA_DIR, "avatar.png")
LOG_FILE = os.path.join(DATA_DIR, "journal.log")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
GOOGLE_CONSOLE_URL = "https://console.cloud.google.com/apis/credentials"
APP_ID = "TheLastSignal.Menu"

# Voyant reseau du bouton Multijoueur : ("mon-serveur.com", 7777). Vide = on teste juste la connexion internet.
SERVER_ADDR = ("", 0)
# La musique de fond change toute seule (fondu enchaine) apres ce nombre de secondes, et a la connexion.
MAX_TRACK_SECONDS = 60
# Commande qui lance ton jeu, ex. ["jeu.exe"] ou [sys.executable, "game.py"]. Le menu ajoute --mode et --save,
# mesure le temps de jeu (affiche dans le profil) et coupe/relance la musique du menu.
GAME_COMMAND = None

BTN_W = 30


def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%d/%m %H:%M:%S}  {msg}\n")
    except Exception:
        pass


def fmt_duration(sec):
    sec = int(sec or 0)
    h, m = sec // 3600, (sec % 3600) // 60
    return f"{h} h {m:02d} min" if h else f"{m} min"



def find_asset(*parts):
    """Cherche les ressources dans DATA_DIR, RES_DIR et les assets du projet."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Remonte plusieurs niveaux pour retrouver la racine du projet.
    project_dirs = [
        script_dir,
        os.path.dirname(script_dir),
        os.path.dirname(os.path.dirname(script_dir)),
        os.path.dirname(os.path.dirname(os.path.dirname(script_dir))),
    ]

    bases = [DATA_DIR, RES_DIR]

    for project_dir in project_dirs:
        bases.append(os.path.join(project_dir, "assets"))

    for base in bases:
        path = os.path.join(base, *parts)
        if os.path.exists(path):
            return path

    # Retourne le chemin attendu, même si le fichier n'existe pas.
    return os.path.join(project_dirs[2], "assets", *parts)



BG_EXTS = (".jpg", ".jpeg", ".png", ".webp")



def list_backgrounds():
    """Recherche les fonds dans le dossier du script et dans assets/."""
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_dir, "assets")

    # Recherche dans les trois emplacements possibles.
    bases = (DATA_DIR, RES_DIR, assets_dir)
    found = []

    for base in bases:
        for name in ("background.jpg", "background.jpeg",
                     "background.png", "background.webp"):
            path = os.path.join(base, name)
            if os.path.isfile(path):
                found.append(path)

        # Dossier backgrounds/ classique.
        folder = os.path.join(base, "backgrounds")
        if os.path.isdir(folder):
            for name in sorted(os.listdir(folder)):
                path = os.path.join(folder, name)
                if os.path.isfile(path) and name.lower().endswith(BG_EXTS):
                    found.append(path)

    # Évite les doublons tout en conservant les chemins distincts.
    unique = []
    seen = set()
    for path in found:
        key = os.path.normcase(os.path.abspath(path))
        if key not in seen:
            seen.add(key)
            unique.append(path)

    return unique



def find_background(settings=None):
    """Un fond DIFFERENT a chaque lancement : tous les fonds passent une fois (ordre aleatoire) avant de se repeter,
    et le meme fond ne revient jamais deux lancements de suite. Memoire dans settings.json (bg_seen / last_bg)."""
    cands = list_backgrounds()
    if not cands:
        return find_asset("background.png")
    if settings is None:
        return cands[0]
    names = {os.path.basename(p): p for p in cands}
    seen = [n for n in settings.get("bg_seen", []) if n in names]
    fresh = [n for n in names if n not in seen and n != settings.get("last_bg")]
    if not fresh:                                   # tour termine : on recommence
        seen = []
        fresh = [n for n in names if n != settings.get("last_bg")] or list(names)
    choice = random.choice(fresh)
    settings["last_bg"], settings["bg_seen"] = choice, seen + [choice]
    return names[choice]


def find_google_secret():
    for base in (DATA_DIR, EXE_DIR, RES_DIR):
        p = os.path.join(base, "client_secret.json")
        if os.path.exists(p):
            return p
        for f in sorted(glob.glob(os.path.join(base, "client_secret*.json"))):
            return f
    return None


# --- Connexion Google (meme systeme que Recherche de contacts) ------------------------------------- #
# client_secret.json (a cote de l'appli) + token.json (cache, reconnexion silencieuse sans navigateur).
GOOGLE_SCOPES = ["openid",
                 "https://www.googleapis.com/auth/userinfo.email",
                 "https://www.googleapis.com/auth/userinfo.profile"]
TOKEN_PATH = os.path.join(DATA_DIR, "token.json")
CREDS_PATH = os.path.join(DATA_DIR, "client_secret.json")


class CredentialsNotFound(Exception):
    """Levee quand client_secret.json est introuvable a cote de l'appli."""


def load_cached_credentials():
    """Charge et rafraichit un token existant, sans jamais ouvrir de navigateur.
    Retourne None si aucun token valide n'est disponible."""
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, GOOGLE_SCOPES)
    except Exception:
        return None
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
            return creds
        except Exception:
            return None
    return None


def google_login(success_message=""):
    """Credentials valides : token en cache si possible, sinon ouvre le navigateur."""
    creds = load_cached_credentials()
    if creds:
        return creds
    secret = find_google_secret()
    if not secret:
        raise CredentialsNotFound(CREDS_PATH)
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(secret, GOOGLE_SCOPES)
    kw = dict(port=0, prompt="select_account", authorization_prompt_message="", success_message=success_message)
    try:
        creds = flow.run_local_server(timeout_seconds=240, **kw)
    except TypeError:
        creds = flow.run_local_server(**kw)
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    return creds


def google_profile(creds):
    """(nom, url_photo) du compte Google connecte."""
    req = urllib.request.Request("https://www.googleapis.com/oauth2/v3/userinfo",
                                 headers={"Authorization": "Bearer " + creds.token})
    info = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
    return info.get("name") or info.get("email") or "Google", info.get("picture")


def find_playlist():
    """Recherche les musiques dans le dossier du jeu et dans assets/music/."""
    exts = (".ogg", ".mp3", ".wav")

    # Dossier racine du projet :
    # The-last-signal/
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_dir, "assets")

    # Cherche d'abord dans les dossiers habituels, puis dans assets/
    bases = (DATA_DIR, RES_DIR, assets_dir)

    # Recherche des fichiers audio dans les dossiers music/
    for base in bases:
        folder = os.path.join(base, "music")

        if os.path.isdir(folder):
            tracks = [
                os.path.join(folder, f)
                for f in sorted(os.listdir(folder))
                if f.lower().endswith(exts)
                and os.path.isfile(os.path.join(folder, f))
            ]

            if tracks:
                return tracks

    # Recherche d'un fichier audio unique
    for base in bases:
        for ext in exts:
            path = os.path.join(base, "music" + ext)

            if os.path.isfile(path):
                return [path]

    # Dernier recours : musique d'ambiance
    path = find_asset("ambient.wav")
    return [path] if os.path.isfile(path) else []


# --------------------------------------------------------------------------- #
#  Traductions
# --------------------------------------------------------------------------- #
# (les textes sont dans le dossier locales/ : un fichier .json par langue)


# --------------------------------------------------------------------------- #
#  Utilitaires
# --------------------------------------------------------------------------- #
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass



# --------------------------------------------------------------------------- #
#  Traductions integrees : le menu reste traduit meme si le dossier locales/ est absent.
#  Les fichiers locales/*.json, s'ils existent, remplacent ces textes cle par cle.
# --------------------------------------------------------------------------- #
BASE_TR = {
    "fr": {
        "_name": "Français",
        "account": "Compte", "auth_title": "Compte", "back": "Retour", "close": "Fermer", "confirm": "Confirmer",
        "confirm_delete": "Supprimer la sauvegarde « {} » ?", "create": "Créer un compte",
        "credits": "Remerciements", "credits_title": "Remerciements", "delete": "Supprimer",
        "err_creds": "Identifiant ou mot de passe incorrect.", "err_exists": "Cet identifiant existe déjà.",
        "err_fill": "Remplis tous les champs.", "err_mismatch": "Les mots de passe ne correspondent pas.",
        "err_short": "Mot de passe trop court (6 caractères minimum).", "fullscreen": "Plein écran",
        "g_badfile": "Ce fichier n'est pas un identifiant Google « Application de bureau ».",
        "g_open": "Ouvrir la console Google", "g_pick": "Choisir client_secret.json",
        "g_saved": "Fichier enregistré, tu peux te connecter.",
        "g_steps": "1. Ouvre la console Google Cloud.\n2. Crée des identifiants « ID client OAuth » de type "
                   "Application de bureau.\n3. Télécharge le fichier JSON puis choisis-le ici.",
        "g_title": "Connexion Google", "google": "Se connecter avec Google",
        "google_done": "Connexion réussie ! Tu peux fermer cet onglet et retourner au jeu.",
        "google_err": "La connexion Google a échoué.", "google_hint": "Un clic, puis tu choisis ton compte Google.",
        "google_installing": "Installation du module Google…",
        "google_nomodule": "Module Google manquant : installe google-auth-oauthlib.",
        "google_offline": "Pas de connexion internet.", "google_timeout": "Délai dépassé, réessaie.",
        "google_wait": "Connexion en cours… termine dans ton navigateur.", "language": "Langue",
        "launching": "Lancement : {}", "load_save": "Charger une sauvegarde",
        "local_account": "Utiliser un compte local", "logged_as": "Connecté : {}", "login": "Connexion",
        "logout": "Se déconnecter", "multi": "Multijoueur", "net_off": "Hors ligne", "net_on": "En ligne",
        "new_multi": "Nouvelle partie", "new_solo": "Nouvelle partie", "no": "Non",
        "no_saves": "Aucune sauvegarde", "or": "ou", "password": "Mot de passe", "play": "Jouer",
        "profile_last": "Dernière sauvegarde", "profile_none": "Aucune", "profile_playtime": "Temps de jeu",
        "profile_saves": "Sauvegardes", "quit": "Quitter", "repeat": "Répéter le mot de passe",
        "resolution": "Résolution", "role_dev": "Développeur", "role_lead": "Directeur du projet et développeur",
        "saves_title": "Sauvegardes", "settings_title": "Paramètres", "setup_deps": "Installation de {}…",
        "setup_files": "Copie des fichiers du jeu…", "setup_folder": "Création du dossier du jeu…",
        "setup_ready": "Prêt !", "solo": "Solo",
        "thanks": "Un grand merci à toutes celles et ceux qui ont rendu ce jeu possible.",
        "username": "Identifiant", "volume": "Volume", "yes": "Oui",
    },
    "en": {
        "_name": "English",
        "account": "Account", "auth_title": "Account", "back": "Back", "close": "Close", "confirm": "Confirm",
        "confirm_delete": "Delete the save \"{}\"?", "create": "Create account", "credits": "Credits",
        "credits_title": "Credits", "delete": "Delete", "err_creds": "Wrong username or password.",
        "err_exists": "This username already exists.", "err_fill": "Please fill in every field.",
        "err_mismatch": "The passwords do not match.", "err_short": "Password too short (6 characters minimum).",
        "fullscreen": "Fullscreen", "g_badfile": "This file is not a Google \"Desktop app\" client.",
        "g_open": "Open the Google console", "g_pick": "Choose client_secret.json",
        "g_saved": "File saved, you can sign in now.",
        "g_steps": "1. Open the Google Cloud console.\n2. Create an \"OAuth client ID\" of type Desktop app.\n"
                   "3. Download the JSON file and choose it here.",
        "g_title": "Google sign-in", "google": "Sign in with Google",
        "google_done": "Signed in! You can close this tab and go back to the game.",
        "google_err": "Google sign-in failed.", "google_hint": "One click, then pick your Google account.",
        "google_installing": "Installing the Google module…",
        "google_nomodule": "Google module missing: install google-auth-oauthlib.",
        "google_offline": "No internet connection.", "google_timeout": "Timed out, please try again.",
        "google_wait": "Signing in… finish in your browser.", "language": "Language",
        "launching": "Launching: {}", "load_save": "Load a save", "local_account": "Use a local account",
        "logged_as": "Signed in: {}", "login": "Sign in", "logout": "Sign out", "multi": "Multiplayer",
        "net_off": "Offline", "net_on": "Online", "new_multi": "New game", "new_solo": "New game", "no": "No",
        "no_saves": "No saves yet", "or": "or", "password": "Password", "play": "Play",
        "profile_last": "Last save", "profile_none": "None", "profile_playtime": "Play time",
        "profile_saves": "Saves", "quit": "Quit", "repeat": "Repeat the password", "resolution": "Resolution",
        "role_dev": "Developer", "role_lead": "Project director and developer", "saves_title": "Saves",
        "settings_title": "Settings", "setup_deps": "Installing {}…", "setup_files": "Copying game files…",
        "setup_folder": "Creating the game folder…", "setup_ready": "Ready!", "solo": "Solo",
        "thanks": "A huge thank you to everyone who made this game possible.", "username": "Username",
        "volume": "Volume", "yes": "Yes",
    },
    "ja": {
        "_name": "日本語",
        "account": "アカウント", "auth_title": "アカウント", "back": "戻る", "close": "閉じる", "confirm": "決定",
        "confirm_delete": "セーブデータ「{}」を削除しますか？", "create": "アカウント作成",
        "credits": "クレジット", "credits_title": "クレジット", "delete": "削除",
        "err_creds": "IDまたはパスワードが違います。", "err_exists": "このIDはすでに使われています。",
        "err_fill": "すべての項目を入力してください。", "err_mismatch": "パスワードが一致しません。",
        "err_short": "パスワードは6文字以上にしてください。", "fullscreen": "フルスクリーン",
        "g_badfile": "このファイルは「デスクトップアプリ」用のGoogle認証情報ではありません。",
        "g_open": "Googleコンソールを開く", "g_pick": "client_secret.json を選ぶ",
        "g_saved": "ファイルを保存しました。ログインできます。",
        "g_steps": "1. Google Cloud コンソールを開く。\n2. 「OAuth クライアント ID」を「デスクトップ アプリ」で作成する。\n"
                   "3. JSONファイルをダウンロードして、ここで選ぶ。",
        "g_title": "Googleログイン", "google": "Googleでログイン",
        "google_done": "ログインしました！このタブを閉じてゲームに戻ってください。",
        "google_err": "Googleログインに失敗しました。", "google_hint": "ワンクリックでGoogleアカウントを選べます。",
        "google_installing": "Googleモジュールをインストール中…",
        "google_nomodule": "Googleモジュールがありません。google-auth-oauthlib をインストールしてください。",
        "google_offline": "インターネットに接続されていません。", "google_timeout": "時間切れです。もう一度お試しください。",
        "google_wait": "ログイン中… ブラウザで操作を完了してください。", "language": "言語",
        "launching": "起動中：{}", "load_save": "セーブデータを読み込む", "local_account": "ローカルアカウントを使う",
        "logged_as": "ログイン中：{}", "login": "ログイン", "logout": "ログアウト", "multi": "マルチプレイ",
        "net_off": "オフライン", "net_on": "オンライン", "new_multi": "ニューゲーム", "new_solo": "ニューゲーム",
        "no": "いいえ", "no_saves": "セーブデータなし", "or": "または", "password": "パスワード", "play": "プレイ",
        "profile_last": "最後のセーブ", "profile_none": "なし", "profile_playtime": "プレイ時間",
        "profile_saves": "セーブ数", "quit": "終了", "repeat": "パスワード（確認）", "resolution": "解像度",
        "role_dev": "開発者", "role_lead": "プロジェクトディレクター／開発者", "saves_title": "セーブデータ",
        "settings_title": "設定", "setup_deps": "{} をインストール中…", "setup_files": "ゲームファイルをコピー中…",
        "setup_folder": "ゲームフォルダを作成中…", "setup_ready": "準備完了！", "solo": "ソロ",
        "thanks": "このゲームを支えてくださったすべての方々に心から感謝します。", "username": "ユーザーID",
        "volume": "音量", "yes": "はい",
    },
    "es": {
        "_name": "Español",
        "account": "Cuenta", "auth_title": "Cuenta", "back": "Volver", "close": "Cerrar", "confirm": "Confirmar",
        "confirm_delete": "¿Eliminar la partida «{}»?", "create": "Crear cuenta", "credits": "Agradecimientos",
        "credits_title": "Agradecimientos", "delete": "Eliminar", "err_creds": "Usuario o contraseña incorrectos.",
        "err_exists": "Este usuario ya existe.", "err_fill": "Rellena todos los campos.",
        "err_mismatch": "Las contraseñas no coinciden.", "err_short": "Contraseña demasiado corta (mínimo 6 caracteres).",
        "fullscreen": "Pantalla completa", "g_badfile": "Este archivo no es una credencial de Google «Aplicación de escritorio».",
        "g_open": "Abrir la consola de Google", "g_pick": "Elegir client_secret.json",
        "g_saved": "Archivo guardado, ya puedes iniciar sesión.",
        "g_steps": "1. Abre la consola de Google Cloud.\n2. Crea un «ID de cliente OAuth» de tipo Aplicación de "
                   "escritorio.\n3. Descarga el archivo JSON y elígelo aquí.",
        "g_title": "Inicio de sesión con Google", "google": "Iniciar sesión con Google",
        "google_done": "¡Sesión iniciada! Puedes cerrar esta pestaña y volver al juego.",
        "google_err": "Error al iniciar sesión con Google.", "google_hint": "Un clic y eliges tu cuenta de Google.",
        "google_installing": "Instalando el módulo de Google…",
        "google_nomodule": "Falta el módulo de Google: instala google-auth-oauthlib.",
        "google_offline": "Sin conexión a internet.", "google_timeout": "Tiempo agotado, inténtalo de nuevo.",
        "google_wait": "Conectando… termina en tu navegador.", "language": "Idioma",
        "launching": "Iniciando: {}", "load_save": "Cargar una partida", "local_account": "Usar una cuenta local",
        "logged_as": "Sesión: {}", "login": "Iniciar sesión", "logout": "Cerrar sesión", "multi": "Multijugador",
        "net_off": "Sin conexión", "net_on": "En línea", "new_multi": "Nueva partida", "new_solo": "Nueva partida",
        "no": "No", "no_saves": "Ninguna partida guardada", "or": "o", "password": "Contraseña", "play": "Jugar",
        "profile_last": "Última partida", "profile_none": "Ninguna", "profile_playtime": "Tiempo de juego",
        "profile_saves": "Partidas", "quit": "Salir", "repeat": "Repetir la contraseña", "resolution": "Resolución",
        "role_dev": "Desarrollador", "role_lead": "Director del proyecto y desarrollador",
        "saves_title": "Partidas guardadas", "settings_title": "Ajustes", "setup_deps": "Instalando {}…",
        "setup_files": "Copiando los archivos del juego…", "setup_folder": "Creando la carpeta del juego…",
        "setup_ready": "¡Listo!", "solo": "Solo",
        "thanks": "Muchas gracias a todas las personas que han hecho posible este juego.",
        "username": "Usuario", "volume": "Volumen", "yes": "Sí",
    },
}


# --------------------------------------------------------------------------- #
#  Textes ajoutes dans cette version (completent locales/*.json sans les modifier)
#  Une langue ajoutee par toi dans locales/ utilise l'anglais pour ces textes tant que tu ne les traduis pas.
# --------------------------------------------------------------------------- #
EXTRA_TR = {
    "fr": {
        "gl_on": "Effet glitch : OUI", "gl_off": "Effet glitch : NON",
        "crt_on": "Effet CRT : OUI", "crt_off": "Effet CRT : NON",
        "controls": "Contrôles", "controls_title": "Contrôles",
        "c_action": "Action", "c_keyboard": "Clavier", "c_gamepad": "Manette",
        "c_reset": "Valeurs par défaut",
        "c_press_key": "Appuie sur une touche…", "c_press_btn": "Appuie sur un bouton…",
        "c_hint": "Clique sur une case, puis appuie sur la touche ou le bouton voulu. "
                  "Échap = annuler · Suppr = vider · clic droit / molette acceptés.",
        "c_pad_none": "Aucune manette détectée", "c_pad_ok": "Manette détectée : {}",
        "act_up": "Avancer", "act_down": "Reculer", "act_left": "Aller à gauche", "act_right": "Aller à droite",
        "act_sprint": "Courir", "act_jump": "Sauter / Esquiver", "act_interact": "Interagir",
        "act_attack": "Attaquer", "act_aim": "Viser / Bloquer", "act_reload": "Recharger",
        "act_inventory": "Inventaire", "act_pause": "Pause",
    },
    "en": {
        "gl_on": "Glitch effect: ON", "gl_off": "Glitch effect: OFF",
        "crt_on": "CRT effect: ON", "crt_off": "CRT effect: OFF",
        "controls": "Controls", "controls_title": "Controls",
        "c_action": "Action", "c_keyboard": "Keyboard", "c_gamepad": "Gamepad",
        "c_reset": "Reset to default",
        "c_press_key": "Press a key…", "c_press_btn": "Press a button…",
        "c_hint": "Click a box, then press the key or button you want. "
                  "Esc = cancel · Del = clear · right click / wheel click accepted.",
        "c_pad_none": "No gamepad detected", "c_pad_ok": "Gamepad detected: {}",
        "act_up": "Move forward", "act_down": "Move back", "act_left": "Move left", "act_right": "Move right",
        "act_sprint": "Sprint", "act_jump": "Jump / Dodge", "act_interact": "Interact",
        "act_attack": "Attack", "act_aim": "Aim / Block", "act_reload": "Reload",
        "act_inventory": "Inventory", "act_pause": "Pause",
    },
    "ja": {
        "gl_on": "グリッチ効果：オン", "gl_off": "グリッチ効果：オフ",
        "crt_on": "CRT効果：オン", "crt_off": "CRT効果：オフ",
        "controls": "操作設定", "controls_title": "操作設定",
        "c_action": "アクション", "c_keyboard": "キーボード", "c_gamepad": "コントローラー",
        "c_reset": "初期設定に戻す",
        "c_press_key": "キーを押してください…", "c_press_btn": "ボタンを押してください…",
        "c_hint": "枠をクリックして、割り当てたいキーまたはボタンを押します。"
                  "Esc＝キャンセル ・ Del＝解除 ・ 右クリック/ホイールも可。",
        "c_pad_none": "コントローラーが見つかりません", "c_pad_ok": "コントローラー検出：{}",
        "act_up": "前進", "act_down": "後退", "act_left": "左へ移動", "act_right": "右へ移動",
        "act_sprint": "ダッシュ", "act_jump": "ジャンプ／回避", "act_interact": "調べる",
        "act_attack": "攻撃", "act_aim": "構える／防御", "act_reload": "リロード",
        "act_inventory": "インベントリ", "act_pause": "ポーズ",
    },
    "es": {
        "gl_on": "Efecto glitch: SÍ", "gl_off": "Efecto glitch: NO",
        "crt_on": "Efecto CRT: SÍ", "crt_off": "Efecto CRT: NO",
        "controls": "Controles", "controls_title": "Controles",
        "c_action": "Acción", "c_keyboard": "Teclado", "c_gamepad": "Mando",
        "c_reset": "Restablecer",
        "c_press_key": "Pulsa una tecla…", "c_press_btn": "Pulsa un botón…",
        "c_hint": "Haz clic en una casilla y pulsa la tecla o el botón que quieras. "
                  "Esc = cancelar · Supr = vaciar · clic derecho / rueda aceptados.",
        "c_pad_none": "No se detecta ningún mando", "c_pad_ok": "Mando detectado: {}",
        "act_up": "Avanzar", "act_down": "Retroceder", "act_left": "Ir a la izquierda", "act_right": "Ir a la derecha",
        "act_sprint": "Correr", "act_jump": "Saltar / Esquivar", "act_interact": "Interactuar",
        "act_attack": "Atacar", "act_aim": "Apuntar / Bloquear", "act_reload": "Recargar",
        "act_inventory": "Inventario", "act_pause": "Pausa",
    },
}

# --------------------------------------------------------------------------- #
#  Controles par defaut (clavier = touches physiques glfw, manette = noms Xbox)
# --------------------------------------------------------------------------- #
ACTIONS = ("up", "down", "left", "right", "sprint", "jump", "interact", "attack", "aim", "reload",
           "inventory", "pause")
DEFAULT_CONTROLS = {
    "keyboard": {"up": "W", "down": "S", "left": "A", "right": "D", "sprint": "LEFT_SHIFT", "jump": "SPACE",
                 "interact": "E", "attack": "MOUSE1", "aim": "MOUSE2", "reload": "R", "inventory": "TAB",
                 "pause": "ESCAPE"},
    "gamepad": {"up": "LS_UP", "down": "LS_DOWN", "left": "LS_LEFT", "right": "LS_RIGHT", "sprint": "L3",
                "jump": "A", "interact": "X", "attack": "RT", "aim": "LT", "reload": "B", "inventory": "Y",
                "pause": "START"},
}
KEY_NAMES = {getattr(glfw, n): n[4:] for n in dir(glfw)
             if n.startswith("KEY_") and n not in ("KEY_UNKNOWN", "KEY_LAST", "KEY_MENU")}
KEY_CODES = {v: k for k, v in KEY_NAMES.items()}
PAD_BUTTONS = {glfw.GAMEPAD_BUTTON_A: "A", glfw.GAMEPAD_BUTTON_B: "B", glfw.GAMEPAD_BUTTON_X: "X",
               glfw.GAMEPAD_BUTTON_Y: "Y", glfw.GAMEPAD_BUTTON_LEFT_BUMPER: "LB",
               glfw.GAMEPAD_BUTTON_RIGHT_BUMPER: "RB", glfw.GAMEPAD_BUTTON_BACK: "BACK",
               glfw.GAMEPAD_BUTTON_START: "START", glfw.GAMEPAD_BUTTON_LEFT_THUMB: "L3",
               glfw.GAMEPAD_BUTTON_RIGHT_THUMB: "R3", glfw.GAMEPAD_BUTTON_DPAD_UP: "DPAD_UP",
               glfw.GAMEPAD_BUTTON_DPAD_RIGHT: "DPAD_RIGHT", glfw.GAMEPAD_BUTTON_DPAD_DOWN: "DPAD_DOWN",
               glfw.GAMEPAD_BUTTON_DPAD_LEFT: "DPAD_LEFT"}
# libelles courts affiches dans les cases (le reste : le nom de la touche tel quel)
_LABELS_FR = {"SPACE": "ESPACE", "ENTER": "ENTRÉE", "TAB": "TAB", "ESCAPE": "ÉCHAP", "BACKSPACE": "RETOUR",
              "LEFT_SHIFT": "MAJ GAUCHE", "RIGHT_SHIFT": "MAJ DROITE", "LEFT_CONTROL": "CTRL GAUCHE",
              "RIGHT_CONTROL": "CTRL DROITE", "LEFT_ALT": "ALT", "RIGHT_ALT": "ALT GR", "UP": "HAUT",
              "DOWN": "BAS", "LEFT": "GAUCHE", "RIGHT": "DROITE", "MOUSE1": "CLIC GAUCHE",
              "MOUSE2": "CLIC DROIT", "MOUSE3": "MOLETTE", "DELETE": "SUPPR", "INSERT": "INSER",
              "PAGE_UP": "PAGE HAUT", "PAGE_DOWN": "PAGE BAS", "CAPS_LOCK": "VERR MAJ",
              "DPAD_UP": "CROIX HAUT", "DPAD_DOWN": "CROIX BAS", "DPAD_LEFT": "CROIX GAUCHE",
              "DPAD_RIGHT": "CROIX DROITE", "LS_UP": "STICK G HAUT", "LS_DOWN": "STICK G BAS",
              "LS_LEFT": "STICK G GAUCHE", "LS_RIGHT": "STICK G DROITE", "RS_UP": "STICK D HAUT",
              "RS_DOWN": "STICK D BAS", "RS_LEFT": "STICK D GAUCHE", "RS_RIGHT": "STICK D DROITE"}
_LABELS_EN = {"SPACE": "SPACE", "ESCAPE": "ESC", "LEFT_SHIFT": "L-SHIFT", "RIGHT_SHIFT": "R-SHIFT",
              "LEFT_CONTROL": "L-CTRL", "RIGHT_CONTROL": "R-CTRL", "LEFT_ALT": "L-ALT", "RIGHT_ALT": "R-ALT",
              "MOUSE1": "LEFT CLICK", "MOUSE2": "RIGHT CLICK", "MOUSE3": "MIDDLE CLICK", "PAGE_UP": "PAGE UP",
              "PAGE_DOWN": "PAGE DOWN", "CAPS_LOCK": "CAPS LOCK", "DPAD_UP": "D-PAD UP",
              "DPAD_DOWN": "D-PAD DOWN", "DPAD_LEFT": "D-PAD LEFT", "DPAD_RIGHT": "D-PAD RIGHT",
              "LS_UP": "L-STICK UP", "LS_DOWN": "L-STICK DOWN", "LS_LEFT": "L-STICK LEFT",
              "LS_RIGHT": "L-STICK RIGHT", "RS_UP": "R-STICK UP", "RS_DOWN": "R-STICK DOWN",
              "RS_LEFT": "R-STICK LEFT", "RS_RIGHT": "R-STICK RIGHT"}


def bind_label(token, lang="fr"):
    """Texte affiche dans une case de controle ('' -> tiret)."""
    if not token:
        return "—"
    table = _LABELS_FR if lang == "fr" else _LABELS_EN
    if token in table:
        return table[token]
    if token.startswith("KP_"):
        return token.replace("KP_", "NUM ").replace("_", " ")
    code = KEY_CODES.get(token)
    if code is not None:
        try:       # nom de la touche selon TON clavier (AZERTY : la touche W physique s'appelle Z)
            name = glfw.get_key_name(code, 0)
            if name:
                return name.upper()
        except Exception:
            pass
    return token.replace("_", " ")


def get_controls(settings):
    """Controles de settings.json completes par les valeurs par defaut."""
    out = {dev: dict(DEFAULT_CONTROLS[dev]) for dev in DEFAULT_CONTROLS}
    saved = settings.get("controls")
    if isinstance(saved, dict):
        for dev in out:
            if isinstance(saved.get(dev), dict):
                for act in ACTIONS:
                    if act in saved[dev] and isinstance(saved[dev][act], str):
                        out[dev][act] = saved[dev][act]
    return out


# --------------------------------------------------------------------------- #
#  Polices systeme (Pillow lit les .ttf directement : plus besoin de Tk)
# --------------------------------------------------------------------------- #
def _font_dirs():
    dirs = []

    if os.name == "nt":
        dirs += [
            os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Microsoft", "Windows", "Fonts"
            ),
        ]
    elif sys.platform == "darwin":
        dirs += [
            "/System/Library/Fonts",
            "/System/Library/Fonts/Supplemental",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts"),
        ]
    else:
        dirs += [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"),
        ]

    # Polices embarquées dans le projet.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for folder in (
        script_dir,
        os.path.dirname(script_dir),
        os.path.dirname(os.path.dirname(script_dir)),
        os.path.dirname(os.path.dirname(os.path.dirname(script_dir))),
    ):
        dirs.append(os.path.join(folder, "assets", "fonts"))

    # Supprime les doublons et garde uniquement les dossiers existants.
    result = []
    seen = set()

    for folder in dirs:
        folder = os.path.abspath(folder)
        if os.path.isdir(folder) and folder not in seen:
            seen.add(folder)
            result.append(folder)

    return result


_FONT_INDEX = {}


def find_system_font(*names):
    """Chemin de la premiere police trouvee parmi 'names' (noms de fichiers), sinon None."""
    if not _FONT_INDEX:
        for base in _font_dirs():
            for root, _dirs, files in os.walk(base):
                for f in files:
                    _FONT_INDEX.setdefault(f.lower(), os.path.join(root, f))
    for n in names:
        p = _FONT_INDEX.get(n.lower())
        if p:
            return p
    return None


def load_locales():
    """Charge locales/*.json (DATA_DIR d'abord, puis le dossier de l'exe). Ajouter une langue = ajouter un fichier.
    Les traductions integrees (BASE_TR + EXTRA_TR) servent de base : un fichier .json n'a qu'a remplacer ce qu'il veut."""
    tr, names = {}, {}
    for base in (DATA_DIR, RES_DIR):
        folder = os.path.join(base, "locales")
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            code = f[:-5]
            if f.lower().endswith(".json") and code not in tr:
                data = load_json(os.path.join(folder, f), None)
                if isinstance(data, dict):
                    tr[code] = data
                    names[code] = str(data.get("_name", code))
    for code in BASE_TR:                  # langues integrees : toujours disponibles
        tr.setdefault(code, {})
        names.setdefault(code, BASE_TR[code]["_name"])
    for code, data in tr.items():         # complete les cles absentes (anglais pour une langue ajoutee par toi)
        for src in (BASE_TR.get(code) or BASE_TR["en"], EXTRA_TR.get(code) or EXTRA_TR["en"]):
            for k, v in src.items():
                if k != "_name":
                    data.setdefault(k, v)
    first = [c for c in ("fr", "ja", "en", "es") if c in tr]
    order = first + sorted(c for c in tr if c not in first)
    return {c: names[c] for c in order}, tr


LANGS, TR = load_locales()


def translate(lang, key):
    base = TR.get("en") or TR.get("fr") or {}
    return TR.get(lang, base).get(key) or base.get(key, key)


def hsv_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def hex_rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def mix(c1, c2, t):
    a, b = hex_rgb(c1), hex_rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), 200_000).hex()
    return salt, h


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def ease_out_expo(t):
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def ease_out_bounce(t):
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


# Palette 60-30-10 : 60 % noir profond (fonds), 30 % anthracite (cartes / panneaux), 10 % accent ambre radio
# (reserve aux elements interactifs et aux etats actifs). Pour du vert phosphore : mets ACCENT = "#00ff66".
COL_BG = "#0c0c0e"
COL_PANEL = "#1e1f24"
ACCENT = "#ff5500"


def extract_palette(img=None):
    return {
        "bg": COL_BG,
        "accent": ACCENT,
        "accent_dim": mix(COL_PANEL, ACCENT, 0.52),
        "panel": COL_PANEL,
        "panel_alt": "#2a2b31",
        "text": "#e8e8ec",
        "muted": "#8d8e98",
        "err": "#ff5a4d",
        "ok": "#7bd88f",
    }


def make_gear(size, color):
    """Dessine une icone d'engrenage (anti-aliasee)."""
    S = size * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    teeth = 8
    r_out, r_in, r_hole = S * 0.48, S * 0.36, S * 0.16
    step = 2 * math.pi / teeth
    pts = []
    for i in range(teeth):
        a0 = step * i
        for ang, r in ((a0 - step * 0.22, r_in), (a0 - step * 0.14, r_out),
                       (a0 + step * 0.14, r_out), (a0 + step * 0.22, r_in)):
            pts.append((c + r * math.cos(ang), c + r * math.sin(ang)))
    d.polygon(pts, fill=color)
    d.ellipse([c - S * 0.40, c - S * 0.40, c + S * 0.40, c + S * 0.40], fill=color)
    d.ellipse([c - r_hole, c - r_hole, c + r_hole, c + r_hole], fill=(0, 0, 0, 0))
    return im.resize((size, size), Image.LANCZOS)


def _title_font(path, px):
    for p in (path, "arialbd.ttf"):
        try:
            return ImageFont.truetype(p, px)
        except Exception:
            pass
    return ImageFont.load_default(px)


def _rand_layer(w, h, scale, rnd):
    sw, sh = max(2, w // scale + 1), max(2, h // scale + 1)
    img = Image.frombytes("L", (sw, sh), bytes(rnd.getrandbits(8) for _ in range(sw * sh)))
    return img.resize((w, h), Image.BICUBIC)


def render_title_parts(text, font_path, px, glow, seed=7):
    """Titre delabre : lettres irregulieres, degrade os -> rouille, eclats sur les bords, rayures,
    contour sombre. Renvoie (halo, coeur), memes dimensions, rognes avec des marges symetriques
    => le titre est parfaitement centre quand on le pose sur son centre."""
    font = _title_font(font_path, px)
    rnd = random.Random(seed)
    pad = int(px * 0.9)
    adv = [font.getlength(ch) for ch in text]
    W, H = int(sum(adv)) + 2 * pad + px, int(px * 1.7) + 2 * pad
    mask = Image.new("L", (W, H), 0)
    x = pad
    for ch, a in zip(text, adv):
        if ch != " ":
            cw, chh = int(a) + px, int(px * 1.7)
            cell = Image.new("L", (cw, chh), 0)
            ImageDraw.Draw(cell).text((px // 2, int(px * 0.15)), ch, font=font, fill=255)
            cell = cell.rotate(rnd.uniform(-3.0, 3.0), resample=Image.BICUBIC, center=(cw // 2, chh // 2))
            mask.paste(255, (int(x) - px // 2, pad + rnd.randint(-int(px * 0.04), int(px * 0.04))), cell)
        x += a
    # usure : eclats surtout sur les bords + gros eclats isoles
    n1 = _rand_layer(W, H, max(3, px // 5), rnd)
    n2 = _rand_layer(W, H, max(2, px // 14), rnd)
    wear = Image.blend(n1, n2, 0.45)
    inner = mask.filter(ImageFilter.MinFilter(max(5, (px // 8) | 1)))
    edge = ImageChops.subtract(mask, inner).filter(ImageFilter.MaxFilter(5)).point(lambda v: 255 if v > 127 else 0)
    chips = ImageChops.lighter(ImageChops.multiply(wear.point(lambda v: 255 if v > 178 else 0), edge),
                               wear.point(lambda v: 255 if v > 219 else 0))
    worn = ImageChops.multiply(mask, ImageChops.invert(chips.point(lambda v: int(v * 0.95))))
    # remplissage : os clair -> orange -> rouille sombre, taches
    grad = Image.linear_gradient("L").resize((W, H))
    fill = ImageOps.colorize(grad, black=(242, 228, 192), white=(150, 48, 14), mid=(232, 122, 36), midpoint=120)
    stain = n1.point(lambda v: 170 + int(v * 0.33))
    fill = ImageChops.multiply(fill, Image.merge("RGB", (stain, stain, stain))).convert("RGBA")
    scratch = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scratch)
    for _ in range(int(W / 9)):
        x0, y0 = rnd.randint(0, W), rnd.randint(pad, H - pad)
        sd.line([(x0, y0), (x0 + rnd.randint(int(px * 0.25), int(px * 0.9)), y0 + rnd.randint(-5, 5))],
                fill=255, width=1)
    fill.paste((255, 240, 210, 255), (0, 0), ImageChops.multiply(scratch, worn).point(lambda v: int(v * 0.55)))
    # contour sombre + ombre
    outline = mask.filter(ImageFilter.MaxFilter(max(5, (px // 10) | 1)))
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dark = Image.new("RGBA", (W, H), (14, 8, 5, 255))
    dark.putalpha(outline)
    core = Image.alpha_composite(core, dark)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shadow.putalpha(mask.point(lambda v: int(v * 0.8)))
    core = Image.alpha_composite(core, ImageChops.offset(shadow, 2, 3))
    fill.putalpha(worn)
    core = Image.alpha_composite(core, fill)
    # halo lumineux (separe pour pouvoir le faire pulser)
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for radius, k in ((px * 0.30, 0.9), (px * 0.10, 0.9)):
        layer = Image.new("RGBA", (W, H), tuple(glow) + (255,))
        layer.putalpha(outline.filter(ImageFilter.GaussianBlur(radius)).point(lambda v, k=k: min(255, int(v * k))))
        halo = Image.alpha_composite(halo, layer)
    l, t, r, b = outline.point(lambda v: 255 if v > 40 else 0).getbbox()
    m = int(px * 0.45)
    box = (max(0, l - m), max(0, t - m), min(W, r + m), min(H, b + m))
    return halo.crop(box), core.crop(box)



SFX_HOOK = None


def sfx(name):
    if SFX_HOOK:
        try:
            SFX_HOOK(name)
        except Exception:
            pass



# --------------------------------------------------------------------------- #
#  Rendu vispy : tout ce qui est affiche est un "sprite" = une texture dessinee par le GPU
#  (le texte et les boutons sont rasterises avec Pillow, puis envoyes en texture)
# --------------------------------------------------------------------------- #
VERT = """
uniform vec4 u_rect;     // x, y, largeur, hauteur en pixels (origine en haut a gauche)
uniform vec2 u_view;     // taille de la fenetre
uniform vec4 u_uv;       // u0, v0, u1, v1
attribute vec2 a_pos;
varying vec2 v_uv;
void main() {
    vec2 p = u_rect.xy + a_pos * u_rect.zw;
    gl_Position = vec4(p.x / u_view.x * 2.0 - 1.0, 1.0 - p.y / u_view.y * 2.0, 0.0, 1.0);
    v_uv = mix(u_uv.xy, u_uv.zw, a_pos);
}
"""
FRAG = """
uniform sampler2D u_tex;
uniform vec3 u_tint;
uniform float u_alpha;
varying vec2 v_uv;
void main() {
    vec4 c = texture2D(u_tex, v_uv);                  // alpha pre-multiplie
    gl_FragColor = vec4(c.rgb * u_tint * u_alpha, c.a * u_alpha);
}
"""


POST_VERT = """
attribute vec2 a_pos;
varying vec2 v_uv;
void main() { v_uv = a_pos; gl_Position = vec4(a_pos * 2.0 - 1.0, 0.0, 1.0); }
"""
POST_FRAG = """
uniform sampler2D u_tex;
uniform vec2 u_res;
uniform float u_time;
uniform float u_glitch;      // 0..1 : rafale de glitch
uniform float u_crt;         // 1 = scanlines / bruit / vignette
uniform float u_gl;          // 1 = glitch autorise
varying vec2 v_uv;
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void main() {
    vec2 uv = v_uv;
    float tick = floor(u_time * 14.0);
    // glitch : bandes horizontales decalees + separation RVB (surtout en haut, la ou est le titre)
    float band = floor(uv.y * 46.0);
    float g = step(0.90, hash(vec2(band, tick))) * u_glitch * u_gl;
    uv.x += g * (hash(vec2(band, tick + 9.0)) - 0.5) * 0.07;
    float ca = 0.0007 * u_crt + g * 0.006;
    vec3 col;
    col.r = texture2D(u_tex, uv + vec2(ca, 0.0)).r;
    col.g = texture2D(u_tex, uv).g;
    col.b = texture2D(u_tex, uv - vec2(ca, 0.0)).b;
    // scanlines CRT
    float sl = 0.5 + 0.5 * sin(uv.y * u_res.y * 3.14159);
    col *= 1.0 - 0.13 * sl * u_crt;
    // bruit cathodique
    float n = hash(uv * u_res + vec2(u_time * 37.0, u_time * 11.0));
    col += (n - 0.5) * 0.045 * u_crt;
    // bande de balayage lente
    float sweep = smoothstep(0.0, 0.06, 1.0 - abs(fract(uv.y - u_time * 0.045) - 0.5) * 2.0 - 0.94);
    col += sweep * 0.025 * u_crt;
    // vignette + legere pulsation de tension
    vec2 d = uv - 0.5;
    col *= 1.0 - dot(d, d) * 0.55 * u_crt;
    col *= 1.0 + 0.012 * sin(u_time * 95.0) * u_crt;
    gl_FragColor = vec4(col, 1.0);
}
"""


class PostFX:
    """Rend toute la scene dans une texture, puis l'affiche avec l'effet CRT (scanlines, bruit, glitch, vignette)."""

    def __init__(self):
        self.prog = gloo.Program(POST_VERT, POST_FRAG)
        self.prog["a_pos"] = gloo.VertexBuffer(np.array([[0, 0], [1, 0], [0, 1], [1, 1]], np.float32))
        self.size = None
        self.tex = self.fbo = None

    def _ensure(self, w, h):
        if self.size == (w, h):
            return
        self.tex = gloo.Texture2D(np.zeros((h, w, 4), np.uint8), interpolation="linear", wrapping="clamp_to_edge")
        self.fbo = gloo.FrameBuffer(self.tex, gloo.RenderBuffer((h, w)))
        self.size = (w, h)

    def begin(self, w, h):
        self._ensure(w, h)
        self.fbo.activate()
        gloo.set_viewport(0, 0, w, h)

    def end(self, w, h, t, glitch, crt, gl):
        self.fbo.deactivate()
        gloo.set_viewport(0, 0, w, h)
        gloo.clear((0.0, 0.0, 0.0, 1.0))
        gloo.set_state(blend=False)
        p = self.prog
        p["u_tex"] = self.tex
        p["u_res"] = (float(w), float(h))
        p["u_time"] = float(t % 1000.0)
        p["u_glitch"] = float(glitch)
        p["u_crt"] = float(crt)
        p["u_gl"] = float(gl)
        p.draw("triangle_strip")
        gloo.set_state(blend=True, blend_func=("one", "one_minus_src_alpha"))


def hex_tint(c):
    return tuple(v / 255 for v in hex_rgb(c))


def _premult(img):
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    a = arr[..., 3:4].astype(np.uint16)
    arr[..., :3] = ((arr[..., :3].astype(np.uint16) * a + 127) // 255).astype(np.uint8)
    return np.ascontiguousarray(arr)


class Sprite:
    """Une image affichee a l'ecran. anchor : c (centre), nw (coin haut-gauche), w (milieu gauche)."""

    def __init__(self, img=None, x=0, y=0, w=None, h=None, z=0, anchor="c", alpha=1.0, tint=(1.0, 1.0, 1.0),
                 tag=None, uv=(0.0, 0.0, 1.0, 1.0)):
        self.tex, self.tw, self.th = None, 0, 0
        self.x, self.y, self.w, self.h = x, y, w, h
        self.z, self.anchor, self.alpha, self.tint, self.tag, self.uv = z, anchor, alpha, tint, tag, uv
        self.visible = True
        self.dx = 0.0
        if img is not None:
            self.set_image(img)

    def set_image(self, img):
        arr = _premult(img)
        h, w = arr.shape[:2]
        if self.tex is not None and (w, h) == (self.tw, self.th):
            self.tex.set_data(arr)
        else:
            self.free()
            self.tex = gloo.Texture2D(arr, interpolation="linear", wrapping="clamp_to_edge")
            self.tw, self.th = w, h

    def free(self):
        if self.tex is not None:
            try:
                self.tex.delete()
            except Exception:
                pass
            self.tex = None


class Renderer:
    """Dessine les sprites : un quad texture par sprite, melange alpha pre-multiplie."""

    def __init__(self):
        self.prog = gloo.Program(VERT, FRAG)
        self.prog["a_pos"] = gloo.VertexBuffer(np.array([[0, 0], [1, 0], [0, 1], [1, 1]], np.float32))
        gloo.set_state(blend=True, blend_func=("one", "one_minus_src_alpha"), depth_test=False,
                       cull_face=False)

    def draw(self, sp, vw, vh):
        if not sp.visible or sp.tex is None or sp.alpha <= 0.002:
            return
        w = sp.w if sp.w is not None else sp.tw
        h = sp.h if sp.h is not None else sp.th
        x, y = sp.x + sp.dx, sp.y
        if sp.anchor == "c":
            x, y = x - w / 2, y - h / 2
        elif sp.anchor == "w":
            y -= h / 2
        elif sp.anchor == "n":
            x -= w / 2
        p = self.prog
        p["u_rect"] = (round(x), round(y), w, h)
        p["u_view"] = (vw, vh)
        p["u_uv"] = sp.uv
        p["u_tint"] = tuple(sp.tint)
        p["u_alpha"] = float(sp.alpha)
        p["u_tex"] = sp.tex
        p.draw("triangle_strip")


# --------------------------------------------------------------------------- #
#  Habillage : polices, texte (avec polices de secours), boutons plats
# --------------------------------------------------------------------------- #
class Skin:
    """Polices et dessin du texte / des boutons (equivalent des polices et du FlatButton de Tk)."""

    def __init__(self, app):
        self.app = app
        self._fonts, self._glyph, self._notdef = {}, {}, {}

        # Polices du jeu : on cherche aussi dans les sous-dossiers de fonts/.
        font_dir = find_asset("fonts")
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        font_dirs = [
            font_dir,
            os.path.join(project_dir, "assets", "fonts"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),
            os.path.join(DATA_DIR, "fonts"),
            os.path.join(RES_DIR, "fonts"),
        ]

        def local_font(*names):
            for folder in font_dirs:
                if not os.path.isdir(folder):
                    continue
                for root, dirs, files in os.walk(folder):
                    dirs.sort()
                    for name in names:
                        for filename in files:
                            if filename.lower() == name.lower():
                                return os.path.join(root, filename)
            return None

        # Le titre utilise Saira si elle existe, sinon Rajdhani Bold.
        self.stencil = (
            local_font("SairaStencilOne-Regular.ttf", "Rajdhani-Bold.ttf")
            or find_system_font(
                "impact.ttf",
                "DejaVuSans-Bold.ttf",
                "NotoSans-Bold.ttf",
            )
        )

        # Rajdhani reste utilisable même si sa variante Medium est absente.
        raj_r = local_font("Rajdhani-Medium.ttf", "Rajdhani-Regular.ttf")
        raj_b = local_font("Rajdhani-Bold.ttf")
        self.raj = bool(raj_r or raj_b)
        self.body_reg = (
            raj_r or raj_b
            or find_system_font(
                "bahnschrift.ttf",
                "segoeui.ttf",
                "DejaVuSans.ttf",
                "NotoSans-Regular.ttf",
            )
        )
        self.body_bold = (
            None if self.raj
            else find_system_font("bahnschrift.ttf")
        )
        self.body_bold_file = (
            raj_b or find_system_font(
                "segoeuib.ttf",
                "arialbd.ttf",
                "DejaVuSans-Bold.ttf",
                "NotoSans-Bold.ttf",
            )
        )

        jp_local = find_asset("fonts", "NotoSansJP-Regular.ttf")
        if os.path.isfile(jp_local):
            try:
                ImageFont.truetype(jp_local, 16)
                self.jp = jp_local
            except Exception as exc:
                log(f"Erreur chargement police japonaise : {exc}")
                self.jp = find_system_font(
                "NotoSansCJK-Regular.ttc",
                "NotoSansCJKjp-Regular.otf",
                "NotoSansJP-Regular.otf",
            )
        else:
            self.jp = find_system_font(
            "NotoSansCJK-Regular.ttc",
            "NotoSansCJKjp-Regular.otf",
            "NotoSansJP-Regular.otf",
            )

        self.jp_bold = self.jp

        self.fallback = find_system_font(
            "seguisym.ttf",
            "DejaVuSans.ttf",
            "arial.ttf",
            "NotoSans-Regular.ttf",
        )
    # ----- polices --------------------------------------------------------- #
    def _load(self, path, px, var=None):
        key = (path, px, var)
        f = self._fonts.get(key)
        if f is None:
            try:
                f = ImageFont.truetype(path, px)
                if var:
                    try:
                        f.set_variation_by_name(var)
                    except Exception:
                        pass
            except Exception:
                f = ImageFont.load_default(px)
            self._fonts[key] = f
        return f

    def chain(self, spec, scale=1.0):
        """Liste de polices [principale, secours...] pour une 'spec' ('t', taille) ou ('b', taille, gras)."""
        px = max(6, int(round(spec[1] * 4 / 3 * scale * (1.14 if spec[0] == "b" and self.raj else 1.0))))
        ja = self.app.lang == "ja"
        if spec[0] == "t":                              # police "titre" : pochoir (police japonaise pour ja)
            cands = [(self.jp_bold, None), (self.body_reg, None)] if ja else \
                    [(self.stencil, None), (self.body_reg, None), (self.jp, None)]
        elif spec[2]:
            cands = [(self.jp_bold, None)] if ja else [(self.body_bold, "Bold"), (self.body_bold_file, None)]
            cands += [(self.body_reg, None), (self.jp, None)]
        else:
            cands = [(self.jp, None)] if ja else [(self.body_reg, None)]
            cands += [(self.body_reg, None), (self.jp, None)]
        cands.append((self.fallback, None))
        out, seen = [], set()
        for path, var in cands:
            if path and (path, var) not in seen:
                seen.add((path, var))
                out.append(self._load(path, px, var))
        return out or [ImageFont.load_default(px)]

    @staticmethod
    def _mask(font, ch):
        im = Image.new("L", (int(font.size * 2) + 8, int(font.size * 2) + 8), 0)
        ImageDraw.Draw(im).text((4, 4), ch, font=font, fill=255)
        return im.tobytes()

    def _has(self, font, ch):
        if ord(ch) < 128 or ch.isspace():
            return True
        k = (id(font), ch)
        ok = self._glyph.get(k)
        if ok is None:
            nd = self._notdef.get(id(font))
            if nd is None:
                nd = self._notdef[id(font)] = self._mask(font, "\uffff")
            ok = self._glyph[k] = self._mask(font, ch) != nd
        return ok

    def runs(self, text, chain):
        out = []
        for ch in text:
            f = next((f for f in chain if self._has(f, ch)), chain[0])
            if out and out[-1][1] is f:
                out[-1][0] += ch
            else:
                out.append([ch, f])
        return out

    def lh(self, spec, scale=1.0):
        a, d = self.chain(spec, scale)[0].getmetrics()
        return a + d

    def zero(self, spec, scale=1.0):
        return self.chain(spec, scale)[0].getlength("0")

    def width(self, text, spec, scale=1.0):
        ch = self.chain(spec, scale)
        return sum(f.getlength(s) for s, f in self.runs(text, ch))

    def draw_text(self, d, x, y, text, spec, scale, fill, align="l"):
        """Texte dont le haut de ligne est en y ; align : l / c (x = centre) / r (x = bord droit)."""
        ch = self.chain(spec, scale)
        runs = self.runs(text, ch)
        total = sum(f.getlength(s) for s, f in runs)
        cx = x - total / 2 if align == "c" else (x - total if align == "r" else x)
        base = y + ch[0].getmetrics()[0]
        for s, f in runs:
            d.text((cx, base), s, font=f, fill=fill, anchor="ls")
            cx += f.getlength(s)
        return total

    def wrap(self, text, spec, scale, maxw):
        """Coupe le texte en lignes de largeur <= maxw (None = pas de coupe)."""
        lines = []
        for para in str(text).split("\n"):
            if not maxw or self.width(para, spec, scale) <= maxw:
                lines.append(para)
                continue
            cur = ""
            tokens = para.split(" ") if " " in para else list(para)
            sep = " " if " " in para else ""
            for tok in tokens:
                trial = (cur + sep + tok) if cur else tok
                if cur and self.width(trial, spec, scale) > maxw:
                    lines.append(cur)
                    cur = tok
                else:
                    cur = trial
                while self.width(cur, spec, scale) > maxw and len(cur) > 1:      # mot trop long
                    k = len(cur) - 1
                    while k > 1 and self.width(cur[:k], spec, scale) > maxw:
                        k -= 1
                    lines.append(cur[:k])
                    cur = cur[k:]
            lines.append(cur)
        return lines

    # ----- boutons plats (bordure accent, survol, enfoncement de 2 px) ----------- #
    def btn_size(self, text, spec, wchars, scale=1.0, pady=11, image=None):
        if image is not None:
            return int(image.width + (20 + 4) * scale), int(image.height + (16 + 4) * scale)
        w = int(wchars * self.zero(spec, scale)) + int(6 * scale)
        if text:                                          # jamais de mot coupe : le bouton s'adapte au texte
            w = max(w, int(math.ceil(self.width(text.upper(), spec, scale))) + int(2 * 28 * scale))
        h = self.lh(spec, scale) + 2 * int(round(pady * scale)) + int(4 * scale)
        return w, h

    def button_image(self, text, spec, wchars, pal, state="n", scale=1.0, pady=11, image=None, hover_image=None,
                     k=None):
        """k (0..1) : niveau de survol pour le fondu ; sinon deduit de l'etat n / h / p."""
        w, h = self.btn_size(text, spec, wchars, scale, pady, image)
        b = max(1, int(round(2 * scale)))
        hot = state in ("h", "p")
        kk = k if k is not None else (1.0 if hot else 0.0)
        im = Image.new("RGBA", (w, h), pal["accent"])
        d = ImageDraw.Draw(im)
        dy = b if state == "p" else 0                        # le bouton "s'enfonce" de 2 px au clic
        d.rectangle([b, b + dy, w - b - 1, h - b - 1], fill=mix(pal["panel"], pal["accent"], kk))
        if image is not None:
            pic = hover_image if (hot and hover_image is not None) else image
            im.alpha_composite(pic.convert("RGBA"), ((w - pic.width) // 2, (h - pic.height) // 2 + dy))
        else:
            lh = self.lh(spec, scale)
            self.draw_text(d, w / 2, (h - lh) / 2 + dy, (text or "").upper(), spec, scale,
                           mix(pal["text"], pal["panel"], kk), "c")
        return im


class Btn:
    """Bouton pose directement sur la scene (menu principal, engrenage) : fondu au survol, decalage de 8 px
    vers la droite, barre d'accent a gauche et cadre de focus clavier / manette."""

    SHIFT = 8

    def __init__(self, app, text=None, command=None, spec=None, width=BTN_W, image=None, hover_image=None,
                 pady=11, z=10, tag="menu", slide=True):
        sk = app.skin
        self.app, self.command, self.state, self.slide = app, command, "n", slide
        self.imgs = {st: sk.button_image(text, spec, width, app.pal, st, 1.0, pady, image, hover_image)
                     for st in ("n", "h", "p")}
        self.sprite = Sprite(self.imgs["n"], z=z, tag=tag)
        self.hot = Sprite(self.imgs["h"], z=z + 1, tag=tag, alpha=0.0)
        w, h = self.size()
        self.bar = Sprite(app.white, z=z + 2, tag=tag, w=5, h=h, anchor="w", tint=hex_tint(app.pal["accent"]),
                          alpha=0.0)
        self.frame = Sprite(self._frame_image(w, h), z=z + 3, tag=tag, alpha=0.0)
        self.t, self.focus, self.gx, self.glitch_until = 0.0, False, 0.0, 0.0

    def _frame_image(self, w, h):
        pad, pal = 7, self.app.pal
        im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        col = hex_rgb(pal["accent"]) + (255,)
        d.rectangle([0, 0, w + 2 * pad - 1, h + 2 * pad - 1], outline=col, width=2)
        for cx in (0, w + 2 * pad - 1):               # petites equerres aux angles
            for cy in (0, h + 2 * pad - 1):
                d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=hex_rgb(pal["bg"]) + (255,), outline=col)
        return im

    def sprites(self):
        return [self.sprite, self.hot, self.bar, self.frame]

    def set_state(self, st):
        if st != self.state:
            self.state = st
            self.hot.set_image(self.imgs["p" if st == "p" else "h"])

    def set_focus(self, on, visible=True):
        self.focus = bool(on)
        self.frame.alpha = 1.0 if (on and visible) else 0.0

    def update(self, dt):
        """Appele a chaque image : interpole le survol et recale les sprites d'habillage sur le principal."""
        target = 1.0 if (self.state in ("h", "p") or self.focus) else 0.0
        k = min(1.0, dt * 16.0)
        self.t += (target - self.t) * k
        if abs(self.t - target) < 0.004:
            self.t = target
        sp, e = self.sprite, ease_out_cubic(self.t)
        dx = (self.SHIFT * e if self.slide else 0.0) + self.gx
        sp.dx = self.hot.dx = self.frame.dx = dx
        self.hot.x, self.hot.y, self.frame.x, self.frame.y = sp.x, sp.y, sp.x, sp.y
        self.hot.alpha = sp.alpha * self.t
        w, h = self.size()
        self.bar.visible = self.slide
        self.bar.x, self.bar.y = sp.x - w / 2, sp.y
        self.bar.h = max(1, int(h * e))
        self.bar.alpha = sp.alpha * min(1.0, self.t * 1.5)
        if self.frame.alpha > 0:
            self.frame.visible = sp.alpha > 0.01

    def size(self):
        return self.sprite.tw, self.sprite.th

    def contains(self, x, y):
        w, h = self.size()
        return abs(x - self.sprite.x) <= w / 2 and abs(y - self.sprite.y) <= h / 2


# --------------------------------------------------------------------------- #
#  Panneaux (popups) : elements empiles verticalement, dessines avec Pillow
# --------------------------------------------------------------------------- #
class PanelState:
    """Etat interactif d'un panneau (survol, focus, texte des champs, selection...)."""

    def __init__(self):
        self.hover = self.down = self.focus = self.drag = self.capture = None
        self.text, self.caret, self.sel, self.scroll, self.val = {}, {}, {}, {}, {}
        self.t0 = time.time()
        self.last_click = (0.0, None)
        self.kfocus, self.kvis, self.hv = None, False, {}


class PanelUI:
    """Construit un panneau avec des methodes proches de pack() de Tk : title(), label(), button()...
    scale < 1 reduit tout (polices comprises) : c'est ce qui evite les menus coupes sur petites fenetres."""

    PADX, PADY = 38, 28

    def __init__(self, app, scale=1.0):
        self.app, self.sk, self.pal, self.s = app, app.skin, app.pal, scale
        self.els = []
        self.W = self.H = self.inner = 0

    def S(self, v):
        return max(1, int(round(v * self.s))) if v else 0

    def P(self, pad):
        return (self.S(pad[0]), self.S(pad[1]))

    def _add(self, kind, nw, nh, pad=(0, 0), fill=False, id=None, **kw):
        e = dict(kind=kind, nw=nw, nh=nh, pad=self.P(pad), fill=fill, id=id or f"e{len(self.els)}", **kw)
        self.els.append(e)
        return e

    # ----- elements ------------------------------------------------------- #
    def title(self, text, size=20, gap=16):
        spec = self.app.font(size)
        self._add("label", self.sk.width(text.upper(), spec, self.s), self.sk.lh(spec, self.s), text=text.upper(),
                  spec=spec, color="accent", align="c", lines=[text.upper()])
        self._add("rule", 0, self.S(2), pad=(8, gap), fill=True)

    def label(self, text, spec=None, color="text", wrap=None, align="c", pad=(0, 0), minlines=0, id=None):
        spec = spec or self.app.body(11)
        lines = self.sk.wrap(text, spec, self.s, self.S(wrap) if wrap else None) if text else []
        lh = self.sk.lh(spec, self.s)
        nw = max([self.sk.width(l, spec, self.s) for l in lines] or [0])
        return self._add("label", nw, max(len(lines), minlines) * lh, pad=pad, fill=(align == "w"), id=id,
                         text=text, spec=spec, color=color, align=align, lines=lines)

    def button(self, text, command, spec, width=BTN_W, pal=None, pad=(0, 8), pady=11, id=None):
        pal = pal or self.pal
        w, h = self.sk.btn_size(text, spec, width, self.s, pady)
        return self._add("button", w, h, pad=pad, id=id, text=text, spec=spec, width=width, bpal=pal, pady=pady,
                         command=command)

    def combo(self, values, current, on_select, width=24, size=13, pad=(0, 18), id=None):
        spec = self.app.body(size)
        w = int(width * self.sk.zero(spec, self.s)) + self.S(46)
        w = max([w] + [int(self.sk.width(v, spec, self.s)) + self.S(60) for v in values])
        return self._add("combo", w, self.sk.lh(spec, self.s) + self.S(22), pad=pad, fill=True, id=id,
                         spec=spec, values=values, current=current, on_select=on_select)

    def slider(self, value, on_change, on_release, length=320, pad=(0, 18), id="slider"):
        spec = self.app.body(11)
        return self._add("slider", self.S(length), self.sk.lh(spec, self.s) + self.S(34), pad=pad, fill=True, id=id,
                         spec=spec, value=value, on_change=on_change, on_release=on_release)

    def entry(self, id, secret=False, on_submit=None, width=34, pad=(0, 0)):
        spec = self.app.body(13)
        w = int(width * self.sk.zero(spec, self.s)) + self.S(12)
        return self._add("entry", w, self.sk.lh(spec, self.s) + self.S(24), pad=pad, fill=True, id=id, spec=spec,
                         secret=secret, on_submit=on_submit)

    def listbox(self, id, items, on_activate, rows=8, width=40, pad=(0, 16)):
        spec = self.app.body(13)
        rowh = self.sk.lh(spec, self.s) + self.S(5)
        w = int(width * self.sk.zero(spec, self.s)) + self.S(8)
        w = max([w] + [int(self.sk.width(it, spec, self.s)) + self.S(34) for it in items])   # nom entier visible
        return self._add("list", w, rows * rowh + self.S(4), pad=pad, id=id, spec=spec, items=items, rows=rows,
                         rowh=rowh, on_activate=on_activate)

    def infobox(self, rows, pad=(0, 16)):
        lab, val = self.app.body(11), self.app.body(11, True)
        layout, h, nw = [], self.S(24), 0
        for a, b in rows:
            lines = self.sk.wrap(b, val, self.s, self.S(250))
            rh = max(self.sk.lh(lab, self.s), len(lines) * self.sk.lh(val, self.s)) + self.S(6)
            layout.append((a, lines, rh))
            h += rh
            nw = max(nw, self.sk.width(a, lab, self.s) + max(self.sk.width(l, val, self.s) for l in lines)
                     + self.S(18))
        return self._add("infobox", nw + self.S(32), h, pad=pad, fill=True, rows=layout, lab=lab, val=val)

    def avatar(self, img, pad=(0, 8)):
        size = self.S(88)
        return self._add("avatar", size, size, pad=pad, img=img.resize((size, size), Image.LANCZOS))

    def tabs(self, labels, active, on_pick, pad=(2, 8)):
        spec = self.app.body(12, True)
        widths = [self.sk.width(t, spec, self.s) + 2 * self.S(16) for _, t in labels]
        gap = self.S(4)
        return self._add("tabs", int(sum(widths) + gap * (len(labels) - 1)), self.sk.lh(spec, self.s) + 2 * self.S(7),
                         pad=pad, spec=spec, labels=labels, widths=widths, gap=gap, active=active, on_pick=on_pick)

    def link(self, text, on_click, pad=(0, 8), id="link"):
        spec = self.app.body(11)
        return self._add("link", self.sk.width(text, spec, self.s), self.sk.lh(spec, self.s) + 2 * self.S(6), pad=pad,
                         id=id, text=text, spec=spec, on_click=on_click)

    def sep_or(self, text, pad=(4, 4)):
        spec = self.app.body(11)
        return self._add("sep", 0, self.sk.lh(spec, self.s) + self.S(4), pad=pad, fill=True, text=text, spec=spec)

    def spacer(self, h):
        self._add("spacer", 0, self.S(h))

    def bindtable(self, rows, visible, on_cell, id="binds"):
        """Tableau des controles : rows = [(texte action, jeton clavier, jeton manette)]."""
        spec, head = self.app.body(12), self.app.body(11, True)
        rowh = self.sk.lh(spec, self.s) + self.S(14)
        cw = int(16 * self.sk.zero(spec, self.s)) + self.S(12)
        toks = [bind_label(tok, self.app.lang) for r in rows for tok in (r[1], r[2])]
        cw = max(cw, min(int(max(self.sk.width(t, spec, self.s) for t in toks)) + self.S(18),
                         int(24 * self.sk.zero(spec, self.s))))              # touches longues : case elargie
        aw = max(self.sk.width(r[0], spec, self.s) for r in rows) + self.S(18)
        hh = self.sk.lh(head, self.s) + self.S(10)
        return self._add("binds", aw + 2 * cw + 2 * self.S(8) + self.S(12), hh + visible * rowh, id=id,
                         rows=rows, visible=visible, rowh=rowh, cw=cw, aw=aw, hh=hh, spec=spec, head=head,
                         on_cell=on_cell)

    # ----- mise en page --------------------------------------------------- #
    def finish(self):
        for e in self.els:
            e["nw"], e["nh"] = int(math.ceil(e["nw"])), int(math.ceil(e["nh"]))
        self.inner = max([e["nw"] for e in self.els] or [100])
        y = 2 + self.S(self.PADY)
        for e in self.els:
            y += e["pad"][0]
            e["y"], e["h"] = y, e["nh"]
            y += e["nh"] + e["pad"][1]
            e["w"] = self.inner if e["fill"] else e["nw"]
            e["x"] = 2 + self.S(self.PADX) + (self.inner - e["w"]) // 2
        self.H = y + self.S(self.PADY) + 2
        self.W = self.inner + 2 * self.S(self.PADX) + 4

    def find(self, id):
        return next((e for e in self.els if e["id"] == id), None)

    # ----- clic / survol -------------------------------------------------- #
    def hit(self, lx, ly):
        """(element, sous-element) sous le point, ou None."""
        for e in self.els:
            if e["kind"] in ("rule", "spacer", "avatar", "infobox") or e["kind"] == "label":
                continue
            if e["x"] <= lx < e["x"] + e["w"] and e["y"] <= ly < e["y"] + e["h"]:
                return e, self.sub(e, lx - e["x"], ly - e["y"])
        return None

    def sub(self, e, rx, ry):
        k = e["kind"]
        if k == "tabs":
            x = 0
            for i, w in enumerate(e["widths"]):
                if x <= rx < x + w:
                    return i
                x += w + e["gap"]
            return None
        if k == "list":
            i = e["ps_scroll"] + (ry - self.S(2)) // e["rowh"] if "ps_scroll" in e else 0
            return int(i) if 0 <= i < len(e["items"]) else None
        if k == "binds":
            if ry < e["hh"]:
                return None
            row = int((ry - e["hh"]) // e["rowh"]) + e.get("ps_scroll", 0)
            gap = self.S(8)
            x0 = e["aw"] + gap
            col = 0 if x0 <= rx < x0 + e["cw"] else (1 if x0 + e["cw"] + gap <= rx < x0 + 2 * e["cw"] + gap else None)
            if col is None or not (0 <= row < len(e["rows"])):
                return None
            return (row, col)
        return 0

    # ----- dessin --------------------------------------------------------- #
    def color(self, name):
        return self.pal.get(name, name)

    def render(self, ps, now):
        p, sk = self.pal, self.sk
        im = Image.new("RGBA", (self.W, self.H), p["accent"])
        d = ImageDraw.Draw(im)
        d.rectangle([2, 2, self.W - 3, self.H - 3], fill=p["panel"])
        for e in self.els:
            getattr(self, "_draw_" + e["kind"])(im, d, e, ps, now)
        if ps.kvis and ps.kfocus:                                   # cadre de focus clavier / manette
            e = self.find(ps.kfocus)
            if e is not None:
                m = self.S(4)
                d.rectangle([e["x"] - m, e["y"] - m, e["x"] + e["w"] + m - 1, e["y"] + e["h"] + m - 1],
                            outline=p["accent"], width=max(1, self.S(2)))
        return im

    def _draw_label(self, im, d, e, ps, now):
        lh = self.sk.lh(e["spec"], self.s)
        for i, line in enumerate(e["lines"]):
            if e["align"] == "w":
                self.sk.draw_text(d, e["x"], e["y"] + i * lh, line, e["spec"], self.s, self.color(e["color"]), "l")
            else:
                self.sk.draw_text(d, e["x"] + e["w"] / 2, e["y"] + i * lh, line, e["spec"], self.s,
                                  self.color(e["color"]), "c")

    def _draw_rule(self, im, d, e, ps, now):
        d.rectangle([e["x"], e["y"], e["x"] + e["w"] - 1, e["y"] + e["h"] - 1], fill=self.pal["accent_dim"])

    def _draw_spacer(self, im, d, e, ps, now):
        pass

    def _draw_button(self, im, d, e, ps, now):
        hov = ps.hover and ps.hover[0] == e["id"]
        down = ps.down and ps.down[0] == e["id"] and hov
        st = "p" if down else ("h" if hov else "n")
        k = ps.hv.get(e["id"], 1.0 if hov else 0.0)
        im.alpha_composite(self.sk.button_image(e["text"], e["spec"], e["width"], e["bpal"], st, self.s, e["pady"],
                                                k=1.0 if down else k), (e["x"], e["y"]))

    def _draw_combo(self, im, d, e, ps, now):
        p, x, y, w, h = self.pal, e["x"], e["y"], e["w"], e["h"]
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=p["accent"])
        aw = self.S(30)
        d.rectangle([x + 1, y + 1, x + w - aw - 1, y + h - 2], fill=p["panel_alt"])
        self.sk.draw_text(d, x + self.S(10), y + (h - self.sk.lh(e["spec"], self.s)) / 2, e["current"], e["spec"],
                          self.s, p["text"], "l")
        cx, cy, k = x + w - aw / 2, y + h / 2, self.S(5)
        d.polygon([(cx - k, cy - k / 2), (cx + k, cy - k / 2), (cx, cy + k * 0.7)], fill=p["panel"])

    def _draw_slider(self, im, d, e, ps, now):
        p, x, y, w = self.pal, e["x"], e["y"], e["w"]
        val = ps.val.get(e["id"], e["value"])
        tw, th = self.S(26), self.S(24)
        lh = self.sk.lh(e["spec"], self.s)
        ty = y + lh + self.S(6)
        d.rectangle([x, ty + self.S(4), x + w - 1, ty + self.S(4) + self.S(14)], fill=p["panel_alt"])
        cx = x + tw / 2 + (w - tw) * val / 100
        active = (ps.hover and ps.hover[0] == e["id"]) or ps.drag == e["id"]
        d.rectangle([cx - tw / 2, ty, cx + tw / 2, ty + th], fill=p["accent"] if active else mix(p["panel_alt"], p["accent"], 0.7))
        self.sk.draw_text(d, cx, y, str(int(val)), e["spec"], self.s, p["text"], "c")

    def _draw_entry(self, im, d, e, ps, now):
        p, x, y, w, h = self.pal, e["x"], e["y"], e["w"], e["h"]
        focus = ps.focus == e["id"]
        idle = mix(p["panel_alt"], p["accent_dim"], 0.45)
        b = self.S(2)
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=p["accent"] if focus else idle)
        bg = mix(p["panel_alt"], p["accent"], 0.10) if focus else p["panel_alt"]
        d.rectangle([x + b, y + b, x + w - b - 1, y + h - b - 1], fill=bg)
        iw, ih = w - 2 * b - 2 * self.S(6), h - 2 * b
        raw = ps.text.get(e["id"], "")
        caret = min(ps.caret.get(e["id"], len(raw)), len(raw))
        shown = raw
        lh = self.sk.lh(e["spec"], self.s)
        layer = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        if e["secret"]:        # points dessines a la main (la police pochoir n'a pas toujours le glyphe)
            dot = lh * 0.30
            adv = dot * 2.3
            caret_x = (dot + (caret - 1) * adv + dot / 2 + 2) if caret else 1
            off = max(0, caret_x - (iw - 6))
            for i in range(len(raw)):
                cx = dot + i * adv - off
                ld.ellipse([cx - dot / 2, ih / 2 - dot / 2, cx + dot / 2, ih / 2 + dot / 2], fill=p["text"])
            caret_x -= off
        else:
            cx_caret = self.sk.width(shown[:caret], e["spec"], self.s)
            off = max(0, cx_caret - (iw - 6))
            self.sk.draw_text(ld, -off, (ih - lh) / 2, shown, e["spec"], self.s, p["text"], "l")
            caret_x = cx_caret - off
        if focus and int((now - ps.t0) / 0.53) % 2 == 0:
            ld.rectangle([caret_x, (ih - lh) / 2, caret_x + max(1, self.S(1.5)), (ih + lh) / 2], fill=p["accent"])
        im.alpha_composite(layer, (x + b + self.S(6), y + b))

    def _draw_list(self, im, d, e, ps, now):
        p, x, y, w, h = self.pal, e["x"], e["y"], e["w"], e["h"]
        focus = ps.focus == e["id"]
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=p["accent"] if focus else p["accent_dim"])
        b = self.S(2)
        d.rectangle([x + b, y + b, x + w - b - 1, y + h - b - 1], fill=p["panel_alt"])
        sel = ps.sel.get(e["id"], 0)
        sc = ps.scroll.get(e["id"], 0)
        e["ps_scroll"] = sc
        for i in range(e["rows"]):
            k = sc + i
            if k >= len(e["items"]):
                break
            ry = y + b + i * e["rowh"]
            if k == sel:
                d.rectangle([x + b, ry, x + w - b - 1, ry + e["rowh"] - 1], fill=p["accent"])
            self.sk.draw_text(d, x + b + self.S(4), ry + self.S(2), e["items"][k], e["spec"], self.s,
                              p["panel"] if k == sel else p["text"], "l")
        if len(e["items"]) > e["rows"]:      # petite barre de defilement
            tot = e["rows"] * e["rowh"]
            bar = max(self.S(18), tot * e["rows"] / len(e["items"]))
            top = y + b + (tot - bar) * sc / max(1, len(e["items"]) - e["rows"])
            d.rectangle([x + w - b - self.S(5), top, x + w - b - 1, top + bar], fill=p["accent_dim"])

    def _draw_infobox(self, im, d, e, ps, now):
        p, x, y, w = self.pal, e["x"], e["y"], e["w"]
        d.rectangle([x, y, x + w - 1, y + e["h"] - 1], fill=p["panel_alt"])
        cy = y + self.S(12)
        for lab, lines, rh in e["rows"]:
            self.sk.draw_text(d, x + self.S(16), cy + self.S(3), lab, e["lab"], self.s, p["muted"], "l")
            lh = self.sk.lh(e["val"], self.s)
            for i, line in enumerate(lines):
                self.sk.draw_text(d, x + w - self.S(16), cy + self.S(3) + i * lh, line, e["val"], self.s,
                                  p["text"], "r")
            cy += rh

    def _draw_avatar(self, im, d, e, ps, now):
        im.alpha_composite(e["img"].convert("RGBA"), (e["x"], e["y"]))

    def _draw_tabs(self, im, d, e, ps, now):
        p, x = self.pal, e["x"]
        lh = self.sk.lh(e["spec"], self.s)
        for i, ((_, text), w) in enumerate(zip(e["labels"], e["widths"])):
            on = e["labels"][i][0] == e["active"]
            d.rectangle([x, e["y"], x + w - 1, e["y"] + e["h"] - 1], fill=p["accent"] if on else p["panel_alt"])
            self.sk.draw_text(d, x + w / 2, e["y"] + (e["h"] - lh) / 2, text, e["spec"], self.s,
                              p["panel"] if on else p["text"], "c")
            x += w + e["gap"]

    def _draw_link(self, im, d, e, ps, now):
        hov = ps.hover and ps.hover[0] == e["id"]
        self.sk.draw_text(d, e["x"], e["y"] + self.S(6), e["text"], e["spec"], self.s,
                          self.pal["accent"] if hov else self.pal["muted"], "l")

    def _draw_sep(self, im, d, e, ps, now):
        p = self.pal
        tw = self.sk.width(e["text"], e["spec"], self.s)
        cy = e["y"] + e["h"] // 2
        gap = self.S(10)
        mid = e["x"] + e["w"] / 2
        d.rectangle([e["x"], cy, mid - tw / 2 - gap, cy], fill=p["accent_dim"])
        d.rectangle([mid + tw / 2 + gap, cy, e["x"] + e["w"] - 1, cy], fill=p["accent_dim"])
        self.sk.draw_text(d, mid, e["y"] + self.S(2), e["text"], e["spec"], self.s, p["muted"], "c")

    def _draw_binds(self, im, d, e, ps, now):
        p, t = self.pal, self.app.t
        x, y, gap = e["x"], e["y"], self.S(8)
        x0 = x + e["aw"] + gap
        self.sk.draw_text(d, x + self.S(4), y + self.S(4), t("c_action").upper(), e["head"], self.s, p["muted"], "l")
        for c, key in enumerate(("c_keyboard", "c_gamepad")):
            self.sk.draw_text(d, x0 + c * (e["cw"] + gap) + e["cw"] / 2, y + self.S(4), t(key).upper(), e["head"],
                              self.s, p["accent"], "c")
        sc = ps.scroll.get(e["id"], 0)
        e["ps_scroll"] = sc
        lh = self.sk.lh(e["spec"], self.s)
        cap = ps.capture
        for i in range(e["visible"]):
            k = sc + i
            if k >= len(e["rows"]):
                break
            name, kb, pad = e["rows"][k]
            ry = y + e["hh"] + i * e["rowh"]
            self.sk.draw_text(d, x + self.S(4), ry + (e["rowh"] - lh) / 2, name, e["spec"], self.s, p["text"], "l")
            for c, tok in enumerate((kb, pad)):
                cx0 = x0 + c * (e["cw"] + gap)
                waiting = cap is not None and cap["row"] == k and cap["col"] == c
                hov = ps.hover and ps.hover[0] == e["id"] and ps.hover[1] == (k, c)
                fillc = p["accent"] if waiting else (p["accent_dim"] if hov else p["panel_alt"])
                d.rectangle([cx0, ry + self.S(2), cx0 + e["cw"] - 1, ry + e["rowh"] - self.S(3)], fill=p["accent"] if waiting or hov else p["accent_dim"])
                d.rectangle([cx0 + 1, ry + self.S(3), cx0 + e["cw"] - 2, ry + e["rowh"] - self.S(4)],
                            fill=p["accent"] if waiting else (mix(p["panel_alt"], p["accent_dim"], 0.5) if hov else p["panel_alt"]))
                if waiting:
                    txt, col = t("c_press_key" if c == 0 else "c_press_btn"), p["panel"]
                else:
                    txt, col = bind_label(tok, self.app.lang), (p["text"] if tok else p["muted"])
                spec = e["spec"]
                while self.sk.width(txt, spec, self.s) > e["cw"] - self.S(8) and spec[1] > 7:
                    spec = (spec[0], spec[1] - 1) + tuple(spec[2:])
                self.sk.draw_text(d, cx0 + e["cw"] / 2, ry + (e["rowh"] - self.sk.lh(spec, self.s)) / 2, txt, spec,
                                  self.s, col, "c")
        if len(e["rows"]) > e["visible"]:        # barre de defilement
            tot = e["visible"] * e["rowh"]
            bar = max(self.S(18), tot * e["visible"] / len(e["rows"]))
            top = y + e["hh"] + (tot - bar) * sc / max(1, len(e["rows"]) - e["visible"])
            d.rectangle([x + e["w"] - self.S(4), top, x + e["w"] - 1, top + bar], fill=p["accent_dim"])


# --------------------------------------------------------------------------- #
#  Application
# --------------------------------------------------------------------------- #
class App:
    def __init__(self):
        self.settings = load_json(SETTINGS_FILE, {})
        self.lang = self.settings.get("lang", "fr")
        if self.lang not in LANGS:
            self.lang = "fr"
        self.user = self.settings.get("google_user") or None   # reconnexion Google automatique
        self.pending_auth = None
        self.jobs = queue.Queue()

        self.panel = self.panel_builder = self.ps = self.panel_ui = None
        self.panel_closable = True
        self.panel_mode = "center"
        self.menu_name = "main"
        self.menu_buttons = []
        self.auth_mode = "login"
        self.auth_msg = None
        self.g_msg = None

        self.bg_mode = "full"
        self.banner_landed = False
        self.banner_h = 0
        self.fullscreen = False
        self._win_geo = None
        self._resize_job = None
        self._save_job = None
        self.google_busy = False
        self.show_local = False
        # effets CRT / glitch + navigation clavier-manette + musique etouffee
        self.crt, self.gl_on = bool(self.settings.get("crt", False)), bool(self.settings.get("glitch", False))
        self.post, self.post_ok, self._poll_sz = None, True, 0.0
        self.glitch, self._glitch_next, self._glitch_end, self._flick_end = 0.0, time.time() + 6.0, 0.0, 0.0
        self.title_core = None
        self._t_start = self._t_last = time.time()
        self.nav_btn, self.nav_vis = None, False
        self.muffle, self.muffle_target, self.muffle_chan, self.muffle_snd = 0.0, 0.0, None, None
        self._muffle_dirty, self._muffle_id = False, None

        self.pygame = None
        self.music_stop = False
        self.music_gen = 0
        self.music_skip = False
        self.sfx = {}
        self.net_ok = None
        self.led_pos = None
        self.pending_delete = None
        self._closing = False
        self.running = True
        globals()["SFX_HOOK"] = self.play_sfx
        self.winsound_track = None
        self.winsound_playing = False

        # scene : liste de sprites triee par z a chaque image ; petit planificateur facon Tk.after
        self.sprites = []
        self.anims = []
        self._timers = []
        self._after_id = 0
        self.r = None
        self._after_draw = None
        self.mx = self.my = 0
        self.hover_btn = self.down_btn = None
        self.dd = None
        self.pad_name, self.pad_down, self._pad_t = None, set(), 0.0
        self.splash = None
        self.gear = None
        self.panel_dirty = False
        self.cursor_hand = self.cursor_ibeam = None

        # ----- fenetre vispy (backend glfw) ---------------------------------- #
        self.vapp = vapp.use_app("glfw")
        self.W, self.H = 1280, 720
        sw, sh = 1920, 1080
        win = self.settings.get("window")
        if isinstance(win, list) and len(win) == 2 and all(isinstance(v, int) for v in win):
            self.W, self.H = max(win[0], 1000), max(win[1], 700)
        self.canvas = vapp.Canvas(title=APP_NAME, size=(self.W, self.H), show=False, resizable=True,
                                  vsync=True, app=self.vapp)
        self.win = getattr(self.canvas._backend, "_id", None)
        if self.win is None:
            raise RuntimeError("Fenetre glfw introuvable : mets a jour vispy et glfw (pip install -U vispy glfw)")
        try:
            mon = glfw.get_primary_monitor()
            sw, sh = glfw.get_video_mode(mon).size
            self.W, self.H = min(self.W, sw), min(self.H, sh)
            glfw.set_window_size(self.win, self.W, self.H)
            px, py = max(0, (sw - self.W) // 2), max(0, (sh - self.H) // 2 - 20)
            saved = self.settings.get("window_pos")
            if isinstance(saved, list) and len(saved) == 2 and all(isinstance(v, int) for v in saved) \
                    and self.pos_visible(saved[0], saved[1]):
                px, py = saved                                  # on rouvre exactement la ou le joueur l'avait laisse
            
        except Exception:
            pass
        self.screen = (sw, sh)
        try:
            glfw.set_window_size_limits(self.win, 1000, 700, glfw.DONT_CARE, glfw.DONT_CARE)
        except Exception:
            pass
        self.set_icon()
        glfw.set_key_callback(self.win, self._glfw_key)
        glfw.set_char_callback(self.win, self._glfw_char)
        glfw.set_mouse_button_callback(self.win, self._glfw_mouse)
        glfw.set_cursor_pos_callback(self.win, self._glfw_cursor)
        glfw.set_scroll_callback(self.win, self._glfw_scroll)
        glfw.set_window_close_callback(self.win, self._glfw_close)
        glfw.set_window_pos_callback(self.win, self._glfw_pos)
        try:
            self.cursor_hand = glfw.create_standard_cursor(glfw.HAND_CURSOR)
            self.cursor_ibeam = glfw.create_standard_cursor(glfw.IBEAM_CURSOR)
        except Exception:
            pass
        self.canvas.events.draw.connect(self.on_draw)
        self.canvas.events.resize.connect(self.on_resize)

        # ----- fond, palette, polices ---------------------------------------- #
        try:
            self.bg_path = find_background(self.settings)      # fond different a chaque lancement
            save_json(SETTINGS_FILE, self.settings)
            self.bg_src = Image.open(self.bg_path).convert("RGB")
        except Exception:
            self.bg_src = Image.new("RGB", (1280, 720), (26, 22, 20))
        self.pal = extract_palette(self.bg_src)
        self.skin = Skin(self)
        self.white = Image.new("RGBA", (2, 2), (255, 255, 255, 255))
        self.bg_sprite = self.add(Sprite(ImageOps.fit(self.bg_src, (self.W, self.H), Image.LANCZOS), 0, 0,
                                         anchor="nw", z=0, alpha=0.0))
        self.bg_menu = self.add(Sprite(self.menu_overlay(), 0, 0, self.W, self.H, anchor="nw", z=1, alpha=0.0))
        self.build_splash()

    # ----- aides ----------------------------------------------------------- #
    def t(self, key):
        return translate(self.lang, key)

    def font(self, size, bold=False):
        """Police 'titre' : pochoir apocalyptique (police japonaise pour le japonais)."""
        return ("t", size)

    def body(self, size, bold=False):
        """Police 'texte' lisible (champs, listes, messages)."""
        return ("b", size, bool(bold))

    def menu_x(self):
        return max(215, int(self.W * 0.2), int(getattr(self, "_menu_half", 0)) + 36)

    def add(self, sp):
        self.sprites.append(sp)
        return sp

    def remove(self, *sps):
        for sp in sps:
            if sp is not None and sp in self.sprites:
                self.sprites.remove(sp)
                sp.free()

    def remove_tag(self, tag):
        for sp in [s for s in self.sprites if s.tag == tag]:
            self.remove(sp)

    def after(self, ms, fn):
        self._after_id += 1
        self._timers.append((time.time() + ms / 1000.0, self._after_id, fn))
        return self._after_id

    def after_idle(self, fn):
        return self.after(0, fn)

    def after_cancel(self, i):
        self._timers = [t for t in self._timers if t[1] != i]

    def animate(self, dur, fn, done=None):
        """fn(t) est appele a chaque image avec t de 0 a 1."""
        self.anims.append([time.time(), dur, fn, done])

    def autosave(self, delay=200):
        """Enregistre settings.json tout de suite apres un changement (regroupe les rafales, ex. curseur de volume)."""
        if self._save_job:
            self.after_cancel(self._save_job)
        self._save_job = self.after(delay, self.save_settings)

    def save_settings(self):
        self.settings["lang"] = self.lang
        save_json(SETTINGS_FILE, self.settings)

    def set_icon(self):
        try:
            if os.name == "nt":
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
            png = find_asset("icon.png")
            if os.path.exists(png):
                ic = Image.open(png).convert("RGBA")
                glfw.set_window_icon(self.win, [ic.resize((s, s), Image.LANCZOS) for s in (256, 64, 32)])
        except Exception:
            pass

    # ----- boucle principale ----------------------------------------------- #
    def run(self):
        self.canvas.show()
        self.try_auto_login()
        try:
            while self.running:
                t0 = time.time()
                self.tick()
                self.canvas.update()
                self.vapp.process_events()
                if time.time() - t0 < 0.008:          # (au cas ou la synchro verticale est coupee)
                    time.sleep(0.008 - (time.time() - t0))
        finally:
            try:
                self.canvas.close()
            except Exception:
                pass

    def destroy(self):
        self.running = False

    def tick(self):
        now = time.time()
        try:
            while True:
                self.jobs.get_nowait()()
        except queue.Empty:
            pass
        due = sorted(t for t in self._timers if t[0] <= now)
        if due:
            self._timers = [t for t in self._timers if t[0] > now]
            for _, _, fn in due:
                fn()
        for a in list(self.anims):
            t = min((now - a[0]) / a[1], 1.0) if a[1] > 0 else 1.0
            a[2](t)
            if t >= 1.0:
                self.anims.remove(a)
                if a[3]:
                    a[3]()
        dt = max(0.0, min(0.1, now - self._t_last))
        self._t_last = now
        for b in list(self.menu_buttons) + ([self.gear] if self.gear is not None else []):
            b.update(dt)
        self.fx_update(now)
        self.muffle_update(dt)
        if now - self._poll_sz > 0.3:                  # filet de securite : la taille reelle a-t-elle change ?
            self._poll_sz = now
            try:
                w, h = glfw.get_window_size(self.win)
                if (w, h) != (self.W, self.H) and w >= 300 and h >= 300 and self._resize_job is None:
                    self._resize_job = self.after(100, lambda: self.relayout(w, h))
            except Exception:
                pass
        self.pulse(now)
        self.poll_gamepad(now)
        self.poll_splash()
        if self.ps is not None and self.panel_ui is not None:
            blink = int((now - self.ps.t0) / 0.53) % 2
            if self.ps.focus and blink != getattr(self, "_blink", None):
                self._blink = blink
                self.panel_dirty = True
            self.panel_hover_anim(dt)
            if getattr(self, "panel_dirty", False):
                self.panel_dirty = False
                self.panel.set_image(self.panel_ui.render(self.ps, now))

    def on_draw(self, ev):
        if self.r is None:
            self.r = Renderer()
        pw, ph = self.canvas.physical_size
        use = (self.crt or (self.gl_on and self.glitch > 0)) and self.post_ok
        if use and self.post is None:
            try:
                self.post = PostFX()
            except Exception as e:
                log(f"effet CRT indisponible : {e!r}")
                self.post_ok = use = False
        gloo.set_state(blend=True, blend_func=("one", "one_minus_src_alpha"), depth_test=False, cull_face=False)
        try:
            if use:
                self.post.begin(pw, ph)
            else:
                gloo.set_viewport(0, 0, pw, ph)
            gloo.clear(tuple(v / 255 for v in hex_rgb(COL_BG)) + (1.0,))
            for sp in sorted(self.sprites, key=lambda s: s.z):
                self.r.draw(sp, self.W, self.H)
            if use:
                self.post.end(pw, ph, time.time() - self._t_start, self.glitch, 1.0 if self.crt else 0.0,
                              1.0 if self.gl_on else 0.0)
        except Exception as e:
            log(f"rendu CRT : {e!r}")
            self.post_ok = False
            try:
                self.post.fbo.deactivate()
            except Exception:
                pass
        if self._after_draw:
            self._after_draw()

    def fx_update(self, now):
        """Rafales de glitch aleatoires (ecran, titre, boutons) + scintillement neon / radio du titre."""
        if not self.gl_on:
            self.glitch = 0.0
            glitchy = False
        else:
            if now >= self._glitch_next:
                self._glitch_end = now + random.uniform(0.12, 0.30)
                self._glitch_next = now + random.uniform(4.5, 10.0)
            self.glitch = 1.0 if now < self._glitch_end else 0.0
            if random.random() < 0.004:
                self._flick_end = now + 0.10
            glitchy = self.glitch or now < self._flick_end
        core, halo = self.title_core, getattr(self, "title_halo", None)
        if core is not None:
            core.alpha = random.choice((1.0, 0.5, 0.85, 0.3, 1.0)) if glitchy else 1.0
            jit = random.choice((-6, -3, 0, 4, 7)) if self.glitch else 0
            core.dx = jit
            if halo is not None:
                halo.dx = jit
        for b in self.menu_buttons:
            hit = self.gl_on and (now < b.glitch_until or (self.glitch and random.random() < 0.35))
            b.gx = random.choice((-9, -5, 5, 8, 12)) if hit else 0.0
            b.sprite.alpha = random.choice((0.55, 1.0, 0.8)) if hit and random.random() < 0.5 else 1.0

    def panel_hover_anim(self, dt):
        ps = self.ps
        changed = False
        for e in self.panel_ui.els:
            if e["kind"] != "button":
                continue
            hov = bool((ps.hover and ps.hover[0] == e["id"]) or (ps.kvis and ps.kfocus == e["id"]))
            tgt = 1.0 if hov else 0.0
            cur = ps.hv.get(e["id"], 0.0)
            if cur != tgt:
                cur += (tgt - cur) * min(1.0, dt * 16.0)
                if abs(cur - tgt) < 0.01:
                    cur = tgt
                ps.hv[e["id"]] = cur
                changed = True
        if changed:
            self.panel_dirty = True

    # ----- fenetre redimensionnable --------------------------------------- #
    def on_resize(self, ev):
        w, h = ev.size
        if (w, h) == (self.W, self.H) or w < 300 or h < 300:
            return
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(150, lambda: self.relayout(w, h))

    def relayout(self, w, h):
        self._resize_job = None
        self.W, self.H = w, h
        cur = self.current_monitor()
        if cur:
            self.screen = (cur[3], cur[4])                       # resolution de l'ecran ou se trouve la fenetre
        self.close_dropdown()
        if not self.fullscreen:
            self.settings["window"] = [w, h]
            self.autosave(600)
        self.set_bg(self.bg_mode)
        if self.splash:
            self.splash["sprite"].x, self.splash["sprite"].y = w / 2, h / 2
        self.remove_tag("emerge")
        if self.banner_landed:
            self.remove_tag("banner")
            self.draw_banner(animate=False)
            if self.gear is not None:
                self.gear.sprite.x, self.gear.sprite.y = self.W - 60, 62
            self.show_menu(self.menu_name, animate=False)
        self.rebuild_panel()
        self.place_panel()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        try:
            if self.fullscreen:
                self._win_geo = glfw.get_window_pos(self.win) + glfw.get_window_size(self.win)
                cur = self.current_monitor()
                mon, mw, mh, hz = (cur[0], cur[3], cur[4], cur[5]) if cur else \
                    (glfw.get_primary_monitor(),) + tuple(glfw.get_video_mode(glfw.get_primary_monitor()).size) + (60,)
                glfw.set_window_monitor(self.win, mon, 0, 0, mw, mh, hz)
            else:
                x, y, w, h = self._win_geo or (100, 100, self.W, self.H)
                glfw.set_window_monitor(self.win, None, x, y, w, h, 0)
        except Exception as e:
            log(f"plein ecran : {e!r}")
        self.settings["fullscreen"] = self.fullscreen
        self.save_settings()

    def on_escape(self):
        if self.dd is not None:
            self.close_dropdown()
        elif self.panel is not None:
            self.cancel_panel()
        elif self.menu_name != "main" and self.banner_landed:
            sfx("close")
            self.go_back()
        elif self.fullscreen:
            self.toggle_fullscreen()

    # ----- fond d'ecran ---------------------------------------------------- #
    def menu_overlay(self):
        """Assombrit le fond (x0.62) et ajoute un degrade noir a gauche, derriere les boutons."""
        n = 512
        xs = np.linspace(0.0, 1.0, n)
        a = 0.38 + 0.62 * (190 / 255) * np.maximum(0.0, 1 - xs / 0.45) ** 1.5
        arr = np.zeros((2, n, 4), np.uint8)
        arr[..., :3] = hex_rgb(COL_BG)
        arr[..., 3] = (a * 255).astype(np.uint8)
        return Image.fromarray(arr, "RGBA")

    def set_bg(self, mode):
        self.bg_sprite.set_image(ImageOps.fit(self.bg_src, (self.W, self.H), Image.LANCZOS))
        self.bg_menu.w, self.bg_menu.h = self.W, self.H
        self.bg_menu.alpha = 1.0 if mode == "menu" else 0.0

    # ----- ecran de demarrage / installation (dans la meme fenetre) -------- #
    def build_splash(self):
        p, W, H = self.pal, 640, 340
        bg = ImageEnhance.Brightness(ImageOps.fit(self.bg_src, (W, H), Image.LANCZOS)).enhance(0.45).convert("RGBA")
        d = ImageDraw.Draw(bg)
        d.rectangle([2, 2, W - 3, H - 3], outline=p["accent"], width=2)
        try:
            ic = Image.open(find_asset("icon.png")).convert("RGBA").resize((96, 96), Image.LANCZOS)
            bg.alpha_composite(ic, (W // 2 - 48, 80 - 48))
        except Exception:
            pass
        try:
            path = (
                    find_asset("fonts", "titre.ttf")
                    if os.path.isfile(find_asset("fonts", "titre.ttf"))
                    else None
                    )

            if not path or not os.path.isfile(path):
                path = (
                         find_asset("fonts", "SairaStencilOne-Regular.ttf")
                         if os.path.isfile(find_asset("fonts", "SairaStencilOne-Regular.ttf"))
                         else find_asset("fonts", "Rajdhani-Bold.ttf")
                          )
            halo, core = render_title_parts("THE LAST SIGNAL", path, 38, hex_rgb(p["accent"]))
            tit = Image.alpha_composite(halo, core)
            bg.alpha_composite(tit, (int(W / 2 - tit.width / 2), int(175 - tit.height / 2)))
        except Exception:
            pass
        self.splash = {"base": bg, "pct": 0, "msg": "", "q": queue.Queue(), "t0": time.time(), "done": False,
                       "sprite": self.add(Sprite(bg, self.W / 2, self.H / 2, z=80, tag="splash"))}
        self.splash_draw(0, "")
        threading.Thread(target=self._setup_worker, daemon=True).start()

    def splash_draw(self, pct, msg):
        sp, p, W = self.splash, self.pal, 640
        im = sp["base"].copy()
        d = ImageDraw.Draw(im)
        self.skin.draw_text(d, W / 2, 245 - self.skin.lh(self.body(12)) / 2, msg, self.body(12), 1.0, p["text"], "c")
        x0, y0, x1, y1 = 80, 275, W - 80, 291
        d.rectangle([x0, y0, x1, y1], outline=p["accent"], width=2)
        d.rectangle([x0 + 2, y0 + 2, x0 + 2 + (x1 - x0 - 4) * pct / 100, y1 - 2], fill=p["accent"])
        sp["sprite"].set_image(im)

    def _setup_worker(self):
        q = self.splash["q"]
        try:
            run_setup(lambda pct, msg: q.put((pct, msg)), self.t)
        except Exception:
            q.put((100, self.t("setup_ready")))
        q.put(("done", None))

    def poll_splash(self):
        sp = self.splash
        if not sp:
            return
        try:
            while True:
                pct, msg = sp["q"].get_nowait()
                if pct == "done":
                    sp["done"] = True
                    break
                sp["pct"], sp["msg"] = pct, msg
                self.splash_draw(pct, msg)
        except queue.Empty:
            pass
        if sp["done"] and time.time() - sp["t0"] >= 1.4:
            old, self.splash = sp["sprite"], None
            self.finish_setup(old)

    def finish_setup(self, old=None):
        """Fondu enchaine : l'ecran de chargement s'efface pendant que le fond apparait et que le logo
        emerge de la brume, puis la fenetre de langue arrive."""
        self.set_bg("full")
        self.animate(1.5, lambda t: setattr(self.bg_sprite, "alpha", ease_in_out(t)))
        if old is not None:
            self.animate(1.3, lambda t: setattr(old, "alpha", 1 - ease_in_out(t)), lambda: self.remove(old))
        self.build_emerge()
        self.after(300, self.start_music)
        self.after(700, self.start_net_monitor)
        if self.settings.get("fullscreen"):
            self.after(250, self.toggle_fullscreen)
        self.after(6300, lambda: self.show_panel(self.build_lang_popup, closable=False))   # apres le titre

    def build_emerge(self):
        """Logo qui emerge progressivement de la brume / des cendres du fond d'ecran."""
        self.remove_tag("emerge")
        W, H = self.W, self.H
        try:
            halo, core = self.make_title(int(min(1000, W - 120)))
            logo = Image.alpha_composite(halo, core)
            ic = None
            try:
                ic = Image.open(find_asset("icon.png")).convert("RGBA").resize((150, 150), Image.LANCZOS)
            except Exception:
                pass
            ih = 160 if ic else 0
            cv = Image.new("RGBA", (logo.width, logo.height + ih), (0, 0, 0, 0))
            if ic:
                cv.alpha_composite(ic, ((logo.width - 150) // 2, 0))
            cv.alpha_composite(logo, (0, ih))
            levels = [cv.filter(ImageFilter.GaussianBlur(26)), cv.filter(ImageFilter.GaussianBlur(10)), cv]
            rng = np.random.default_rng(3)
            fog = np.zeros((144, 256), np.float32)
            for (gw, gh), amp in (((4, 3), 1.0), ((8, 5), 0.6), ((16, 9), 0.35), ((32, 18), 0.2)):
                n = Image.fromarray((rng.random((gh, gw)) * 255).astype(np.uint8)).resize((256, 144), Image.BICUBIC)
                fog += np.asarray(n, np.float32) / 255 * amp
            fog = ((fog - fog.min()) / (fog.max() - fog.min())) ** 1.7
            fa = np.zeros((144, 256, 4), np.uint8)
            fa[..., 0], fa[..., 1], fa[..., 2], fa[..., 3] = 205, 178, 160, (fog * 235).astype(np.uint8)
            fogsp = self.add(Sprite(Image.fromarray(fa, "RGBA"), -0.2 * W, 0, W * 1.25, H, anchor="nw", z=30,
                                    tag="emerge", alpha=0.0))
            logos = [self.add(Sprite(im, W / 2, H * 0.45, z=31 + i, tag="emerge", alpha=0.0))
                     for i, im in enumerate(levels)]
        except Exception as e:
            log(f"logo brume : {e!r}")
            return
        base = [(sp.tw, sp.th) for sp in logos]

        def ramp(t, a, b):
            return max(0.0, min(1.0, (t - a) / (b - a)))

        EMERGE, DUR, FADE = 2.3, 6.4, (5.3, 6.2)       # apparition 2,3 s, le titre reste, s'efface juste apres

        def step(t):
            ta = t * DUR
            u = min(1.0, ta / EMERGE)
            fogsp.alpha = 0.8 * math.sin(math.pi * min(1.0, u * 1.12)) ** 1.3
            fogsp.x = -0.2 * W + 0.2 * W * u
            out = 1 - ramp(ta, *FADE)
            alphas = (ramp(u, 0.05, 0.30) * (1 - ramp(u, 0.30, 0.55)),
                      ramp(u, 0.20, 0.45) * (1 - ramp(u, 0.45, 0.70)),
                      ramp(u, 0.40, 0.75))
            k = 1.10 - 0.10 * ease_out_cubic(ramp(u, 0.0, 0.85))
            for sp, a, (tw, th) in zip(logos, alphas, base):
                sp.alpha, sp.w, sp.h = a * out, tw * k, th * k

        self.animate(DUR, step, lambda: self.remove_tag("emerge"))

    # ----- clavier / souris / manette (glfw direct : repetition de touche, touches speciales, boutons souris) ----- #
    def _glfw_close(self, win):
        glfw.set_window_should_close(win, False)
        self.on_close()

    def _glfw_key(self, win, key, scancode, action, mods):
        name = KEY_NAMES.get(key)
        if name:
            self.on_key(name, action, mods)

    def _glfw_pos(self, win, x, y):
        if self.fullscreen or glfw.get_window_attrib(win, glfw.ICONIFIED):
            return
        if self.settings.get("window_pos") != [x, y]:
            self.settings["window_pos"] = [x, y]
            self.autosave(600)

    def monitors_info(self):
        out = []
        try:
            for m in glfw.get_monitors():
                mx, my = glfw.get_monitor_pos(m)
                vm = glfw.get_video_mode(m)
                out.append((m, mx, my, vm.size.width, vm.size.height, vm.refresh_rate))
        except Exception:
            pass
        return out

    def pos_visible(self, x, y):
        """Vrai si la barre de titre de la fenetre tomberait sur un ecran actuellement branche."""
        mons = self.monitors_info()
        return not mons or any(mx <= x + self.W / 2 < mx + mw and my <= y + 20 < my + mh
                               for _, mx, my, mw, mh, _ in mons)

    def current_monitor(self):
        """Ecran qui contient le plus la fenetre : (monitor, x, y, largeur, hauteur, hz)."""
        mons = self.monitors_info()
        if not mons:
            return None
        wx, wy = glfw.get_window_pos(self.win)
        ww, wh = glfw.get_window_size(self.win)

        def overlap(m):
            _, mx, my, mw, mh, _ = m
            return max(0, min(wx + ww, mx + mw) - max(wx, mx)) * max(0, min(wy + wh, my + mh) - max(wy, my))
        return max(mons, key=overlap)

    def _glfw_char(self, win, cp):
        self.on_char(chr(cp))

    def _glfw_cursor(self, win, x, y):
        self.mx, self.my = x, y
        self.on_move()

    def _glfw_mouse(self, win, button, action, mods):
        if action == glfw.PRESS:
            self.on_press(button)
        elif action == glfw.RELEASE:
            self.on_release(button)

    def _glfw_scroll(self, win, dx, dy):
        self.on_scroll(dy)

    def set_cursor(self, kind):
        cur = {"hand": self.cursor_hand, "ibeam": self.cursor_ibeam}.get(kind)
        if kind != getattr(self, "_cursor_kind", None):
            self._cursor_kind = kind
            try:
                glfw.set_cursor(self.win, cur)
            except Exception:
                pass

    def panel_origin(self):
        sp = self.panel
        return sp.x - sp.tw / 2, sp.y - sp.th / 2

    def pick(self):
        """Ce qui est sous la souris : ('dd', ligne) | ('panel', (element, sous-element)) | ('btn', Btn) | None."""
        x, y = self.mx, self.my
        if self.dd is not None:
            dx, dy, dw, dh = self.dd["rect"]
            if dx <= x < dx + dw and dy <= y < dy + dh:
                return ("dd", int((y - dy) // self.dd["rowh"]))
        if self.panel is not None and self.panel_ui is not None:
            ox, oy = self.panel_origin()
            lx, ly = x - ox, y - oy
            if 0 <= lx < self.panel.tw and 0 <= ly < self.panel.th:
                h = self.panel_ui.hit(lx, ly)
                return ("panel", h) if h else ("panel", None)
        btns = list(self.menu_buttons) + ([self.gear] if getattr(self, "gear", None) else [])
        for b in btns:
            if b.contains(x, y):
                return ("btn", b)
        return None

    def on_move(self):
        if self.ps is not None and self.ps.drag:
            self.slider_to(self.mx)
        if getattr(self, "_last_m", None) != (self.mx, self.my):         # vrai mouvement : on cache le focus clavier
            self._last_m = (self.mx, self.my)
            if self.nav_vis:
                self.nav_vis = False
                for b in self.nav_list():
                    b.set_focus(False)
            if self.ps is not None and self.ps.kvis:
                self.ps.kvis = False
                self.panel_dirty = True
        tgt = self.pick()
        # panneau
        if self.ps is not None:
            new = None
            if tgt and tgt[0] == "panel" and tgt[1]:
                e, sub = tgt[1]
                new = (e["id"], sub)
            if new != self.ps.hover:
                if new and self.panel_ui.find(new[0])["kind"] == "button" and (not self.ps.hover or self.ps.hover[0] != new[0]):
                    sfx("hover")
                self.ps.hover = new
                self.panel_dirty = True
        if self.dd is not None:
            row = tgt[1] if tgt and tgt[0] == "dd" else None
            if row != self.dd["hover"]:
                self.dd["hover"] = row
                self.dd_draw()
        # boutons de la scene
        hb = tgt[1] if tgt and tgt[0] == "btn" else None
        if hb is not self.hover_btn:
            if self.hover_btn is not None:
                self.hover_btn.set_state("n")
            self.hover_btn = hb
            if hb is not None:
                hb.set_state("p" if self.down_btn is hb else "h")
                hb.glitch_until = time.time() + 0.14
                if self.down_btn is None:
                    sfx("hover")
        elif hb is not None and self.down_btn is hb:
            hb.set_state("p")
        # curseur
        kind = None
        if hb is not None or (tgt and tgt[0] == "dd"):
            kind = "hand"
        elif tgt and tgt[0] == "panel" and tgt[1]:
            kind = "ibeam" if tgt[1][0]["kind"] == "entry" else "hand"
        self.set_cursor(kind)

    def on_press(self, button):
        ps = self.ps
        # capture d'une touche de controle avec la souris
        if ps is not None and ps.capture is not None:
            tgt = self.pick()
            cell = tgt[1][1] if tgt and tgt[0] == "panel" and tgt[1] and tgt[1][0]["kind"] == "binds" else None
            if ps.capture["col"] == 0 and (button in (1, 2) or (button == 0 and cell == (ps.capture["row"], 0))):
                return self.assign_bind(ps.capture["row"], 0, f"MOUSE{button + 1}")
            ps.capture = None
            self.panel_dirty = True
        if button != 0:
            return
        tgt = self.pick()
        if self.dd is not None:
            if tgt and tgt[0] == "dd":
                self.dd_choose(tgt[1])
            else:
                same = tgt and tgt[0] == "panel" and tgt[1] and tgt[1][0] is self.dd["e"]
                self.close_dropdown()
                if same:
                    return
                tgt = self.pick()
            if tgt and tgt[0] == "dd":
                return
        if tgt and tgt[0] == "panel" and tgt[1]:
            e, sub = tgt[1]
            self.panel_press(e, sub)
        elif tgt and tgt[0] == "btn":
            self.down_btn = tgt[1]
            tgt[1].set_state("p")
            sfx("click")

    def panel_press(self, e, sub):
        ps, k = self.ps, e["kind"]
        self.panel_dirty = True
        if k == "button":
            ps.down = (e["id"], sub)
            sfx("click")
        elif k == "combo":
            self.open_dropdown(e)
        elif k == "slider":
            ps.drag = e["id"]
            self.slider_to(self.mx)
        elif k == "entry":
            ps.focus = e["id"]
            ps.t0 = time.time()
            ox, _ = self.panel_origin()
            iw_x = ox + e["x"] + self.panel_ui.S(2) + self.panel_ui.S(6)
            txt = ps.text.get(e["id"], "")
            best, bx = 0, abs(self.mx - iw_x)
            for i in range(len(txt) + 1):
                w = self.entry_x(e, txt[:i], i)
                if abs(self.mx - (iw_x + w)) < bx:
                    best, bx = i, abs(self.mx - (iw_x + w))
            ps.caret[e["id"]] = best
        elif k == "list":
            if sub is not None:
                ps.sel[e["id"]] = sub
                ps.focus = e["id"]
                now = time.time()
                if now - ps.last_click[0] < 0.4 and ps.last_click[1] == (e["id"], sub):
                    e["on_activate"]()
                ps.last_click = (now, (e["id"], sub))
        elif k == "tabs":
            if sub is not None:
                e["on_pick"](e["labels"][sub][0])
        elif k == "link":
            e["on_click"]()
        elif k == "binds":
            if sub is not None:
                row, col = sub
                ps.capture = {"row": row, "col": col, "base": set(self.pad_down)}

    def entry_x(self, e, txt, caret):
        """Abscisse (dans le champ) du curseur apres 'caret' caracteres."""
        if e["secret"]:
            dot = self.skin.lh(e["spec"], self.panel_ui.s) * 0.30
            return (dot + (caret - 1) * dot * 2.3 + dot / 2 + 2) if caret else 1
        return self.skin.width(txt[:caret], e["spec"], self.panel_ui.s)

    def on_release(self, button):
        if button != 0:
            return
        ps = self.ps
        if ps is not None:
            if ps.drag:
                e = self.panel_ui.find(ps.drag)
                ps.drag = None
                self.panel_dirty = True
                if e:
                    e["on_release"]()
            if ps.down:
                down, ps.down = ps.down, None
                self.panel_dirty = True
                tgt = self.pick()
                if tgt and tgt[0] == "panel" and tgt[1] and tgt[1][0]["id"] == down[0]:
                    e = self.panel_ui.find(down[0])
                    self.after(40, e["command"])
        b, self.down_btn = self.down_btn, None
        if b is not None:
            tgt = self.pick()
            on = tgt and tgt[0] == "btn" and tgt[1] is b
            b.set_state("h" if on else "n")
            if on and b.command:
                self.after(40, b.command)

    def on_scroll(self, dy):
        tgt = self.pick()
        if self.dd is not None:
            return
        if tgt and tgt[0] == "panel":
            ox, oy = self.panel_origin()
            for e in self.panel_ui.els:
                if e["kind"] in ("list", "binds") and e["y"] <= self.my - oy < e["y"] + e["h"]:
                    n = len(e["items"] if e["kind"] == "list" else e["rows"])
                    vis = e["rows"] if e["kind"] == "list" else e["visible"]
                    cur = self.ps.scroll.get(e["id"], 0)
                    self.ps.scroll[e["id"]] = max(0, min(max(0, n - vis), cur - int(dy)))
                    self.panel_dirty = True
                    self.on_move()

    def slider_to(self, x):
        e = self.panel_ui.find(self.ps.drag) if self.ps and self.ps.drag else None
        if not e:
            return
        ox, _ = self.panel_origin()
        tw = self.panel_ui.S(26)
        v = (x - (ox + e["x"] + tw / 2)) / max(1, e["w"] - tw) * 100
        v = int(max(0, min(100, round(v))))
        if v != self.ps.val.get(e["id"]):
            self.ps.val[e["id"]] = v
            self.panel_dirty = True
            e["on_change"](v)

    def on_key(self, name, action, mods):
        ps = self.ps
        pressed, repeat = action != glfw.RELEASE, action == glfw.REPEAT
        if not pressed:
            return
        # capture d'une touche de controle (clavier)
        if ps is not None and ps.capture is not None and ps.capture["col"] == 0:
            if repeat:
                return
            if name == "ESCAPE":
                ps.capture = None
                self.panel_dirty = True
            elif name in ("DELETE", "BACKSPACE"):
                self.assign_bind(ps.capture["row"], 0, "")
            else:
                self.assign_bind(ps.capture["row"], 0, name)
            return
        if ps is not None and ps.capture is not None and name == "ESCAPE":
            ps.capture = None
            self.panel_dirty = True
            return
        if name == "F11" and not repeat:
            return self.toggle_fullscreen()
        if name == "F10" and not repeat:
            self.toggle_crt()
            return
        if self.dd is not None:
            if name == "ESCAPE":
                self.close_dropdown()
            elif name in ("UP", "DOWN"):
                n = len(self.dd["items"])
                cur = self.dd["hover"] if self.dd["hover"] is not None else 0
                self.dd["hover"] = (cur + (1 if name == "DOWN" else -1)) % n
                self.dd_draw()
            elif name in ("ENTER", "KP_ENTER") and self.dd["hover"] is not None:
                self.dd_choose(self.dd["hover"])
            return
        if name == "ESCAPE":
            if not repeat:
                self.on_escape()
            return
        if ps is None or self.panel_ui is None:
            return self.menu_key(name, repeat)
        foc = self.panel_ui.find(ps.focus) if ps.focus else None
        if foc is not None and foc["kind"] == "entry":
            if name in ("UP", "DOWN"):
                return self.panel_nav(1 if name == "DOWN" else -1)
            return self.entry_key(foc, name, mods)
        if foc is not None and foc["kind"] == "list":
            n = len(foc["items"])
            sel = ps.sel.get(foc["id"], 0)
            if name in ("UP", "DOWN"):
                step = 1 if name == "DOWN" else -1
                if not 0 <= sel + step < n:                       # bout de liste : on passe a l'element voisin
                    return self.panel_nav(step)
                sel += step
                ps.sel[foc["id"]] = sel
                sc = ps.scroll.get(foc["id"], 0)
                ps.scroll[foc["id"]] = min(sel, max(sc, sel - foc["rows"] + 1)) if sel >= sc else sel
                self.panel_dirty = True
            elif name in ("ENTER", "KP_ENTER"):
                foc["on_activate"]()
            elif name == "TAB":
                self.panel_nav(-1 if mods & glfw.MOD_SHIFT else 1)
            return
        self.panel_key(name, repeat, mods)

    # ----- navigation clavier / manette : menu principal et panneaux ------------------------- #
    def nav_list(self):
        return list(self.menu_buttons) + ([self.gear] if self.gear is not None else [])

    def nav_set(self, btn):
        for b in self.nav_list():
            b.set_focus(b is btn, True)
        self.nav_btn, self.nav_vis = btn, True

    def menu_key(self, name, repeat):
        btns = self.nav_list()
        if not btns or not self.banner_landed:
            return
        if name in ("UP", "DOWN", "TAB", "LEFT", "RIGHT"):
            step = -1 if name in ("UP", "LEFT") else 1
            i = btns.index(self.nav_btn) if self.nav_btn in btns else (-1 if step > 0 else 0)
            self.nav_set(btns[(i + step) % len(btns)])
            sfx("hover")
        elif name in ("ENTER", "KP_ENTER", "SPACE") and not repeat and self.nav_btn in btns:
            sfx("click")
            self.after(40, self.nav_btn.command)

    def panel_items(self):
        return [e for e in self.panel_ui.els if e["kind"] in ("button", "combo", "slider", "link", "list", "entry")]

    def panel_focus(self, eid):
        ps, e = self.ps, self.panel_ui.find(eid)
        ps.kfocus, ps.kvis = eid, True
        ps.focus = eid if e["kind"] in ("entry", "list") else None
        if e["kind"] == "entry":
            ps.caret.setdefault(eid, len(ps.text.get(eid, "")))
            ps.t0 = time.time()
        self.panel_dirty = True

    def panel_nav(self, step):
        items = self.panel_items()
        if not items:
            return
        ids = [e["id"] for e in items]
        ps = self.ps
        cur = ps.kfocus if ps.kfocus in ids else (ps.focus if ps.focus in ids else None)
        i = ids.index(cur) if cur is not None else (-1 if step > 0 else 0)
        self.panel_focus(ids[(i + step) % len(ids)])
        sfx("hover")

    def panel_key(self, name, repeat, mods):
        ps = self.ps
        if name in ("UP", "DOWN", "TAB"):
            return self.panel_nav(-1 if (name == "UP" or (name == "TAB" and mods & glfw.MOD_SHIFT)) else 1)
        e = self.panel_ui.find(ps.kfocus) if ps.kfocus else None
        if e is None:
            return
        if name in ("ENTER", "KP_ENTER", "SPACE") and not repeat:
            k = e["kind"]
            if k == "button":
                sfx("click")
                self.after(40, e["command"])
            elif k == "combo":
                self.open_dropdown(e)
            elif k == "link":
                e["on_click"]()
        elif name in ("LEFT", "RIGHT") and e["kind"] == "slider":
            v = int(ps.val.get(e["id"], e["value"])) + (5 if name == "RIGHT" else -5)
            v = max(0, min(100, v))
            ps.val[e["id"]] = v
            self.panel_dirty = True
            e["on_change"](v)
            e["on_release"]()

    def entry_key(self, e, name, mods):
        ps = self.ps
        txt = ps.text.get(e["id"], "")
        c = min(ps.caret.get(e["id"], len(txt)), len(txt))
        ps.t0 = time.time()
        self.panel_dirty = True
        if name == "BACKSPACE" and c > 0:
            txt, c = txt[:c - 1] + txt[c:], c - 1
        elif name == "DELETE":
            txt = txt[:c] + txt[c + 1:]
        elif name == "LEFT":
            c = max(0, c - 1)
        elif name == "RIGHT":
            c = min(len(txt), c + 1)
        elif name == "HOME":
            c = 0
        elif name == "END":
            c = len(txt)
        elif name == "V" and mods & glfw.MOD_CONTROL:
            try:
                clip = glfw.get_clipboard_string(self.win) or ""
                clip = clip.decode("utf-8", "ignore") if isinstance(clip, bytes) else clip
                clip = "".join(ch for ch in clip if ch.isprintable())
                txt, c = txt[:c] + clip + txt[c:], c + len(clip)
            except Exception:
                pass
        elif name in ("ENTER", "KP_ENTER"):
            if e["on_submit"]:
                e["on_submit"]()
        elif name == "TAB":
            ids = [x["id"] for x in self.panel_ui.els if x["kind"] == "entry"]
            ps.focus = ids[(ids.index(e["id"]) + (-1 if mods & glfw.MOD_SHIFT else 1)) % len(ids)]
        ps.text[e["id"]], ps.caret[e["id"]] = txt, c

    def on_char(self, ch):
        ps = self.ps
        if ps is None or self.panel_ui is None or not ps.focus or not ch.isprintable():
            return
        e = self.panel_ui.find(ps.focus)
        if e is None or e["kind"] != "entry":
            return
        txt = ps.text.get(e["id"], "")
        c = min(ps.caret.get(e["id"], len(txt)), len(txt))
        ps.text[e["id"]] = txt[:c] + ch + txt[c:]
        ps.caret[e["id"]] = c + 1
        ps.t0 = time.time()
        self.panel_dirty = True

    # ----- manette ---------------------------------------------------------- #
    def poll_gamepad(self, now):
        capturing = self.ps is not None and self.ps.capture is not None and self.ps.capture["col"] == 1
        if not capturing and now - self._pad_t < 0.15:
            return
        self._pad_t = now
        name, down = None, set()
        try:
            for jid in range(glfw.JOYSTICK_1, glfw.JOYSTICK_LAST + 1):
                if glfw.joystick_present(jid) and glfw.joystick_is_gamepad(jid):
                    st = glfw.get_gamepad_state(jid)
                    if st is None:
                        continue
                    name = glfw.get_gamepad_name(jid) or glfw.get_joystick_name(jid) or "Gamepad"
                    for i, b in enumerate(st.buttons):
                        if b and i in PAD_BUTTONS:
                            down.add(PAD_BUTTONS[i])
                    ax = st.axes
                    for (ix, iy, pre) in ((glfw.GAMEPAD_AXIS_LEFT_X, glfw.GAMEPAD_AXIS_LEFT_Y, "LS"),
                                          (glfw.GAMEPAD_AXIS_RIGHT_X, glfw.GAMEPAD_AXIS_RIGHT_Y, "RS")):
                        if ax[ix] > 0.6:
                            down.add(pre + "_RIGHT")
                        elif ax[ix] < -0.6:
                            down.add(pre + "_LEFT")
                        if ax[iy] > 0.6:
                            down.add(pre + "_DOWN")
                        elif ax[iy] < -0.6:
                            down.add(pre + "_UP")
                    if ax[glfw.GAMEPAD_AXIS_LEFT_TRIGGER] > 0.5:
                        down.add("LT")
                    if ax[glfw.GAMEPAD_AXIS_RIGHT_TRIGGER] > 0.5:
                        down.add("RT")
                    break
        except Exception:
            name, down = None, set()
        if name != self.pad_name:
            self.pad_name = name
            if self.panel_builder == self.build_controls:
                self.refresh_panel()
        if capturing:
            cap = self.ps.capture
            new = [tok for tok in sorted(down) if tok not in cap["base"]]
            cap["base"] &= down | cap["base"]
            if new:
                self.assign_bind(cap["row"], 1, new[0])
        prev, self.pad_down = self.pad_down, down
        if not capturing and name and glfw.get_window_attrib(self.win, glfw.FOCUSED):
            for toks, key in ((("DPAD_UP", "LS_UP"), "UP"), (("DPAD_DOWN", "LS_DOWN"), "DOWN"),
                              (("DPAD_LEFT", "LS_LEFT"), "LEFT"), (("DPAD_RIGHT", "LS_RIGHT"), "RIGHT")):
                if any(t in down for t in toks):
                    self.on_key(key, glfw.PRESS, 0)
                    break
            if "A" in down and "A" not in prev:
                self.on_key("ENTER", glfw.PRESS, 0)
            if "B" in down and "B" not in prev:
                self.on_key("ESCAPE", glfw.PRESS, 0)

    # ----- listes deroulantes (combobox) ----------------------------------- #
    def open_dropdown(self, e):
        ox, oy = self.panel_origin()
        ui = self.panel_ui
        rowh = self.skin.lh(e["spec"], ui.s) + ui.S(10)
        w, h = e["w"], rowh * len(e["values"]) + 2
        x, y = ox + e["x"], oy + e["y"] + e["h"]
        if y + h > self.H - 4:
            y = max(4, oy + e["y"] - h)
        cur = e["values"].index(e["current"]) if e["current"] in e["values"] else None
        self.dd = {"e": e, "items": e["values"], "rect": (x, y, w, h), "rowh": rowh, "hover": cur,
                   "spec": e["spec"], "s": ui.s, "sprite": self.add(Sprite(None, x, y, anchor="nw", z=60))}
        self.dd_draw()

    def dd_draw(self):
        dd, p = self.dd, self.pal
        x, y, w, h = dd["rect"]
        im = Image.new("RGBA", (w, h), p["accent"])
        d = ImageDraw.Draw(im)
        d.rectangle([1, 1, w - 2, h - 2], fill=p["panel_alt"])
        for i, it in enumerate(dd["items"]):
            ry = 1 + i * dd["rowh"]
            on = dd["hover"] == i
            if on:
                d.rectangle([1, ry, w - 2, ry + dd["rowh"] - 1], fill=p["accent"])
            self.skin.draw_text(d, 10 * dd["s"], ry + (dd["rowh"] - self.skin.lh(dd["spec"], dd["s"])) / 2, it,
                                dd["spec"], dd["s"], p["panel"] if on else p["text"], "l")
        dd["sprite"].set_image(im)

    def close_dropdown(self):
        if self.dd is not None:
            self.remove(self.dd["sprite"])
            self.dd = None

    def dd_choose(self, i):
        dd = self.dd
        if dd is None or not (0 <= i < len(dd["items"])):
            return
        val, cb = dd["items"][i], dd["e"]["on_select"]
        self.close_dropdown()
        cb(val)

    # ----- banniere -------------------------------------------------------- #
    def make_title(self, bw):
        """Rend le titre (halo + coeur) pour qu'il tienne entre les deux eclairs, centre."""
        path = (find_asset("fonts", "titre.ttf")
        if os.path.isfile(find_asset("fonts", "titre.ttf"))
        else None
         )
        if not path or not os.path.isfile(path):
            path = (
            find_asset("fonts", "SairaStencilOne-Regular.ttf")
            if os.path.isfile(find_asset("fonts", "SairaStencilOne-Regular.ttf"))
            else find_asset("fonts", "Rajdhani-Bold.ttf")
            ) 
        glow = hex_rgb(self.pal["accent"])
        text = "THE LAST SIGNAL"
        target = bw - 2 * 118
        w100 = _title_font(path, 100).getlength(text)
        px = int(max(28, min(84, target / (w100 / 100 + 1.0))))
        for _ in range(5):
            halo, core = render_title_parts(text, path, px, glow)
            if core.width <= target or px <= 28:
                break
            px = max(28, int(px * target / core.width) - 1)
        return halo, core

    def draw_banner(self, animate=True):
        p = self.pal
        bw = int(min(900, self.W - 260))
        halo, core = self.make_title(bw)
        bh = max(104, core.height + 34)
        y0, cx = 26, self.W / 2
        x0, y1 = cx - bw / 2, y0 + bh
        cy = (y0 + y1) / 2
        self.banner_h = bh
        pad = 12
        im = Image.new("RGBA", (bw + 2 * pad + 8, bh + 2 * pad + 10), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle([pad + 7, pad + 9, pad + bw + 7, pad + bh + 9], fill=(0, 0, 0, 255))
        d.rectangle([pad, pad, pad + bw, pad + bh], fill=p["panel"], outline=p["accent"], width=3)
        d.rectangle([pad + 10, pad + 10, pad + bw - 10, pad + bh - 10], outline=p["accent_dim"], width=1)
        for rx in (pad + 20, pad + bw - 20):
            for ry in (pad + 20, pad + bh - 20):
                d.ellipse([rx - 5, ry - 5, rx + 5, ry + 5], fill=p["panel_alt"], outline=p["accent"])
        parts = [Sprite(im, x0 - pad, y0 - pad, anchor="nw", z=20, tag="banner")]
        pts = [(4, -28), (-10, 6), (-2, 6), (-6, 28), (10, -8), (2, -8), (8, -28)]
        big = Image.new("RGBA", (24 * 4, 60 * 4), (0, 0, 0, 0))
        ImageDraw.Draw(big).polygon([(4 * (12 + a), 4 * (30 + b)) for a, b in pts], fill=(255, 255, 255, 255))
        bolt = big.resize((24, 60), Image.LANCZOS)
        self.bolts = [Sprite(bolt, bx, cy, z=21, tag="banner") for bx in (x0 + 62, x0 + bw - 62)]
        self.title_halo = Sprite(halo, cx, cy, z=22, tag="banner")
        parts += self.bolts + [self.title_halo, Sprite(core, cx, cy, z=23, tag="banner")]
        for sp in parts:
            sp.by = sp.y
            self.add(sp)
        self.banner_parts = parts
        self.title_core = parts[-1]
        self.pulse(time.time())
        if not animate:
            return
        total = y1 + 50
        self.set_banner_dy(-total)

        def step(t):
            self.set_banner_dy(-total * (1 - ease_out_bounce(t)))

        self.animate(1.2, step, self.after_banner)

    def set_banner_dy(self, dy):
        for sp in self.banner_parts:
            sp.y = sp.by + dy

    def drop_banner(self):
        self.draw_banner(animate=True)

    def pulse(self, now):
        if not self.banner_landed and not getattr(self, "banner_parts", None):
            return
        p = self.pal
        t = (math.sin(now * 2.2) + 1) / 2
        col = hex_rgb(mix(p["accent_dim"], p["accent"], 0.25 + 0.6 * t))
        for b in getattr(self, "bolts", []):
            b.tint = tuple(c / 255 for c in col)
        if getattr(self, "title_halo", None) is not None:
            self.title_halo.alpha = min(1.0, 0.35 + 0.7 * t)

    def after_banner(self):
        p = self.pal
        self.banner_landed = True
        gear_n, gear_h = make_gear(30, p["text"]), make_gear(30, p["panel"])
        self.gear = Btn(self, command=self.toggle_settings, image=gear_n, hover_image=gear_h, z=30, tag="gear",
                        slide=False)
        self.gear.sprite.x, self.gear.sprite.y = self.W - 60, 62
        for sp in self.gear.sprites():
            self.add(sp)
        self.show_menu("main")

    # ----- menus ----------------------------------------------------------- #
    def account_label(self):
        if self.user:
            name = self.user if len(self.user) <= 16 else self.user[:15] + "..."
            return self.t("logged_as").format(name)
        return self.t("account")

    def text_sprite(self, text, spec, color, x, y, z=10, tag="menu"):
        sk = self.skin
        w, h = int(sk.width(text, spec)) + 8, sk.lh(spec) + 8
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sk.draw_text(ImageDraw.Draw(im), w / 2, 4, text, spec, 1.0, color, "c")
        return self.add(Sprite(im, x, y, z=z, tag=tag))

    def show_menu(self, name, animate=True):
        t, p = self.t, self.pal
        self.menu_name = name
        self.remove_tag("menu")
        self.menu_buttons = []
        self.hover_btn = self.down_btn = self.nav_btn = None
        self.nav_vis = False

        header = None
        if name == "main":
            specs = [(t("solo"), lambda: self.show_menu("solo")),
                     (t("multi"), self.go_multi),
                     (self.account_label(), lambda: self.open_auth(None)),
                     (t("credits"), self.open_credits),
                     (t("quit"), self.on_close)]
        elif name == "solo":
            header = t("solo")
            specs = [(t("new_solo"), lambda: self.launch_game("solo")),
                     (t("load_save"), lambda: self.open_saves("solo")),
                     (t("back"), self.go_back)]
        else:
            header = t("multi")
            specs = [(t("new_multi"), lambda: self.launch_game("multi")),
                     (t("load_save"), lambda: self.open_saves("multi")),
                     (t("back"), self.go_back)]

        # police ajustee : le plus long libelle doit tenir en entier dans le bouton, sans jamais sortir de la fenetre
        fs, max_btn = 14, self.W * 0.46
        while fs > 9 and max(self.skin.width(l.upper(), self.font(fs)) for l, _ in specs) + 56 > max_btn:
            fs -= 1
        zw = self.skin.zero(self.font(fs))
        bw_chars = max(BTN_W, max(self.skin.width(l.upper(), self.font(fs)) + 56 for l, _ in specs) / zw)
        self._menu_half = (int(bw_chars * zw) + 6) / 2 + Btn.SHIFT
        mx = self.menu_x()
        y0 = int(self.H * (0.40 if header else 0.355))
        spacing = max(60, min(82, (self.H - 70 - y0) / max(1, len(specs) - 1)))
        if header:
            self.text_sprite(header.upper(), self.font(24), p["accent"], mx, y0 - 80)
            self.add(Sprite(self.white, mx, y0 - 50, 340, 2, z=10, tag="menu", tint=hex_tint(p["accent_dim"])))

        for i, (label, cmd) in enumerate(specs):
            btn = Btn(self, text=label, command=cmd, spec=self.font(fs), width=bw_chars)
            self.menu_buttons.append(btn)
            for sp in btn.sprites():
                self.add(sp)
            y = int(y0 + i * spacing)
            if animate:
                btn.sprite.x, btn.sprite.y = -260, y
                self.after(120 * i, lambda b=btn, yy=y, tx=mx: self.slide_in(b, tx, yy))
            else:
                btn.sprite.x, btn.sprite.y = mx, y
            if name == "main" and i == 1:       # voyant d'etat a cote de "Multijoueur"
                lx = mx + btn.size()[0] // 2 + 26
                self.after(120 * i + 480 if animate else 0, lambda lx=lx, yy=y: self.draw_led(lx, yy))

    # ----- voyant reseau --------------------------------------------------- #
    def led_color(self):
        return {True: "#46d36a", False: "#e0483c"}.get(self.net_ok, self.pal["muted"])

    def draw_led(self, x, y):
        if self.menu_name != "main":
            return
        col, p = self.led_color(), self.pal
        txt = {True: self.t("net_on"), False: self.t("net_off")}.get(self.net_ok, "...").upper()
        spec = self.body(10, True)
        w = 35 + int(self.skin.width(txt, spec)) + 10
        im = Image.new("RGBA", (w, 30), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([1, 2, 27, 28], fill=mix(p["panel"], col, 0.28))
        d.ellipse([7, 8, 21, 22], fill=col, outline=p["panel"], width=2)
        self.skin.draw_text(d, 35, 15 - self.skin.lh(spec) / 2, txt, spec, 1.0, col, "l")
        self.remove_tag("led")
        self.add(Sprite(im, x - 14, y, anchor="w", z=11, tag="led"))
        self.led_pos = (x, y)

    def start_net_monitor(self):
        threading.Thread(target=self._net_worker, daemon=True).start()

    def _net_worker(self):
        while not self._closing:
            host, port = SERVER_ADDR if SERVER_ADDR[0] else ("1.1.1.1", 443)
            try:
                socket.create_connection((host, port), timeout=2.5).close()
                ok = True
            except Exception:
                ok = False
            self.jobs.put(lambda ok=ok: self.set_net(ok))
            for _ in range(30):
                if self._closing:
                    return
                time.sleep(0.5)

    def set_net(self, ok):
        if ok != self.net_ok:
            self.net_ok = ok
            if self.led_pos and any(s.tag == "led" for s in self.sprites):
                self.draw_led(*self.led_pos)

    def slide_in(self, btn, tx, y, dur=0.42):
        x0 = -260

        def step(t):
            btn.sprite.x, btn.sprite.y = x0 + (tx - x0) * ease_out_cubic(t), y

        if btn in self.menu_buttons:
            self.animate(dur, step)

    def go_back(self):
        self.close_panel()
        self.show_menu("main")

    def go_multi(self):
        if self.user:
            self.show_menu("multi")
        else:
            self.open_auth(lambda: self.show_menu("multi"))

    # ----- musique --------------------------------------------------------- #
    def start_music(self):
        self.music_gen += 1
        threading.Thread(target=self._music_worker, daemon=True).start()

    def load_sfx(self, pg):
        for name in ("hover", "click", "launch", "open", "close"):
            for fn in ("ui_" + name, name):            # nouveaux sons ui_*.wav en priorite, anciens en secours
                p = find_asset("sfx", fn + ".wav")
                if os.path.exists(p):
                    try:
                        self.sfx[name] = pg.mixer.Sound(p)
                        break
                    except Exception as e:
                        log(f"sfx {fn}: {e!r}")

    def play_sfx(self, name):
        snd, vol = self.sfx.get(name), self.settings.get("volume", 50)
        if snd is None or vol <= 0:
            return
        try:
            snd.set_volume(min(1.0, vol / 100 * 1.4))
            snd.play()
        except Exception:
            pass

    def _ramp_down(self, pg, gen, secs):
        """Fondu sortant du morceau, execute dans le thread musique (l'interface ne bouge pas)."""
        try:
            v0 = pg.mixer.music.get_volume()
            n = max(1, int(secs / 0.05))
            for k in range(n):
                if gen != self.music_gen:
                    return
                pg.mixer.music.set_volume(v0 * (1 - (k + 1) / n))
                time.sleep(0.05)
        except Exception:
            pass

    def _music_worker(self):
        gen = self.music_gen
        tracks = find_playlist()
        log(f"playlist ({len(tracks)}) : {[os.path.basename(t) for t in tracks]}")
        if not tracks:
            log("aucune piste trouvee (dossier music/ vide ?)")
            return
        pg = None
        try:
            try:
                import pygame as pg
            except ImportError:
                if not FROZEN:
                    subprocess.run([sys.executable, "-m", "pip", "install", "--only-binary=:all:", "pygame-ce>=2.5.6"],
                                   capture_output=True, timeout=900)
                    importlib.invalidate_caches()
                    import pygame as pg
        except Exception as e:
            log(f"pygame indisponible : {e!r}")
            pg = None
        if pg is not None:
            try:
                pg.mixer.init()
                self.pygame = pg
                self.load_sfx(pg)
                order, i, last, t_start = tracks[:], 0, None, 0.0
                random.shuffle(order)
                while gen == self.music_gen and not self.music_stop:
                    if not pg.mixer.music.get_busy():             # morceau fini -> le suivant
                        nxt = order[i % len(order)]
                        if nxt == last and len(order) > 1:
                            i += 1
                            nxt = order[i % len(order)]
                        try:
                            log(f"lecture : {os.path.basename(nxt)}")
                            pg.mixer.music.load(nxt)
                            pg.mixer.music.set_volume(self.settings.get("volume", 50) / 100)
                            pg.mixer.music.play(fade_ms=2500)
                            last, t_start = nxt, time.time()
                            self.music_skip = False
                        except Exception as e:
                            log(f"erreur de lecture : {e!r}")
                            time.sleep(1.5)
                        i += 1
                        if i % len(order) == 0:
                            random.shuffle(order)
                    elif len(order) > 1 and (self.music_skip or time.time() - t_start > MAX_TRACK_SECONDS):
                        self.music_skip = False                   # changement de morceau en fondu
                        self.muffle_stop(1600)
                        self._ramp_down(pg, gen, 1.6)
                        if gen == self.music_gen:
                            pg.mixer.music.stop()
                        continue
                    self.music_skip = self.music_skip and len(order) > 1
                    time.sleep(0.3)
                return
            except Exception as e:
                log(f"pygame.mixer : {e!r}")
                self.pygame = None
        wavs = [t for t in tracks if t.lower().endswith(".wav")]
        if os.name == "nt" and wavs:   # secours sans pygame (Windows) : pistes WAV les unes apres les autres
            try:
                import winsound
                log("secours winsound")
                self.winsound_track = wavs[0]
                order, i = wavs[:], 0
                random.shuffle(order)
                while gen == self.music_gen and not self.music_stop:
                    if self.settings.get("volume", 50) <= 0:
                        time.sleep(0.5)
                        continue
                    self.winsound_playing = True
                    winsound.PlaySound(order[i % len(order)], winsound.SND_FILENAME)   # bloque jusqu'a la fin
                    self.winsound_playing = False
                    i += 1
            except Exception as e:
                log(f"winsound : {e!r}")

    def next_track(self):
        """Passe au morceau suivant (appele par ex. a la connexion)."""
        try:
            if self.pygame:
                self.music_skip = True
            elif self.winsound_track and self.winsound_playing:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)   # la boucle enchaine sur la piste suivante
        except Exception:
            pass

    def apply_volume(self):
        v = self.settings.get("volume", 50)
        try:
            if self.pygame:
                self.pygame.mixer.music.set_volume(v / 100)
                self._muffle_dirty = True
            elif self.winsound_track and v == 0 and self.winsound_playing:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
                self.winsound_playing = False
        except Exception:
            pass

    def _fade_thread(self, secs):
        pg = self.pygame
        try:
            v0 = pg.mixer.music.get_volume()
            n = max(1, int(secs / 0.04))
            for k in range(n):
                pg.mixer.music.set_volume(v0 * (1 - (k + 1) / n))
                time.sleep(0.04)
            pg.mixer.music.stop()
        except Exception:
            pass

    def fade_out_music(self, ms=1500):
        """Baisse progressivement la musique (sans bloquer l'interface), puis l'arrete."""
        self.music_stop = True
        self.muffle_stop(ms)
        try:
            if self.pygame:
                threading.Thread(target=self._fade_thread, args=(ms / 1000,), daemon=True).start()
            elif self.winsound_track and self.winsound_playing:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
                self.winsound_playing = False
        except Exception:
            pass

    def restore_music(self):
        if self.music_stop and not self._closing:
            self.music_stop = False
            self.start_music()

    def on_close(self):
        if self._closing:
            return
        self._closing = True
        self.save_settings()
        self.fade_out_music(700)
        self.after(750, self.destroy)

    # ----- panneaux (popups) ---------------------------------------------- #
    def show_panel(self, builder, closable=True, side=False):
        self.close_panel(sound=False)
        self.panel_builder, self.panel_closable = builder, closable
        self.panel_mode = "side" if side else "center"
        self.ps = PanelState()
        self.nav_vis = False
        for b in self.nav_list():
            b.set_focus(False)
        self.panel = self.add(Sprite(None, 0, 0, z=50, tag="panel"))
        self.rebuild_panel()
        self.place_panel()
        self.fade_panel()
        if builder != self.build_lang_popup:
            sfx("open")                       # petit "balayage de frequence radio"
            # (musique etouffee desactivee : la musique continue normalement dans les menus)

    def rebuild_panel(self):
        """(Re)construit le contenu du panneau. Si la fenetre est trop petite, tout est reduit
        (polices comprises) jusqu'a ce que le panneau tienne en entier : plus de menu coupe."""
        if self.panel is None or self.panel_builder is None:
            return
        if self.panel_mode == "side":
            top = (26 + self.banner_h + 16) if self.banner_h else 10
            avail_h, avail_w = self.H - top - 12, self.W - (self.menu_x() + 190) - 12
        else:
            avail_h, avail_w = self.H - 24, self.W - 24
        s, ui = 1.0, None
        for _ in range(4):
            ui = PanelUI(self, s)
            self.panel_builder(ui)
            ui.finish()
            k = min(avail_h / ui.H, avail_w / ui.W)
            if k >= 0.995 or s <= 0.45:
                break
            s = max(0.45, s * k * 0.99)
        self.panel_ui = ui
        self.panel_dirty = False
        self.panel.set_image(ui.render(self.ps, time.time()))

    def place_panel(self):
        if self.panel is None:
            return
        pw, ph, W, H = self.panel.tw, self.panel.th, self.W, self.H
        if self.panel_mode == "center":
            x, y = W / 2, H / 2
        else:
            mx = self.menu_x()
            x = max((W + mx + 190) / 2, mx + 190 + 280)
            x = min(x, W - 280)
            left, right = mx + 190, W - 12
            x = min(max(x, left + pw / 2), right - pw / 2) if pw <= right - left else (left + right) / 2
            top = (26 + self.banner_h + 16) if self.banner_h else 10
            y = max(top + ph / 2, min(H * 0.56, H - ph / 2 - 12))
        self.panel.x, self.panel.y = x, y

    def fade_panel(self, dur=0.42, dx=90):
        """Apparition du panneau : fondu depuis le noir + glissement depuis la droite (ease-out expo)."""
        sp = self.panel
        bx = sp.x
        sp.tint, sp.x = (0.0, 0.0, 0.0), bx + dx

        def step(t):
            if self.panel is not sp:
                return
            e = ease_out_expo(t)
            f = min(1.0, t * 2.6)
            sp.tint, sp.x = (f, f, f), bx + dx * (1 - e)

        self.animate(dur, step)

    def refresh_panel(self):
        if self.panel is not None:
            self.rebuild_panel()
            self.place_panel()

    def close_panel(self, sound=True):
        self.close_dropdown()
        if sound and self.panel is not None and self.panel_builder != self.build_lang_popup:
            sfx("close")
        self.remove(self.panel)
        self.panel = self.panel_builder = self.ps = self.panel_ui = None
        self.pending_delete = None
        self.show_local = False
        self.set_muffle(False)
        self.set_cursor(None)

    def cancel_panel(self):
        if self.panel is None or not self.panel_closable:
            return
        self.pending_auth = None
        self.close_panel()

    def lang_pick(self, on_change):
        """Callback de la liste de langues."""
        def selected(name):
            self.lang = next(k for k, v in LANGS.items() if v == name)
            self.save_settings()
            self.after_idle(on_change)
        return selected

    # ----- popup de langue ------------------------------------------------- #
    def build_lang_popup(self, ui):
        ui.title("LANGUE  ·  LANGUAGE  ·  言語  ·  IDIOMA", size=17, gap=20)
        ui.combo(list(LANGS.values()), LANGS[self.lang], self.lang_pick(self.refresh_panel), pad=(0, 22))
        ui.button(self.t("confirm"), self.confirm_language, self.font(14), width=22, pad=(0, 0))

    def confirm_language(self):
        self.save_settings()
        self.close_panel()
        self.crossfade()

    def crossfade(self):
        """Le fond s'assombrit en fondu, puis la banniere tombe."""
        def done():
            self.bg_mode = "menu"
            self.drop_banner()

        self.animate(0.30, lambda t: setattr(self.bg_menu, "alpha", t), done)

    # ----- remerciements --------------------------------------------------- #
    def open_credits(self):
        self.show_panel(self.build_credits, side=True)

    def build_credits(self, ui):
        t = self.t
        ui.title(t("credits_title"))
        ui.label(t("thanks"), self.body(12), "muted", wrap=380, pad=(0, 22))
        for name, role in (("Morgan Piva", "role_lead"), ("Cyril Capiez", "role_dev")):
            ui.label(name.upper(), self.font(22), "text")
            ui.label(t(role), self.body(12, True), "accent", wrap=380, pad=(2, 20))
        ui.button(t("back"), self.cancel_panel, self.font(13), width=26, pad=(0, 0))

    # ----- parametres ------------------------------------------------------ #
    def toggle_settings(self):
        if self.panel_builder == self.build_settings:
            self.cancel_panel()
        else:
            self.show_panel(self.build_settings, side=True)

    def build_settings(self, ui):
        t = self.t
        ui.title(t("settings_title"))
        ui.label(t("language"), self.body(11), "muted", align="w", pad=(0, 4))
        ui.combo(list(LANGS.values()), LANGS[self.lang], self.lang_pick(self.refresh_all), pad=(0, 18))
        ui.label(t("volume"), self.body(11), "muted", align="w", pad=(0, 4))
        ui.slider(self.settings.get("volume", 50), self.set_volume, self.save_settings, pad=(0, 18))
        ui.label(t("resolution"), self.body(11), "muted", align="w", pad=(0, 4))
        sw, sh = self.screen
        sizes = [r for r in ((1280, 720), (1600, 900), (1920, 1080), (2560, 1440), (3840, 2160))
                 if r[0] <= sw and r[1] <= sh]
        cur = f"{self.W} × {self.H}"
        values = [f"{w} × {h}" for w, h in sizes]
        if cur not in values:
            values.insert(0, cur)
        ui.combo(values, cur, self.pick_resolution, pad=(0, 18))
        ui.button(t("fullscreen"), self.toggle_fullscreen, self.font(12), width=26, pad=(0, 8))
        ui.button(t("crt_on" if self.crt else "crt_off"), self.toggle_crt, self.font(12), width=26, pad=(0, 8))
        ui.button(t("gl_on" if self.gl_on else "gl_off"), self.toggle_glitch, self.font(12), width=26, pad=(0, 8))
        ui.button(t("controls"), self.open_controls, self.font(12), width=26, pad=(0, 8))
        ui.button(t("close"), self.cancel_panel, self.font(12), width=26, pad=(0, 0))

    def toggle_crt(self):
        self.crt = not self.crt
        self.settings["crt"] = self.crt
        self.save_settings()
        self.refresh_panel()

    def toggle_glitch(self):
        self.gl_on = not self.gl_on
        self.settings["glitch"] = self.gl_on
        self.save_settings()
        self.refresh_panel()

    def pick_resolution(self, val):
        w, h = (int(v) for v in val.replace("×", " ").split())
        if self.fullscreen:
            self.toggle_fullscreen()
        glfw.set_window_size(self.win, w, h)        # relayout() enregistre la taille automatiquement

    def set_volume(self, value):
        self.settings["volume"] = int(float(value))
        self.apply_volume()
        self.autosave()

    def refresh_all(self):
        self.show_menu(self.menu_name, animate=False)
        self.refresh_panel()

    # ----- controles clavier / manette -------------------------------------- #
    def open_controls(self):
        self.show_panel(self.build_controls, side=True)

    def build_controls(self, ui):
        t = self.t
        ctl = get_controls(self.settings)
        ui.title(t("controls_title"))
        rows = [(t("act_" + a), ctl["keyboard"][a], ctl["gamepad"][a]) for a in ACTIONS]
        ui.bindtable(rows, visible=6 if self.H < 760 else 8, on_cell=None)
        ui.label(t("c_hint"), self.body(10), "muted", wrap=520, pad=(10, 4))
        if self.pad_name:
            ui.label(t("c_pad_ok").format(self.pad_name), self.body(11, True), "ok", wrap=520, pad=(0, 12))
        else:
            ui.label(t("c_pad_none"), self.body(11), "muted", wrap=520, pad=(0, 12))
        ui.button(t("c_reset"), self.reset_controls, self.font(12), width=26, pad=(0, 8))
        ui.button(t("back"), lambda: self.show_panel(self.build_settings, side=True), self.font(12), width=26,
                  pad=(0, 0))

    def assign_bind(self, row, col, token):
        """Affecte une touche / un bouton a une action ; si un autre l'utilisait deja, les deux s'echangent."""
        dev, act = ("keyboard", "gamepad")[col], ACTIONS[row]
        ctl = get_controls(self.settings)
        if token:
            other = next((a for a in ACTIONS if a != act and ctl[dev][a] == token), None)
            if other:
                ctl[dev][other] = ctl[dev][act]
        ctl[dev][act] = token
        self.settings["controls"] = ctl
        self.save_settings()
        if self.ps is not None:
            self.ps.capture = None
        self.refresh_panel()
        sfx("click")

    def reset_controls(self):
        self.settings["controls"] = {dev: dict(v) for dev, v in DEFAULT_CONTROLS.items()}
        self.save_settings()
        if self.ps is not None:
            self.ps.capture = None
        self.refresh_panel()

    # ----- sauvegardes ----------------------------------------------------- #
    def open_saves(self, mode):
        self.show_panel(lambda ui: self.build_saves(ui, mode), side=True)

    def build_saves(self, ui, mode):
        t = self.t
        ui.title(t("saves_title"))
        folder = os.path.join(SAVES_DIR, mode)
        files = []
        try:
            for f in os.listdir(folder):
                if f.lower().endswith((".json", ".sav", ".save")):
                    full = os.path.join(folder, f)
                    files.append((os.path.getmtime(full), full))
        except OSError:
            pass
        files.sort(reverse=True)

        if not files:
            ui.label(t("no_saves"), self.body(13), "muted", pad=(10, 24))
        else:
            items = []
            for m, full in files:
                stem = os.path.splitext(os.path.basename(full))[0]
                items.append(f" {stem}    ·    {datetime.fromtimestamp(m):%d/%m/%Y %H:%M}")

            def play():
                sel = self.ps.sel.get("saves", 0)
                if 0 <= sel < len(files):
                    path = files[sel][1]
                    self.close_panel()
                    self.launch_game(mode, path)

            self.ps.focus = self.ps.focus or "saves"
            ui.listbox("saves", items, play, rows=8, width=40, pad=(0, 16))

            pend = self.pending_delete if self.pending_delete and self.pending_delete[0] == mode else None
            if pend:      # etape de confirmation, en rouge
                stem = os.path.splitext(os.path.basename(pend[1]))[0]
                ui.label(t("confirm_delete").format(stem), self.body(12, True), "err", wrap=360, pad=(0, 12))
                ui.button(t("yes"), self.do_delete_save, self.font(13), width=26, pal=dict(self.pal, accent=self.pal["err"]))
                ui.button(t("no"), self.cancel_delete, self.font(13), width=26, pad=(0, 0))
                return

            def ask_delete():
                sel = self.ps.sel.get("saves", 0)
                if 0 <= sel < len(files):
                    self.pending_delete = (mode, files[sel][1])
                    self.refresh_panel()

            ui.button(t("play"), play, self.font(13), width=26)
            ui.button(t("delete"), ask_delete, self.font(12), width=26, pal=dict(self.pal, accent=self.pal["err"]))
        ui.button(t("back"), self.cancel_panel, self.font(13), width=26, pad=(0, 0))

    def do_delete_save(self):
        pend, self.pending_delete = self.pending_delete, None
        if pend:
            try:
                os.remove(pend[1])
            except OSError:
                pass
        self.refresh_panel()

    def cancel_delete(self):
        self.pending_delete = None
        self.refresh_panel()


    # ----- profil ---------------------------------------------------------- #
    def profile_key(self):
        return (self.user or "_invite").lower()

    def add_playtime(self, seconds):
        data = load_json(PROFILES_FILE, {})
        prof = data.setdefault(self.profile_key(), {})
        prof["playtime"] = int(prof.get("playtime", 0) + seconds)
        save_json(PROFILES_FILE, data)

    def last_save_info(self):
        newest, count = None, 0
        for mode in ("solo", "multi"):
            folder = os.path.join(SAVES_DIR, mode)
            try:
                for f in os.listdir(folder):
                    if f.lower().endswith((".json", ".sav", ".save")):
                        count += 1
                        full = os.path.join(folder, f)
                        m = os.path.getmtime(full)
                        if newest is None or m > newest[0]:
                            newest = (m, os.path.splitext(f)[0])
            except OSError:
                pass
        return newest, count

    def make_avatar(self, size=88):
        S = size * 4
        pic = None
        if self.settings.get("google_user") == self.user and os.path.exists(AVATAR_FILE):
            try:
                pic = ImageOps.fit(Image.open(AVATAR_FILE).convert("RGB"), (S, S), Image.LANCZOS)
            except Exception:
                pic = None
        if pic is None:     # pas de photo : pastille avec l'initiale
            pic = Image.new("RGB", (S, S), hex_rgb(self.pal["panel_alt"]))
            d = ImageDraw.Draw(pic)
            f = _title_font(find_asset("fonts", "SairaStencilOne-Regular.ttf"), int(S * 0.5))
            ini = (self.user or "?")[:1].upper()
            bb = d.textbbox((0, 0), ini, font=f)
            d.text(((S - (bb[2] - bb[0])) / 2 - bb[0], (S - (bb[3] - bb[1])) / 2 - bb[1]), ini, font=f,
                   fill=hex_rgb(self.pal["accent"]))
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=255)
        out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        out.paste(pic, (0, 0), mask)
        ImageDraw.Draw(out).ellipse([3, 3, S - 4, S - 4], outline=hex_rgb(self.pal["accent"]) + (255,),
                                    width=max(2, S // 22))
        return out.resize((size, size), Image.LANCZOS)

    # ----- connexion / compte --------------------------------------------- #
    def open_auth(self, callback):
        self.pending_auth = callback
        self.auth_mode = "login"
        self.auth_msg = None
        self.show_panel(self.build_auth, side=True)

    def build_auth(self, ui):
        p, t = self.pal, self.t
        ui.title(t("auth_title"))

        if self.user:
            ui.avatar(self.make_avatar(88))
            ui.label(t("logged_as").format(self.user), self.body(14, True), "text", pad=(0, 14))
            prof = load_json(PROFILES_FILE, {}).get(self.profile_key(), {})
            newest, count = self.last_save_info()
            last = (f"{newest[1]}  ·  {datetime.fromtimestamp(newest[0]):%d/%m/%Y %H:%M}"
                    if newest else t("profile_none"))
            ui.infobox([(t("profile_playtime"), fmt_duration(prof.get("playtime", 0))),
                        (t("profile_last"), last), (t("profile_saves"), str(count))])
            ui.button(t("logout"), self.logout, self.font(13), width=30)
            ui.button(t("back"), self.cancel_panel, self.font(13), width=30, pad=(0, 0))
            return

        hero = dict(p, panel=p["accent"], text=p["panel"], accent=p["text"])      # bouton plein, bien visible
        ui.button("G    " + t("google"), self.google_login, self.font(15), width=30, pal=hero, pady=16, pad=(0, 10))
        ui.label(t("google_hint"), self.body(11), "muted", wrap=360, pad=(0, 6))
        if self.auth_msg is None:
            ui.label("", self.body(11), "muted", wrap=360, pad=(4, 8), minlines=1)
        else:
            key, kind = self.auth_msg
            ui.label(t(key), self.body(11), {"err": "err", "ok": "ok"}.get(kind, "muted"), wrap=360, pad=(4, 8),
                     minlines=1)

        if not self.show_local:       # par defaut : seulement Google. Le compte local est replie.
            ui.link(t("local_account"), lambda: self.toggle_local(True))
            ui.button(t("back"), self.cancel_panel, self.font(13), width=30, pad=(0, 0))
            return

        ui.sep_or(t("or"))
        ui.tabs([("login", t("login")), ("create", t("create"))], self.auth_mode, self.set_auth_mode)

        def field(label, id, secret=False):
            ui.label(label, self.body(11), "muted", align="w", pad=(6, 2))
            ui.entry(id, secret=secret, on_submit=self.submit_auth)

        field(t("username"), "e_user")
        field(t("password"), "e_pw", True)
        if self.auth_mode == "create":
            field(t("repeat"), "e_pw2", True)
        if self.ps.focus is None:
            self.ps.focus = "e_user"
        ui.spacer(8)
        ui.button(t(self.auth_mode), self.submit_auth, self.font(13), width=30)
        ui.button(t("back"), self.cancel_panel, self.font(13), width=30, pad=(0, 0))

    def toggle_local(self, show):
        self.show_local = show
        self.auth_msg = None
        self.refresh_panel()

    def set_auth_mode(self, mode):
        self.auth_mode = mode
        self.auth_msg = None
        self.refresh_panel()

    def set_auth_msg(self, key, kind="err"):
        self.auth_msg = (key, kind)
        if self.panel_builder == self.build_auth:
            self.refresh_panel()

    def submit_auth(self):
        if self.ps is None or self.panel_builder != self.build_auth:
            return
        user, pw = self.ps.text.get("e_user", "").strip(), self.ps.text.get("e_pw", "")
        accounts = load_json(ACCOUNTS_FILE, {})
        key = user.lower()

        if self.auth_mode == "create":
            pw2 = self.ps.text.get("e_pw2", "")
            if not user or not pw or not pw2:
                return self.set_auth_msg("err_fill")
            if pw != pw2:
                return self.set_auth_msg("err_mismatch")
            if len(pw) < 6:
                return self.set_auth_msg("err_short")
            if key in accounts:
                return self.set_auth_msg("err_exists")
            salt, h = hash_pw(pw)
            accounts[key] = {"name": user, "salt": salt, "hash": h}
            save_json(ACCOUNTS_FILE, accounts)
            self.on_login_success(user)
        else:
            if not user or not pw:
                return self.set_auth_msg("err_fill")
            acc = accounts.get(key)
            if not acc or not hmac.compare_digest(hash_pw(pw, acc["salt"])[1], acc["hash"]):
                return self.set_auth_msg("err_creds")
            self.on_login_success(acc.get("name", user))

    def on_login_success(self, name, remember=False):
        self.user = name
        self.next_track()           # nouvelle ambiance a la connexion
        if remember:
            self.settings["google_user"] = name
        else:
            self.settings.pop("google_user", None)
        self.save_settings()
        callback, self.pending_auth = self.pending_auth, None
        self.close_panel()
        self.show_menu(self.menu_name, animate=False)
        if callback:
            callback()

    def logout(self):
        self.user = None
        self.settings.pop("google_user", None)
        self.save_settings()
        try:
            os.remove(TOKEN_PATH)                  # vraie deconnexion : le prochain clic redemande le compte
        except OSError:
            pass
        self.close_panel()
        self.show_menu("main", animate=False)

    # ----- Google ---------------------------------------------------------- #
    def google_login(self):
        if self.google_busy:                       # une connexion est deja en cours
            return self.set_auth_msg("google_wait", "info")
        if not os.path.exists(TOKEN_PATH) and not find_google_secret():
            self.g_msg = None
            self.show_panel(self.build_google_setup, side=True)      # "as-tu le fichier ?" : choisir / obtenir
            return
        self.google_busy = True
        self.set_auth_msg("google_wait", "info")
        threading.Thread(target=self._google_worker, daemon=True).start()

    def _google_profile_login(self, creds):
        name, pic = google_profile(creds)
        if pic:
            try:
                raw = urllib.request.urlopen(pic, timeout=10).read()
                Image.open(io.BytesIO(raw)).convert("RGB").save(AVATAR_FILE)
            except Exception:
                pass
        return name

    def try_auto_login(self):
        """Au demarrage : reconnexion silencieuse avec token.json, sans navigateur."""
        if not self.settings.get("google_user"):
            return
        def worker():
            try:
                creds = load_cached_credentials()
                if not creds:
                    raise ValueError("no token")
                name = self._google_profile_login(creds)
                self.jobs.put(lambda: setattr(self, "user", name))
            except Exception as e:
                log(f"reconnexion Google : {e!r}")
        threading.Thread(target=worker, daemon=True).start()

    def _google_worker(self):
        try:
            if not load_cached_credentials():
                try:
                    socket.create_connection(("accounts.google.com", 443), timeout=5).close()
                except OSError:
                    self.jobs.put(lambda: self.set_auth_msg("google_offline"))
                    return
            try:
                import google_auth_oauthlib.flow  # noqa: F401
            except ImportError:
                if FROZEN:
                    raise
                self.jobs.put(lambda: self.set_auth_msg("google_installing", "info"))
                subprocess.run([sys.executable, "-m", "pip", "install", "google-auth-oauthlib"],
                               capture_output=True, timeout=900)
                importlib.invalidate_caches()
                import google_auth_oauthlib.flow  # noqa: F401
            self.jobs.put(lambda: self.set_auth_msg("google_wait", "info"))
            creds = google_login(self.t("google_done"))
            name = self._google_profile_login(creds)
            self.jobs.put(lambda: self.on_login_success(name, remember=True))
        except CredentialsNotFound:
            def need_file():
                self.g_msg = None
                self.show_panel(self.build_google_setup, side=True)
            self.jobs.put(need_file)
        except ImportError:
            self.jobs.put(lambda: self.set_auth_msg("google_nomodule"))
        except OSError as e:                      # reseau coupe / lent / DNS...
            log(f"google (reseau) : {e!r}")
            self.jobs.put(lambda: self.set_auth_msg("google_offline"))
        except Exception as e:
            log(f"google : {e!r}")
            slow = "timeout" in (type(e).__name__ + str(e)).lower()
            self.jobs.put(lambda: self.set_auth_msg("google_timeout" if slow else "google_err"))
        finally:
            self.jobs.put(lambda: setattr(self, "google_busy", False))

    # ----- musique etouffee (filtre passe-bas) quand un panneau est ouvert --------------------- #
    def set_muffle(self, on):
        self.muffle_target = 1.0 if on else 0.0

    def muffle_update(self, dt):
        cur, tgt = self.muffle, self.muffle_target
        if cur != tgt:
            step = dt / (0.45 if tgt > cur else 1.3)       # baisse rapide, remontee lente et douce
            cur = min(tgt, cur + step) if tgt > cur else max(tgt, cur - step)
            self.muffle = cur
            self._muffle_dirty = True
        if self._muffle_dirty:
            self._muffle_dirty = False
            self.muffle_apply()

    def muffle_apply(self):
        pg = self.pygame
        if pg is None:
            return
        try:
            ch = self.muffle_chan
            if ch is not None and not ch.get_busy():
                ch = self.muffle_chan = None
            m = self.muffle if ch is not None else 0.0
            v = self.settings.get("volume", 50) / 100 * (1.0 - 0.35 * self.muffle)      # ducking : -35 % au maximum
            if pg.mixer.music.get_busy():
                pg.mixer.music.set_volume(v * (1 - m))
            if ch is not None:
                ch.set_volume(v * m * 0.85)
        except Exception:
            pass

    def muffle_prepare(self, pg, path):
        """Prepare en arriere-plan une copie filtree (passe-bas ~650 Hz) du morceau qui demarre."""
        self.muffle_stop(0)
        gen, t0, token = self.music_gen, time.time(), object()
        self._muffle_id = token

        def work():
            try:
                snd = pg.mixer.Sound(path)
                arr = pg.sndarray.array(snd)
                n, rate = arr.shape[0], pg.mixer.get_init()[0]
                if n > rate * 60 * 8:                           # morceau trop long : on ne filtre pas
                    return
                x = arr.astype(np.float32)
                if x.ndim == 1:
                    x = x[:, None]
                spec = np.fft.rfft(x, axis=0)
                f = np.fft.rfftfreq(n, 1.0 / rate)
                h = 1.0 / np.sqrt(1.0 + (f / 650.0) ** 4)       # Butterworth ordre 2, sans dephasage
                y = np.fft.irfft(spec * h[:, None], n=n, axis=0)
                y = np.clip(y, -32768, 32767).astype(np.int16)
                y = y[int((time.time() - t0 + 0.05) * rate):]      # le morceau a deja demarre : on rattrape
                if len(y) < rate or self._muffle_id is not token or gen != self.music_gen:
                    return
                if arr.ndim == 1:
                    y = y[:, 0]
                s2 = pg.sndarray.make_sound(np.ascontiguousarray(y))
                s2.set_volume(0.0)
                ch = s2.play()
                if ch is None or self._muffle_id is not token:
                    return
                self.muffle_snd, self.muffle_chan = s2, ch
                self._muffle_dirty = True
            except Exception as e:
                log(f"filtre passe-bas : {e!r}")

        threading.Thread(target=work, daemon=True).start()

    def muffle_stop(self, ms=1000):
        self._muffle_id = None
        ch, self.muffle_chan = self.muffle_chan, None
        try:
            if ch is not None:
                ch.fadeout(ms) if ms else ch.stop()
        except Exception:
            pass

    def build_google_setup(self, ui):
        t = self.t
        ui.title(t("g_title"))
        ui.label(t("g_steps"), self.body(12), "text", wrap=400, align="w", pad=(0, 16))
        ui.button(t("g_open"), lambda: webbrowser.open(GOOGLE_CONSOLE_URL), self.font(12), width=30)
        ui.button(t("g_pick"), self.pick_google_secret, self.font(12), width=30)
        ui.label(self.g_msg or "", self.body(11), "err", wrap=380, pad=(4, 8), minlines=1)
        ui.button(t("back"), lambda: self.show_panel(self.build_auth, side=True), self.font(12), width=30,
                  pad=(0, 0))

    def pick_google_secret(self):
        path = ""
        try:     # simple boite de dialogue de fichier (Tk n'est utilise que pour ca)
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            try:
                path = filedialog.askopenfilename(title="client_secret.json", filetypes=[("JSON", "*.json")])
            finally:
                root.destroy()
        except Exception as e:
            log(f"selecteur de fichier : {e!r}")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "installed" not in data:
                raise ValueError("not a desktop client")
            shutil.copyfile(path, os.path.join(DATA_DIR, "client_secret.json"))
        except Exception:
            self.g_msg = self.t("g_badfile")
            self.refresh_panel()
            return
        self.auth_msg = ("g_saved", "ok")
        self.show_panel(self.build_auth, side=True)
        self.google_login()                       # nouvelle tentative de connexion

    def toast(self, text):
        p, spec = self.pal, self.body(13, True)
        self.remove_tag("toast")
        lh = self.skin.lh(spec)
        w, h = int(self.skin.width(text, spec)) + 44, lh + 24
        im = Image.new("RGBA", (w, h), p["accent"])
        d = ImageDraw.Draw(im)
        d.rectangle([2, 2, w - 3, h - 3], fill=p["panel"])
        self.skin.draw_text(d, w / 2, (h - lh) / 2, text, spec, 1.0, p["text"], "c")
        self.add(Sprite(im, self.W / 2, self.H - 50, z=70, tag="toast"))
        self.after(2600, lambda: self.remove_tag("toast"))


    # ----- lancement du jeu ------------------------------------------------ #
    
    def launch_game(self, mode, save=None):
        """Lance le jeu sans rouvrir le menu."""

        label = f"{mode} / {os.path.basename(save) if save else 'new'}"
        self.toast(self.t("launching").format(label))
        self.play_sfx("launch")
        self.fade_out_music(1800)

        try:
            project_root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            signal_file = os.path.join(
             tempfile.gettempdir(),
             f"last_signal_connected_{os.getpid()}.txt",
             ) 
            if os.path.exists(signal_file):
                os.remove(signal_file)
            cmd = [
            sys.executable,
            "-m",
            "client_python.game_launcher",
            "--mode", mode,
            "--signal-file", signal_file,
            ]

            if save:
                cmd += ["--save", save]

            proc = subprocess.Popen(cmd, cwd=project_root)
            

            threading.Thread(
            target=self._watch_game,
            args=(proc, time.time(),signal_file),
            daemon=True,
            ).start()
            
            

        except Exception as e:
            log(f"lancement du jeu : {e!r}")

            self.after(4200, self.restore_music)   # aucun jeu branche : on remet la musique

    
    def _watch_game(self, proc, t0, signal_file):
        menu_closed = False

        while proc.poll() is None:
            if os.path.exists(signal_file) and not menu_closed:
                menu_closed = True

                def close_menu():
                    if hasattr(self, "stop") and callable(self.stop):
                        self.stop()
                    elif hasattr(self, "destroy") and callable(self.destroy):
                        self.destroy()
                    elif hasattr(self, "root") and hasattr(self.root, "destroy"):
                        self.root.destroy()

                self.jobs.put(close_menu)

            time.sleep(0.1)

        secs = time.time() - t0

        def finish():
            self.add_playtime(secs)
            self.restore_music()

        self.jobs.put(finish)

        if os.path.exists(signal_file):
            os.remove(signal_file)



# --------------------------------------------------------------------------- #
#  Installation au premier lancement (dossier du jeu, fichiers, modules)
# --------------------------------------------------------------------------- #
BUNDLED = ("background.jpg", "background.png", "icon.png", "icon.ico", "ambient.wav", "client_secret.json")


def run_setup(report, tr):
    """report(pourcentage, message). Cree le dossier du jeu, copie les fichiers de l'exe, installe les modules."""
    report(4, tr("setup_folder"))
    for sub in ("solo", "multi"):
        os.makedirs(os.path.join(SAVES_DIR, sub), exist_ok=True)

    if FROZEN:  # l'exe contient tout : on deploie les fichiers dans le dossier du jeu
        report(10, tr("setup_files"))
        stamp = os.path.join(DATA_DIR, "version.txt")
        try:
            update = open(stamp).read().strip() != APP_VERSION
        except OSError:
            update = True
        files = [(n, n) for n in BUNDLED if os.path.exists(os.path.join(RES_DIR, n))]
        for folder in ("fonts", "music", "sfx", "locales", "backgrounds"):
            src = os.path.join(RES_DIR, folder)
            if os.path.isdir(src):
                files += [(os.path.join(folder, f), f) for f in sorted(os.listdir(src))]
        for i, (rel, _) in enumerate(files):
            dst = os.path.join(DATA_DIR, rel)
            if update or not os.path.exists(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(os.path.join(RES_DIR, rel), dst)
            report(10 + 60 * (i + 1) / max(1, len(files)), tr("setup_files"))
        with open(stamp, "w") as f:
            f.write(APP_VERSION)
    else:       # script .py : on installe ce qui manque
        report(30, tr("setup_files"))
        for mod, pipname in (("pygame", "pygame-ce"), ("google_auth_oauthlib", "google-auth-oauthlib")):
            try:
                importlib.import_module(mod)
            except ImportError:
                report(50, tr("setup_deps").format(pipname))
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "--only-binary=:all:", pipname],
                                   capture_output=True, timeout=900)
                    importlib.invalidate_caches()
                except Exception:
                    pass
    report(100, tr("setup_ready"))




