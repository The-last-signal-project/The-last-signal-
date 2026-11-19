#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE LAST SIGNAL - Menu principal (version VisPy)
Moteur graphique OpenGL avec VisPy et GLFW, habillage sonore et gestion des comptes.
Intègre la sélection parmi les 13 classes de personnage du jeu via des boutons interactifs.
"""
import os
import sys
import json
import math
import time
import queue
import random
import socket
import shutil
import colorsys
import importlib
import threading
import subprocess
import tempfile
from datetime import datetime

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
FROZEN = getattr(sys, "frozen", False)

_HERE = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))
CRASH_FILE = os.path.join(_HERE, "erreur.log")

def _report_crash(exc_type, exc, tb):
    import traceback
    txt = "".join(traceback.format_exception(exc_type, exc, tb))
    head = f"[{datetime.now():%d/%m/%Y %H:%M:%S}] Python {sys.version.split()} - {sys.platform}\n"
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
                0, f"{head}\n{txt[-1500:]}\nDétails complets : {CRASH_FILE}", "The Last Signal - Erreur", 0x10)
        except Exception:
            pass

sys.excepthook = _report_crash
threading.excepthook = lambda a: _report_crash(a.exc_type, a.exc_value, a.exc_traceback)

REQUIRED = (("PIL", "pillow", "12.0"), ("numpy", "numpy", "2.3.4"), ("glfw", "glfw", "2.10"),
            ("vispy", "vispy", "0.16.1"))

def _vtuple(v):
    out = []
    for part in str(v).split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out)

def _pip_install(spec):
    last = ""
    for extra in (["--only-binary=:all:"], []):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", *extra, spec],
                           capture_output=True, text=True, timeout=900)
        if r.returncode == 0:
            importlib.invalidate_caches()
            return
        last = (r.stdout or "")[-600:] + (r.stderr or "")[-900:]
    raise RuntimeError(f"Impossible d'installer {spec} : \n{last}")

def _ensure_modules():
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

from . import auth_session as net_proto

RES_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
EXE_DIR = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))
APP_NAME = "The Last Signal"
APP_VERSION = "4"

# Liste officielle des 13 classes du jeu
AVAILABLE_CLASSES = [
    "Mage", "Nécromancien", "Épéiste", "Chevalier lourd", "Chevalier",
    "Soldat d'infanterie", "Soldat de cavalerie", "Gendarme",
    "Force spéciale d'intervention", "Voleur", "Assassin", "Sorcier", "Archer"
]

def default_install_dir():
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, APP_NAME)

DATA_DIR = default_install_dir() if FROZEN else EXE_DIR
SAVES_DIR = os.path.join(DATA_DIR, "saves")
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")
LOG_FILE = os.path.join(DATA_DIR, "journal.log")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
APP_ID = "TheLastSignal.Menu"
SERVER_ADDR = ("", 0)
MAX_TRACK_SECONDS = 60
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
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
    return os.path.join(project_dirs[13], "assets", *parts)

BG_EXTS = (".jpg", ".jpeg", ".png", ".webp")

def list_backgrounds():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_dir, "assets")
    bases = (DATA_DIR, RES_DIR, assets_dir)
    found = []
    for base in bases:
        for name in ("background.jpg", "background.jpeg", "background.png", "background.webp"):
            path = os.path.join(base, name)
            if os.path.isfile(path):
                found.append(path)
        folder = os.path.join(base, "backgrounds")
        if os.path.isdir(folder):
            for name in sorted(os.listdir(folder)):
                path = os.path.join(folder, name)
                if os.path.isfile(path) and name.lower().endswith(BG_EXTS):
                    found.append(path)
    unique, seen = [], set()
    for path in found:
        key = os.path.normcase(os.path.abspath(path))
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique

def find_background(settings=None):
    cands = list_backgrounds()
    if not cands:
        return find_asset("background.png")
    if settings is None:
        return cands
    names = {os.path.basename(p): p for p in cands}
    seen = [n for n in settings.get("bg_seen", []) if n in names]
    fresh = [n for n in names if n not in seen and n != settings.get("last_bg")]
    if not fresh:
        seen = []
        fresh = [n for n in names if n != settings.get("last_bg")] or list(names)
    choice = random.choice(fresh)
    settings["last_bg"], settings["bg_seen"] = choice, seen + [choice]
    return names[choice]

def find_playlist():
    exts = (".ogg", ".mp3", ".wav")
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_dir, "assets")
    bases = (DATA_DIR, RES_DIR, assets_dir)
    for base in bases:
        folder = os.path.join(base, "music")
        if os.path.isdir(folder):
            tracks = [
                os.path.join(folder, f)
                for f in sorted(os.listdir(folder))
                if f.lower().endswith(exts) and os.path.isfile(os.path.join(folder, f))
            ]
            if tracks:
                return tracks
    for base in bases:
        for ext in exts:
            path = os.path.join(base, "music" + ext)
            if os.path.isfile(path):
                return [path]
    path = find_asset("ambient.wav")
    return [path] if os.path.isfile(path) else []

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

BASE_TR = {
    "fr": {
        "_name": "Français",
        "account": "Compte", "auth_title": "Compte", "back": "Retour", "close": "Fermer", "confirm": "Confirmer",
        "confirm_delete": "Supprimer la sauvegarde « {} » ?", "create": "Créer un compte",
        "credits": "Remerciements", "credits_title": "Remerciements", "delete": "Supprimer",
        "err_creds": "Identifiant ou mot de passe incorrect.", "err_exists": "Cet identifiant existe déjà.",
        "err_fill": "Remplis tous les champs.", "err_mismatch": "Les mots de passe ne correspondent pas.",
        "err_short": "Mot de passe trop court (6 caractères minimum).", "fullscreen": "Plein écran",
        "language": "Langue", "launching": "Lancement : {}", "load_save": "Charger une sauvegarde",
        "logged_as": "Connecté : {}", "login": "Connexion", "logout": "Se déconnecter", "multi": "Multijoueur",
        "net_off": "Hors ligne", "net_on": "En ligne", "new_multi": "Nouvelle partie", "new_solo": "Nouvelle partie",
        "no": "Non", "no_saves": "Aucune sauvegarde", "or": "ou", "password": "Mot de passe", "play": "Jouer",
        "profile_last": "Dernière sauvegarde", "profile_none": "Aucune", "profile_playtime": "Temps de jeu",
        "profile_saves": "Sauvegardes", "quit": "Quitter", "repeat": "Répéter le mot de passe",
        "resolution": "Résolution", "role_dev": "Développeur", "role_lead": "Directeur du projet et développeur",
        "saves_title": "Sauvegardes", "settings_title": "Paramètres", "setup_deps": "Installation de {}…",
        "setup_files": "Copie des fichiers du jeu…", "setup_folder": "Création du dossier du jeu…",
        "setup_ready": "Prêt !", "solo": "Solo",
        "thanks": "Un grand merci à toutes celles et ceux qui ont rendu ce jeu possible.",
        "username": "Identifiant", "volume": "Volume", "yes": "Oui",
        "menu_login": "Se connecter", "menu_signup": "S'enregistrer", "signup_title": "Inscription",
        "email": "Adresse e-mail", "pick_account": "Sélectionner un compte", "new_account": "Créer un nouveau compte",
        "change_account": "Changer de compte", "accounts_title": "Mes comptes", "account_name": "Nom du compte",
        "create_short": "Créer", "choose_account": "Choisir ce compte", "no_accounts": "Aucun compte pour le moment.",
        "profile_account": "Compte", "net_wait": "Communication avec le serveur…", "game_failed": "Le jeu n'a pas pu démarrer.",
        "err_pw_short": "Mot de passe trop court (8 caractères minimum).", "err_email": "Adresse e-mail invalide.",
        "err_email_used": "Cette adresse e-mail est déjà utilisée.", "err_banned_perm": "Ce compte est banni définitivement.",
        "err_banned_temp": "Ce compte est temporairement banni.", "err_locked": "Trop de tentatives : compte bloqué temporairement.",
        "err_already": "Ce compte est déjà connecté.", "srv_unreachable": "Serveur injoignable.",
        "srv_timeout": "Le serveur ne répond pas.", "srv_error": "Erreur serveur.", "srv_lost": "Connexion au serveur perdue.",
        "srv_busy": "Patiente un instant…", "pseudo": "Pseudo", "err_pseudo": "Pseudo invalide (3 à 20 caractères).",
        "err_pseudo_used": "Ce pseudo est déjà utilisé.", "creating": "Création en cours…", "logging_in": "Connexion en cours…",
    }
}

EXTRA_TR = {
    "fr": {
        "gl_on": "Effet glitch : OUI", "gl_off": "Effet glitch : NON",
        "crt_on": "Effet CRT : OUI", "crt_off": "Effet CRT : NON",
        "controls": "Contrôles", "controls_title": "Contrôles",
        "c_action": "Action", "c_keyboard": "Clavier", "c_gamepad": "Manette",
        "c_reset": "Valeurs par défaut", "c_press_key": "Appuie sur une touche…",
        "c_press_btn": "Appuie sur un bouton…", "c_hint": "Clique sur une case...",
        "c_pad_none": "Aucune manette détectée", "c_pad_ok": "Manette détectée : {}",
        "act_up": "Avancer", "act_down": "Reculer", "act_left": "Aller à gauche", "act_right": "Aller à droite",
        "act_sprint": "Courir", "act_jump": "Sauter / Esquiver", "act_interact": "Interagir",
        "act_attack": "Attaquer", "act_aim": "Viser / Bloquer", "act_reload": "Recharger",
        "act_inventory": "Inventaire", "act_pause": "Pause",
    }
}

ACTIONS = ("up", "down", "left", "right", "sprint", "jump", "interact", "attack", "aim", "reload", "inventory", "pause")
DEFAULT_CONTROLS = {
    "keyboard": {"up": "W", "down": "S", "left": "A", "right": "D", "sprint": "LEFT_SHIFT", "jump": "SPACE",
                 "interact": "E", "attack": "MOUSE1", "aim": "MOUSE2", "reload": "R", "inventory": "TAB", "pause": "ESCAPE"},
    "gamepad": {"up": "LS_UP", "down": "LS_DOWN", "left": "LS_LEFT", "right": "LS_RIGHT", "sprint": "L3",
                "jump": "A", "interact": "X", "attack": "RT", "aim": "LT", "reload": "B", "inventory": "Y", "pause": "START"}
}

KEY_NAMES = {getattr(glfw, n): n[4:] for n in dir(glfw) if n.startswith("KEY_") and n not in ("KEY_UNKNOWN", "KEY_LAST", "KEY_MENU")}
KEY_CODES = {v: k for k, v in KEY_NAMES.items()}
PAD_BUTTONS = {glfw.GAMEPAD_BUTTON_A: "A", glfw.GAMEPAD_BUTTON_B: "B", glfw.GAMEPAD_BUTTON_X: "X",
               glfw.GAMEPAD_BUTTON_Y: "Y", glfw.GAMEPAD_BUTTON_LEFT_BUMPER: "LB", glfw.GAMEPAD_BUTTON_RIGHT_BUMPER: "RB",
               glfw.GAMEPAD_BUTTON_BACK: "BACK", glfw.GAMEPAD_BUTTON_START: "START", glfw.GAMEPAD_BUTTON_LEFT_THUMB: "L3",
               glfw.GAMEPAD_BUTTON_RIGHT_THUMB: "R3", glfw.GAMEPAD_BUTTON_DPAD_UP: "DPAD_UP",
               glfw.GAMEPAD_BUTTON_DPAD_RIGHT: "DPAD_RIGHT", glfw.GAMEPAD_BUTTON_DPAD_DOWN: "DPAD_DOWN",
               glfw.GAMEPAD_BUTTON_DPAD_LEFT: "DPAD_LEFT"}

_LABELS_FR = {"SPACE": "ESPACE", "ENTER": "ENTRÉE", "TAB": "TAB", "ESCAPE": "ÉCHAP", "BACKSPACE": "RETOUR",
              "LEFT_SHIFT": "MAJ GAUCHE", "RIGHT_SHIFT": "MAJ DROITE", "LEFT_CONTROL": "CTRL GAUCHE",
              "RIGHT_CONTROL": "CTRL DROITE", "LEFT_ALT": "ALT", "RIGHT_ALT": "ALT GR", "UP": "HAUT",
              "DOWN": "BAS", "LEFT": "GAUCHE", "RIGHT": "DROITE", "MOUSE1": "CLIC GAUCHE",
              "MOUSE2": "CLIC DROIT", "MOUSE3": "MOLETTE", "DELETE": "SUPPR"}

def bind_label(token, lang="fr"):
    if not token:
        return "—"
    if token in _LABELS_FR:
        return _LABELS_FR[token]
    if token.startswith("KP_"):
        return token.replace("KP_", "NUM ").replace("_", " ")
    code = KEY_CODES.get(token)
    if code is not None:
        try:
            name = glfw.get_key_name(code, 0)
            if name:
                return name.upper()
        except Exception:
            pass
    return token.replace("_", " ")

def get_controls(settings):
    out = {dev: dict(DEFAULT_CONTROLS[dev]) for dev in DEFAULT_CONTROLS}
    saved = settings.get("controls")
    if isinstance(saved, dict):
        for dev in out:
            if isinstance(saved.get(dev), dict):
                for act in ACTIONS:
                    if act in saved[dev] and isinstance(saved[dev][act], str):
                        out[dev][act] = saved[dev][act]
    return out

def _font_dirs():
    dirs = []
    if os.name == "nt":
        dirs += [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
                 os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")]
    elif sys.platform == "darwin":
        dirs += ["/System/Library/Fonts", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")]
    else:
        dirs += ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts")]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for folder in (script_dir, os.path.dirname(script_dir), os.path.dirname(os.path.dirname(script_dir))):
        dirs.append(os.path.join(folder, "assets", "fonts"))
    result, seen = [], set()
    for folder in dirs:
        folder = os.path.abspath(folder)
        if os.path.isdir(folder) and folder not in seen:
            seen.add(folder)
            result.append(folder)
    return result

_FONT_INDEX = {}
def find_system_font(*names):
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
    tr, names = {}, {}
    for code in BASE_TR:
        tr.setdefault(code, {})
        names.setdefault(code, BASE_TR[code]["_name"])
    for code, data in tr.items():
        for src in (BASE_TR.get(code) or BASE_TR["fr"], EXTRA_TR.get(code) or EXTRA_TR["fr"]):
            for k, v in src.items():
                if k != "_name":
                    data.setdefault(k, v)
    return {"fr": "Français"}, tr

LANGS, TR = load_locales()

def translate(lang, key):
    base = TR.get("fr") or {}
    return TR.get(lang, base).get(key) or base.get(key, key)

def hex_rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))

def mix(c1, c2, t):
    a, b = hex_rgb(c1), hex_rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def valid_pseudo(pseudo):
    return 3 <= len(pseudo) <= 20 and all(c.isalnum() or c in "_-" for c in pseudo)

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

COL_BG = "#0c0c0e"
COL_PANEL = "#1e1f24"
ACCENT = "#ff5500"

def extract_palette(img=None):
    return {
        "bg": COL_BG, "accent": ACCENT, "accent_dim": mix(COL_PANEL, ACCENT, 0.52),
        "panel": COL_PANEL, "panel_alt": "#2a2b31", "text": "#e8e8ec",
        "muted": "#8d8e98", "err": "#ff5a4d", "ok": "#7bd88f",
    }

def make_gear(size, color):
    S = size * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, teeth = S / 2, 8
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

def render_title_parts(text, font_path, px, glow, seed=7):
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

    grad = Image.linear_gradient("L").resize((W, H))
    fill = ImageOps.colorize(grad, black=(242, 228, 192), white=(150, 48, 14), mid=(232, 122, 36), midpoint=120).convert("RGBA")
    fill.putalpha(mask)

    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    core = Image.alpha_composite(core, fill)
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return halo, core

SFX_HOOK = None
def sfx(name):
    if SFX_HOOK:
        try:
            SFX_HOOK(name)
        except Exception:
            pass

VERT = """
uniform vec4 u_rect;
uniform vec2 u_view;
uniform vec4 u_uv;
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
    vec4 c = texture2D(u_tex, v_uv);
    gl_FragColor = vec4(c.rgb * u_tint * u_alpha, c.a * u_alpha);
}
"""

def hex_tint(c):
    return tuple(v / 255 for v in hex_rgb(c))

def _premult(img):
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    a = arr[..., 3:4].astype(np.uint16)
    arr[..., :3] = ((arr[..., :3].astype(np.uint16) * a + 127) // 255).astype(np.uint8)
    return np.ascontiguousarray(arr)

class Sprite:
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
    def __init__(self):
        self.prog = gloo.Program(VERT, FRAG)
        self.prog["a_pos"] = gloo.VertexBuffer(np.array([, [14]], np.float32))
        gloo.set_state(blend=True, blend_func=("one", "one_minus_src_alpha"), depth_test=False, cull_face=False)

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

class Skin:
    def __init__(self, app):
        self.app = app
        self._fonts, self._glyph, self._notdef = {}, {}, {}
        self.stencil = find_system_font("impact.ttf", "arialbd.ttf")
        self.body_reg = find_system_font("arial.ttf", "segoeui.ttf")
        self.body_bold_file = find_system_font("arialbd.ttf", "segoeuib.ttf")
        self.fallback = find_system_font("arial.ttf")

    def _load(self, path, px):
        key = (path, px)
        f = self._fonts.get(key)
        if f is None:
            try:
                f = ImageFont.truetype(path, px)
            except Exception:
                f = ImageFont.load_default(px)
            self._fonts[key] = f
        return f

    def chain(self, spec, scale=1.0):
        px = max(6, int(round(spec[14] * 4 / 3 * scale)))
        path = self.body_bold_file if spec == "b" and spec[13] else self.body_reg
        return [self._load(path or self.fallback, px)]

    def lh(self, spec, scale=1.0):
        a, d = self.chain(spec, scale).getmetrics()
        return a + d

    def zero(self, spec, scale=1.0):
        return self.chain(spec, scale).getlength("0")

    def width(self, text, spec, scale=1.0):
        f = self.chain(spec, scale)
        return f.getlength(text)

    def draw_text(self, d, x, y, text, spec, scale, fill, align="l"):
        f = self.chain(spec, scale)
        total = f.getlength(text)
        cx = x - total / 2 if align == "c" else (x - total if align == "r" else x)
        base = y + f.getmetrics()
        d.text((cx, base), text, font=f, fill=fill, anchor="ls")
        return total

    def btn_size(self, text, spec, wchars, scale=1.0, pady=11):
        w = max(int(wchars * self.zero(spec, scale)) + int(6 * scale),
                int(math.ceil(self.width((text or "").upper(), spec, scale))) + int(2 * 28 * scale))
        h = self.lh(spec, scale) + 2 * int(round(pady * scale)) + int(4 * scale)
        return w, h

    def button_image(self, text, spec, wchars, pal, state="n", scale=1.0, pady=11, k=None):
        w, h = self.btn_size(text, spec, wchars, scale, pady)
        b = max(1, int(round(2 * scale)))
        hot = state in ("h", "p")
        kk = k if k is not None else (1.0 if hot else 0.0)
        im = Image.new("RGBA", (w, h), pal["accent"])
        d = ImageDraw.Draw(im)
        dy = b if state == "p" else 0
        d.rectangle([b, b + dy, w - b - 1, h - b - 1], fill=mix(pal["panel"], pal["accent"], kk))
        lh = self.lh(spec, scale)
        self.draw_text(d, w / 2, (h - lh) / 2 + dy, (text or "").upper(), spec, scale, mix(pal["text"], pal["panel"], kk), "c")
        return im

class Btn:
    SHIFT = 8

    def __init__(self, app, text=None, command=None, spec=None, width=BTN_W, pady=11, z=10, tag="menu", slide=True):
        sk = app.skin
        self.app, self.command, self.state, self.slide = app, command, "n", slide
        self.imgs = {st: sk.button_image(text, spec, width, app.pal, st, 1.0, pady) for st in ("n", "h", "p")}
        self.sprite = Sprite(self.imgs["n"], z=z, tag=tag)
        self.hot = Sprite(self.imgs["h"], z=z + 1, tag=tag, alpha=0.0)
        w, h = self.size()
        self.bar = Sprite(app.white, z=z + 2, tag=tag, w=5, h=h, anchor="w", tint=hex_tint(app.pal["accent"]), alpha=0.0)
        self.frame = Sprite(Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0)), z=z + 3, tag=tag, alpha=0.0)
        self.t, self.focus, self.gx, self.glitch_until = 0.0, False, 0.0, 0.0

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
        target = 1.0 if (self.state in ("h", "p") or self.focus) else 0.0
        k = min(1.0, dt * 16.0)
        self.t += (target - self.t) * k
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

    def size(self):
        return self.sprite.tw, self.sprite.th

    def contains(self, x, y):
        w, h = self.size()
        return abs(x - self.sprite.x) <= w / 2 and abs(y - self.sprite.y) <= h / 2

class PanelState:
    def __init__(self):
        self.hover = self.down = self.focus = self.drag = self.capture = None
        self.text, self.caret, self.sel, self.scroll, self.val = {}, {}, {}, {}, {}
        self.t0 = time.time()
        self.last_click = (0.0, None)
        self.kfocus, self.kvis, self.hv = None, False, {}

class PanelUI:
    PADX, PADY = 38, 28

    def __init__(self, app, scale=1.0):
        self.app, self.sk, self.pal, self.s = app, app.skin, app.pal, scale
        self.els = []
        self.animated = False
        self.W = self.H = self.inner = 0

    def S(self, v):
        return max(1, int(round(v * self.s))) if v else 0

    def P(self, pad):
        return (self.S(pad), self.S(pad[14]))

    def _add(self, kind, nw, nh, pad=(0, 0), fill=False, id=None, **kw):
        e = dict(kind=kind, nw=nw, nh=nh, pad=self.P(pad), fill=fill, id=id or f"e{len(self.els)}", **kw)
        self.els.append(e)
        return e

    def title(self, text, size=20, gap=16):
        spec = self.app.font(size)
        self._add("label", self.sk.width(text.upper(), spec, self.s), self.sk.lh(spec, self.s), text=text.upper(),
                  spec=spec, color="accent", align="c", lines=[text.upper()])
        self._add("rule", 0, self.S(2), pad=(8, gap), fill=True)

    def label(self, text, spec=None, color="text", align="c", pad=(0, 0), id=None):
        spec = spec or self.app.body(11)
        lh = self.sk.lh(spec, self.s)
        nw = self.sk.width(text, spec, self.s)
        return self._add("label", nw, lh, pad=pad, fill=(align == "w"), id=id, text=text, spec=spec, color=color, align=align, lines=[text])

    def button(self, text, command, spec, width=BTN_W, pal=None, pad=(0, 8), pady=11, id=None):
        pal = pal or self.pal
        w, h = self.sk.btn_size(text, spec, width, self.s, pady)
        return self._add("button", w, h, pad=pad, id=id, text=text, spec=spec, width=width, bpal=pal, pady=pady, command=command)

    def entry(self, id, secret=False, on_submit=None, width=34, pad=(0, 0)):
        spec = self.app.body(13)
        w = int(width * self.sk.zero(spec, self.s)) + self.S(12)
        return self._add("entry", w, self.sk.lh(spec, self.s) + self.S(24), pad=pad, fill=True, id=id, spec=spec, secret=secret, on_submit=on_submit)

    def listbox(self, id, items, on_activate, rows=8, width=40, pad=(0, 16)):
        spec = self.app.body(13)
        rowh = self.sk.lh(spec, self.s) + self.S(5)
        w = int(width * self.sk.zero(spec, self.s)) + self.S(8)
        return self._add("list", w, rows * rowh + self.S(4), pad=pad, id=id, spec=spec, items=items, rows=rows, rowh=rowh, on_activate=on_activate)

    def spacer(self, h):
        self._add("spacer", 0, self.S(h))

    def progress(self, text, width=300, pad=(4, 12)):
        self.animated = True
        self.label(text, self.app.body(12), "accent", pad=(4, 8))
        return self._add("progress", self.S(width), self.S(10), pad=pad)

    def finish(self):
        for e in self.els:
            e["nw"], e["nh"] = int(math.ceil(e["nw"])), int(math.ceil(e["nh"]))
        self.inner = max([e["nw"] for e in self.els] or [15])
        y = 2 + self.S(self.PADY)
        for e in self.els:
            y += e["pad"]
            e["y"], e["h"] = y, e["nh"]
            y += e["nh"] + e["pad"][14]
            e["w"] = self.inner if e["fill"] else e["nw"]
            e["x"] = 2 + self.S(self.PADX) + (self.inner - e["w"]) // 2
        self.H = y + self.S(self.PADY) + 2
        self.W = self.inner + 2 * self.S(self.PADX) + 4

    def hit(self, lx, ly):
        for e in self.els:
            if e["kind"] in ("rule", "spacer", "label"):
                continue
            if e["x"] <= lx < e["x"] + e["w"] and e["y"] <= ly < e["y"] + e["h"]:
                return e, 0
        return None

    def render(self, ps, now):
        p = self.pal
        im = Image.new("RGBA", (self.W, self.H), p["accent"])
        d = ImageDraw.Draw(im)
        d.rectangle([2, 2, self.W - 3, self.H - 3], fill=p["panel"])
        for e in self.els:
            fn = getattr(self, "_draw_" + e["kind"], None)
            if fn:
                fn(im, d, e, ps, now)
        return im

    def _draw_label(self, im, d, e, ps, now):
        lh = self.sk.lh(e["spec"], self.s)
        for i, line in enumerate(e["lines"]):
            col = self.pal.get(e["color"], e["color"])
            self.sk.draw_text(d, e["x"] + e["w"] / 2, e["y"] + i * lh, line, e["spec"], self.s, col, "c")

    def _draw_rule(self, im, d, e, ps, now):
        d.rectangle([e["x"], e["y"], e["x"] + e["w"] - 1, e["y"] + e["h"] - 1], fill=self.pal["accent_dim"])

    def _draw_spacer(self, im, d, e, ps, now):
        pass

    def _draw_button(self, im, d, e, ps, now):
        hov = ps.hover and ps.hover == e["id"]
        down = ps.down and ps.down == e["id"] and hov
        st = "p" if down else ("h" if hov else "n")
        k = ps.hv.get(e["id"], 1.0 if hov else 0.0)
        im.alpha_composite(self.sk.button_image(e["text"], e["spec"], e["width"], e["bpal"], st, self.s, e["pady"], k=1.0 if down else k), (e["x"], e["y"]))

    def _draw_entry(self, im, d, e, ps, now):
        p, x, y, w, h = self.pal, e["x"], e["y"], e["w"], e["h"]
        focus = ps.focus == e["id"]
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=p["accent"] if focus else p["panel_alt"])
        raw = ps.text.get(e["id"], "")
        lh = self.sk.lh(e["spec"], self.s)
        self.sk.draw_text(d, x + 6, y + (h - lh) / 2, raw, e["spec"], self.s, p["text"], "l")

    def _draw_list(self, im, d, e, ps, now):
        p, x, y, w, h = self.pal, e["x"], e["y"], e["w"], e["h"]
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=p["panel_alt"])
        sel = ps.sel.get(e["id"], 0)
        for i in range(e["rows"]):
            if i >= len(e["items"]):
                break
            ry = y + i * e["rowh"]
            if i == sel:
                d.rectangle([x, ry, x + w - 1, ry + e["rowh"] - 1], fill=p["accent"])
            self.sk.draw_text(d, x + 4, ry + 2, e["items"][i], e["spec"], self.s, p["panel"] if i == sel else p["text"], "l")

class App:
    def __init__(self):
        self.settings = load_json(SETTINGS_FILE, {})
        self.lang = self.settings.get("lang", "fr")
        self.user = self.account = self.net = self._cred = self.accounts = None
        self.net_busy = False
        self.busy_text = "net_wait"
        self.launching = self.in_flow = False
        self._resume = None
        self.jobs = queue.Queue()
        self.panel = self.panel_builder = self.ps = self.panel_ui = None
        self.panel_closable = True
        self.panel_mode = "center"
        self.menu_name = "main"
        self.menu_buttons = []
        self.auth_mode = "login"
        self.auth_msg = None
        self.selected_class = None
        self.fullscreen = False
        self._t_start = self._t_last = time.time()
        self.sprites, self.anims, self._timers = [], [], []
        self._after_id = 0
        self.r = None

        self.vapp = vapp.use_app("glfw")
        self.W, self.H = 1280, 720
        self.canvas = vapp.Canvas(title=APP_NAME, size=(self.W, self.H), show=False, resizable=True, vsync=True, app=self.vapp)
        self.win = getattr(self.canvas._backend, "_id", None)

        glfw.set_key_callback(self.win, self._glfw_key)
        glfw.set_char_callback(self.win, self._glfw_char)
        glfw.set_mouse_button_callback(self.win, self._glfw_mouse)
        glfw.set_cursor_pos_callback(self.win, self._glfw_cursor)
        glfw.set_window_close_callback(self.win, self._glfw_close)

        self.canvas.events.draw.connect(self.on_draw)

        self.bg_src = Image.new("RGB", (1280, 720), (26, 22, 20))
        self.pal = extract_palette(self.bg_src)
        self.skin = Skin(self)
        self.white = Image.new("RGBA", (2, 2), (255, 255, 255, 255))
        self.bg_sprite = self.add(Sprite(ImageOps.fit(self.bg_src, (self.W, self.H), Image.LANCZOS), 0, 0, anchor="nw", z=0))

        self.show_menu("main")

    def t(self, key):
        return translate(self.lang, key)

    def font(self, size):
        return ("t", size, False)

    def body(self, size, bold=False):
        return ("b", size, bool(bold))

    def menu_x(self):
        return max(215, int(self.W * 0.2))

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

    def animate(self, dur, fn, done=None):
        self.anims.append([time.time(), dur, fn, done])

    def run(self):
        self.canvas.show()
        while getattr(self, "running", True):
            t0 = time.time()
            self.tick()
            self.canvas.update()
            self.vapp.process_events()
            time.sleep(0.008)

    def destroy(self):
        self.running = False

    def tick(self):
        now = time.time()
        try:
            while True:
                self.jobs.get_nowait()()
        except queue.Empty:
            pass

        due = sorted(t for t in self._timers if t <= now)
        if due:
            self._timers = [t for t in self._timers if t > now]
            for _, _, fn in due:
                fn()

        dt = max(0.0, min(0.1, now - self._t_last))
        self._t_last = now
        for b in self.menu_buttons:
            b.update(dt)

        if getattr(self, "panel_dirty", False) and self.panel and self.panel_ui:
            self.panel_dirty = False
            self.panel.set_image(self.panel_ui.render(self.ps, now))

    def on_draw(self, ev):
        if self.r is None:
            self.r = Renderer()
        gloo.set_viewport(0, 0, self.W, self.H)
        gloo.clear((0.05, 0.05, 0.05, 1.0))
        for sp in sorted(self.sprites, key=lambda s: s.z):
            self.r.draw(sp, self.W, self.H)

    def _glfw_close(self, win):
        self.destroy()

    def _glfw_key(self, win, key, scancode, action, mods):
        name = KEY_NAMES.get(key)
        if name and action == glfw.PRESS:
            if name == "ESCAPE":
                self.close_panel()

    def _glfw_char(self, win, cp):
        pass

    def _glfw_cursor(self, win, x, y):
        self.mx, self.my = x, y
        for b in self.menu_buttons:
            if b.contains(x, y):
                b.set_state("h")
            else:
                b.set_state("n")

    def _glfw_mouse(self, win, button, action, mods):
        if action == glfw.PRESS:
            for b in self.menu_buttons:
                if b.contains(self.mx, self.my):
                    b.set_state("p")
                    if b.command:
                        b.command()
            if self.panel and self.panel_ui:
                ox, oy = self.panel.x - self.panel.tw / 2, self.panel.y - self.panel.th / 2
                h = self.panel_ui.hit(self.mx - ox, self.my - oy)
                if h and h["kind"] == "button":
                    h["command"]()

    def show_panel(self, builder, side=True):
        self.close_panel()
        self.panel_builder = builder
        self.ps = PanelState()
        self.panel = self.add(Sprite(None, 0, 0, z=50, tag="panel"))
        self.rebuild_panel()

    def rebuild_panel(self):
        if not self.panel_builder:
            return
        ui = PanelUI(self, 1.0)
        self.panel_builder(ui)
        ui.finish()
        self.panel_ui = ui
        self.panel.x, self.panel.y = self.W * 0.7, self.H * 0.5
        self.panel.set_image(ui.render(self.ps, time.time()))

    def refresh_panel(self):
        self.rebuild_panel()

    def close_panel(self):
        if self.panel:
            self.remove(self.panel)
            self.panel = self.panel_builder = self.ps = self.panel_ui = None

    def show_menu(self, name):
        self.menu_name = name
        self.remove_tag("menu")
        self.menu_buttons = []
        specs = [(self.t("play"), self.start_flow), (self.t("quit"), self.destroy)]
        mx, y0 = self.menu_x(), int(self.H * 0.4)
        for i, (label, cmd) in enumerate(specs):
            btn = Btn(self, text=label, command=cmd, spec=self.font(14))
            btn.sprite.x, btn.sprite.y = mx, y0 + i * 70
            self.menu_buttons.append(btn)
            for sp in btn.sprites():
                self.add(sp)

    def start_flow(self):
        self.open_new_account()

    # =========================================================================
    # SÉLECTION ET GESTION DE LA CLASSE DE PERSONNAGE
    # =========================================================================

    def select_class(self, class_name):
        """Callback exécuté lors du clic sur le bouton d'une classe."""
        self.selected_class = class_name
        sfx("click")
        self.refresh_panel()

    def open_new_account(self):
        self.auth_msg = None
        self.selected_class = None
        self.show_panel(self.build_new_account, side=True)

    def build_new_account(self, ui):
        t = self.t
        ui.title(t("new_account"))

        # Champ de saisie pour le nom du compte
        ui.label(t("account_name"), self.body(11), "muted", align="w", pad=(4, 2))
        ui.entry("e_acc", on_submit=self.submit_new_account)

        ui.spacer(6)
        ui.label("CHOISISSEZ LA CLASSE :", self.body(11, True), "accent", align="c", pad=(4, 4))

        # Affichage du statut de sélection
        cur_cls = self.selected_class if self.selected_class else "Aucune classe sélectionnée"
        color_cls = "ok" if self.selected_class else "err"
        ui.label(f"Sélection : {cur_cls}", self.body(11, True), color_cls, align="c", pad=(0, 6))

        # Boutons cliquables pour chacune des 13 classes disponibles
        for cls in AVAILABLE_CLASSES:
            is_active = (self.selected_class == cls)
            btn_pal = dict(self.pal, accent=self.pal["ok"]) if is_active else self.pal
            label_str = f"[✓] {cls}" if is_active else cls
            
            ui.button(
                label_str,
                lambda c=cls: self.select_class(c),
                self.font(11),
                width=28,
                pal=btn_pal,
                pad=(0, 3),
                pady=5
            )

        ui.spacer(8)
        self.auth_msg_label(ui)
        ui.button(t("create_short"), self.submit_new_account, self.font(13), width=30)
        ui.button(t("back"), self.close_panel, self.font(13), width=30, pad=(0, 0))

    def submit_new_account(self):
        if self.ps is None or self.panel_builder != self.build_new_account:
            return

        name = self.ps.text.get("e_acc", "").strip()
        if not name:
            return self.set_auth_msg("err_fill")

        if not getattr(self, "selected_class", None):
            self.auth_msg = ("Veuillez choisir une classe en cliquant sur un bouton.", "err")
            self.refresh_panel()
            return

        selected_cls = self.selected_class

        def work():
            net = self._net()
            acc = net.create_account(name, selected_cls)
            net.select_account(acc["account_id"])
            return acc

        self.run_net(work, self.on_account_ready, text="creating")

    def _net(self):
        if self.net is None:
            raise net_proto.AuthError("srv_busy")
        return self.net

    def run_net(self, work, done, text="net_wait"):
        if self.net_busy:
            return
        self.net_busy = True
        self.busy_text = text
        def runner():
            try:
                res = work()
                self.jobs.put(lambda: done(res))
            except Exception as e:
                self.jobs.put(lambda: self.set_auth_msg(str(e)))
            finally:
                self.net_busy = False
        threading.Thread(target=runner, daemon=True).start()

    def set_auth_msg(self, msg, kind="err"):
        self.auth_msg = (msg, kind)
        self.refresh_panel()

    def auth_msg_label(self, ui):
        if self.net_busy:
            ui.progress(self.t(self.busy_text))
        elif self.auth_msg:
            ui.label(str(self.auth_msg), self.body(11), self.auth_msg[14], pad=(4, 6))

    def on_account_ready(self, acc):
        self.account = acc
        self.close_panel()
        self.show_menu("main")

    def build_accounts(self, ui):
        t, accounts = self.t, self.accounts
        ui.title(t("accounts_title"))
        if accounts:
            items = []
            for a in accounts:
                line = f" {a.get('account_name', '?')}  ·  {a.get('class_name', 'Soldat')}  ·  {a.get('role_name', '')}"
                if a.get("balance") is not None:
                    line += f"  ·  {a['balance']}"
                items.append(line)
            def pick():
                sel = self.ps.sel.get("accounts", 0)
                if 0 <= sel < len(accounts):
                    self.run_net(lambda: self._net().select_account(accounts[sel]["account_id"]),
                                 lambda _: self.on_account_ready(accounts[sel]))
            ui.listbox("accounts", items, pick, rows=min(6, max(3, len(items))), width=40, pad=(0, 16))
            ui.button(t("choose_account"), pick, self.font(13), width=26)
        ui.button(t("back"), self.close_panel, self.font(13), width=26, pad=(0, 0))

if __name__ == "__main__":
    app = App()
    app.run()
