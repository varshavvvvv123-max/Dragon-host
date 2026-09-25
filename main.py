
"""
𝐃𝐑𝐀𝐆𝐎𝐍 𝐗 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 𝐁𝐎𝐓 𝐕𝟑.𝟓 — FULL COLOR BUTTONS + ALL FIXES
FEATURES: OWNER APPROVAL + TERMINAL ACCESS + MY FILES + COLOR BUTTONS
FIX: Android/Termux compatibility, psutil fallback, all bugs fixed
UPGRADE: Native Telegram color buttons (primary/success/danger)
CREDITS: CYBERX CODER + OMEGA UPGRADE
"""

import subprocess
import sys
import os
import importlib
import warnings

def safe_import(module_name, fallback_module=None, pip_name=None):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        pip_name = pip_name or module_name
        print(f"📦 Installing missing package: {pip_name} ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name, "--quiet"])
            return importlib.import_module(module_name)
        except:
            if fallback_module:
                warnings.warn(f"⚠️ {module_name} not available, using fallback")
                return fallback_module
            raise

def _ensure_telegram_library():
    try:
        import telebot
        from telebot.types import InlineKeyboardButton
        import inspect
        if "style" not in inspect.signature(InlineKeyboardButton.__init__).parameters:
            raise ImportError("pyTelegramBotAPI is too old for colored buttons")
        return telebot
    except (ImportError, TypeError, ValueError):
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-U",
            "pyTelegramBotAPI>=4.36.1", "--quiet"
        ])
        import telebot
        return telebot

telebot = _ensure_telegram_library()
from telebot import types
from telebot.types import (
    MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    print("⚠️ psutil not available, using fallback process management")
    HAS_PSUTIL = False
    class MockPsutil:
        class NoSuchProcess(Exception): pass
        class Process:
            def __init__(self, pid):
                self.pid = pid
            def is_running(self):
                try:
                    os.kill(self.pid, 0)
                    return True
                except OSError:
                    return False
            def children(self, recursive=False):
                return []
            def terminate(self):
                try: os.kill(self.pid, 15)
                except: pass
            def kill(self):
                try: os.kill(self.pid, 9)
                except: pass
            def wait(self, timeout=None): return
            def status(self): return 'running'
            @property
            def cpu_percent(self): return 0
            @property
            def memory_info(self):
                class Mem:
                    rss = 0
                    vms = 0
                return Mem()
            @property
            def name(self): return 'unknown'
        def cpu_percent(self, interval=1): return 0
        def virtual_memory(self):
            class Mem:
                percent = 0
                used = 0
                total = 0
            return Mem()
        def disk_usage(self, path):
            class Disk:
                percent = 0
                used = 0
                total = 0
            return Disk()
    psutil = MockPsutil()

def _ensure_package(import_name, pip_name=None):
    try:
        importlib.import_module(import_name)
    except ImportError:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pip_name or import_name, "--quiet"
        ])

_ensure_package("flask", "Flask")
_ensure_package("requests", "requests")
_ensure_package("qrcode", "qrcode")

import zipfile
import tempfile
import shutil
import time
from datetime import datetime, timedelta
import sqlite3
import json
import logging
import threading
import re
import atexit
import requests
import qrcode
from io import BytesIO
import hashlib
import random
import string
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm CYBERX HOSTING BOT V3.5"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("✅ Flask Keep-Alive Started.")

# ================================
# CONFIGURATION
# ================================
TOKEN = "8795028783:AAFLuZg1I9DTH1DKZGhPwtcUMiKDLhFApSQ"
OWNER_ID = 8535388961
ADMIN_ID = 8535388961
YOUR_USERNAME = '@Dragon_X_1'
UPDATE_CHANNEL = 'https://t.me/Dragon_X_111'
UPDATE_GROUP = 'https://t.me/Dragon_X_11'

FORCE_SUB_CHANNELS = ["@Dragon_X_king1"]
FORCE_SUB_CHANNEL_LINKS = [
    "https://t.me/Dragon_X_king1"
]
FORCE_SUB_CHANNEL_NAMES = ["𝐃ʀᴀɢᴏɴ 𝐗 👑"]

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'CYBERX_uploads')
TITAN_DATA_DIR = os.path.join(BASE_DIR, 'CYBERX_data')
DATABASE_PATH = os.path.join(TITAN_DATA_DIR, 'CYBERX_bot.db')
RUNNING_SCRIPTS_DB = os.path.join(TITAN_DATA_DIR, 'running_scripts.json')
REFERRAL_DB = os.path.join(TITAN_DATA_DIR, 'referrals.json')
PENDING_DIR = os.path.join(TITAN_DATA_DIR, 'pending_approvals')

_CB_DATA = {}
_CB_SEQ = 0
_CB_LOCK = threading.Lock()

def cb_store(action, user_id, file_name):
    global _CB_SEQ
    with _CB_LOCK:
        _CB_SEQ += 1
        key = str(_CB_SEQ)
        _CB_DATA[key] = (action, user_id, file_name)
        return key

def cb_resolve(callback_data):
    if ':' in callback_data:
        prefix, key = callback_data.split(':', 1)
        with _CB_LOCK:
            entry = _CB_DATA.get(key)
        if entry:
            return entry
        return None
    parts = callback_data.split('_')
    if len(parts) >= 3:
        try:
            uid = int(parts[1])
            fn = '_'.join(parts[2:])
            return (parts[0], uid, fn)
        except (ValueError, IndexError):
            pass
    return None

TIER_SYSTEM = {
    "free": {"name": "FREE", "upload_limit": 1, "max_file_size": 50 * 1024 * 1024,
        "icon": "🎫", "color": "#2ecc71", "auto_restart": False, "referral_needed": 3},
    "premium": {"name": "PREMIUM", "upload_limit": 10, "max_file_size": 200 * 1024 * 1024,
        "icon": "⭐", "color": "#f39c12", "auto_restart": True, "referral_needed": 0},
    "owner": {"name": "OWNER", "upload_limit": float('inf'), "max_file_size": float('inf'),
        "icon": "👑", "color": "#e74c3c", "auto_restart": True, "referral_needed": 0}
}

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(TITAN_DATA_DIR, exist_ok=True)
os.makedirs(PENDING_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN, parse_mode=None)

try:
    _style_probe = InlineKeyboardButton(text='style-test', callback_data='style-test', style='primary')
    if getattr(_style_probe, 'style', None) != 'primary':
        raise RuntimeError("style field is not supported by this SDK")
except Exception as exc:
    raise RuntimeError("Colored buttons require pyTelegramBotAPI >= 4.36.1.") from exc

bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
referral_data = {}
pending_files = {}
terminal_sessions = {}
pending_notifications = {}

BANNED_USERS_FILE = os.path.join(TITAN_DATA_DIR, 'banned_users.json')
banned_users = set()

def _load_banned_users():
    global banned_users
    try:
        if os.path.exists(BANNED_USERS_FILE):
            with open(BANNED_USERS_FILE, 'r') as f:
                banned_users = set(json.load(f))
        else:
            banned_users = set()
    except:
        banned_users = set()

def _save_banned_users():
    try:
        with open(BANNED_USERS_FILE, 'w') as f:
            json.dump(list(banned_users), f)
    except:
        pass

def is_user_banned(user_id):
    return user_id in banned_users

def ban_user(user_id):
    banned_users.add(user_id)
    _save_banned_users()
    for fname, ftype in user_files.get(user_id, []):
        script_key = f"{user_id}_{fname}"
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
    if user_id in terminal_sessions:
        del terminal_sessions[user_id]

def unban_user(user_id):
    banned_users.discard(user_id)
    _save_banned_users()

_load_banned_users()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_to_bold_uppercase(text: str) -> str:
    bold_mapping = {
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆',
        'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍',
        'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔',
        'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠',
        'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧',
        'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭', 'u': '𝐮',
        'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓', '6': '𝟔',
        '7': '𝟕', '8': '𝟖', '9': '𝟗',
        ' ': ' ', '!': '!', '@': '@', '#': '#', '$': '$', '%': '%', '^': '^',
        '&': '&', '*': '*', '(': '(', ')': ')', '-': '-', '_': '_', '=': '=',
        '+': '+', '[': '[', ']': ']', '{': '{', '}': '}', '\\': '\\', '|': '|',
        ';': ';', ':': ':', "'": "'", '"': '"', ',': ',', '.': '.', '<': '<',
        '>': '>', '/': '/', '?': '?', '`': '`', '~': '~'
    }
    result = []
    for char in str(text):
        if char in bold_mapping:
            result.append(bold_mapping[char])
        else:
            result.append(char)
    try:
        return ''.join(result)
    except:
        safe_result = []
        for c in result:
            try:
                safe_result.append(c)
                ''.join(safe_result).encode('utf-8')
            except:
                safe_result.append('?')
        return ''.join(safe_result)

B = convert_to_bold_uppercase

BUTTON_STYLES = {"primary": "primary", "success": "success", "danger": "danger"}

def _normalize_button_style(style):
    if style is None:
        return None
    try:
        return BUTTON_STYLES.get(str(style).strip().lower())
    except Exception:
        return None

def _button_text(text):
    if text is None:
        return ""
    try:
        return str(text).strip()
    except Exception:
        return ""

def make_colored_button(text: str, style: str = None, **kwargs) -> InlineKeyboardButton:
    clean_text = _button_text(text)
    normalized_style = _normalize_button_style(style)
    button_kwargs = kwargs.copy()
    button_kwargs.pop("style", None)
    if normalized_style:
        button_kwargs["style"] = normalized_style
    try:
        return InlineKeyboardButton(text=clean_text, **button_kwargs)
    except TypeError:
        button_kwargs.pop("style", None)
        return InlineKeyboardButton(text=clean_text, **button_kwargs)

def make_styled_row(buttons_config: list) -> list:
    row = []
    if not buttons_config:
        return row
    for cfg in buttons_config:
        if not isinstance(cfg, dict):
            continue
        cfg_copy = cfg.copy()
        text = cfg_copy.pop("text", "")
        style = cfg_copy.pop("style", None)
        try:
            button = make_colored_button(text, style=style, **cfg_copy)
            row.append(button)
        except Exception:
            continue
    return row

def _add_button_rows(markup, buttons, columns=2):
    if markup is None or not buttons:
        return markup
    try:
        columns = max(1, int(columns))
    except (TypeError, ValueError):
        columns = 2
    for i in range(0, len(buttons), columns):
        row = buttons[i:i + columns]
        if row:
            markup.row(*row)
    return markup

NOTIFIED_USERS_FILE = os.path.join(TITAN_DATA_DIR, 'notified_users.json')
_notified_users_cache = set()

def _load_notified_users():
    global _notified_users_cache
    try:
        if os.path.exists(NOTIFIED_USERS_FILE):
            with open(NOTIFIED_USERS_FILE, 'r') as f:
                _notified_users_cache = set(json.load(f))
        else:
            _notified_users_cache = set()
    except:
        _notified_users_cache = set()

def _save_notified_users():
    try:
        with open(NOTIFIED_USERS_FILE, 'w') as f:
            json.dump(list(_notified_users_cache), f)
    except:
        pass

_load_notified_users()

def _get_db_user_count():
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''SELECT COUNT(*) FROM (
            SELECT user_id FROM active_users
            UNION
            SELECT user_id FROM user_files
        )''')
        count = c.fetchone()[0] or 0
        conn.close()
        return count
    except Exception as e:
        logger.error(f"DB count error: {e}")
        return len(active_users)

def notify_owner_new_user(user_id, first_name, username):
    if user_id in _notified_users_cache:
        return
    _notified_users_cache.add(user_id)
    _save_notified_users()
    uname = f"@{username}" if username else "No username"
    alert = f"""🆕 NEW USER JOINED!

👤 Name: {first_name}
🆔 ID: {user_id}
👥 Username: {uname}
📊 Total Users: {_get_db_user_count()}

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    try:
        bot.send_message(OWNER_ID, alert)
    except Exception as e:
        logger.error(f"Owner notification failed: {e}")

class ReferralSystem:
    def __init__(self):
        self.referral_file = REFERRAL_DB

    def load_referrals(self):
        global referral_data
        try:
            if os.path.exists(self.referral_file):
                with open(self.referral_file, 'r') as f:
                    referral_data = json.load(f)
            else:
                referral_data = {}
        except Exception as e:
            logger.error(f"Error loading referrals: {e}")
            referral_data = {}

    def save_referrals(self):
        try:
            with open(self.referral_file, 'w') as f:
                json.dump(referral_data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving referrals: {e}")

    def generate_referral_code(self, user_id):
        code = f"CYBERX{user_id}{random.randint(1000, 9999)}"
        if user_id not in referral_data:
            referral_data[user_id] = {
                'code': code, 'referrals': [], 'count': 0,
                'auto_restart_enabled': False, 'generated_at': datetime.now().isoformat(),
                'username': ''
            }
        else:
            referral_data[user_id]['code'] = code
        self.save_referrals()
        return code

    def get_referral_code(self, user_id):
        if user_id in referral_data:
            return referral_data[user_id].get('code')
        return self.generate_referral_code(user_id)

    def add_referral(self, referrer_id, referred_id, referred_username=None):
        if referrer_id == referred_id:
            return False
        if referrer_id not in referral_data:
            self.generate_referral_code(referrer_id)
        if 'username' not in referral_data[referrer_id]:
            referral_data[referrer_id]['username'] = ''
        referred_info = {
            'user_id': referred_id, 'username': referred_username or '',
            'joined_at': datetime.now().isoformat()
        }
        if referred_id not in [r['user_id'] for r in referral_data[referrer_id].get('referrals', [])]:
            referral_data[referrer_id].setdefault('referrals', []).append(referred_info)
            referral_data[referrer_id]['count'] = len(referral_data[referrer_id]['referrals'])
            if referral_data[referrer_id]['count'] >= TIER_SYSTEM['free']['referral_needed']:
                referral_data[referrer_id]['auto_restart_enabled'] = True
            self.save_referrals()
            return True
        return False

    def get_referral_count(self, user_id):
        if user_id in referral_data:
            return referral_data[user_id]['count']
        return 0

    def is_auto_restart_enabled(self, user_id):
        if user_id in referral_data:
            return referral_data[user_id]['auto_restart_enabled']
        return False

    def get_top_referrers(self, limit=10):
        referrers = []
        for user_id, data in referral_data.items():
            if 'count' in data and data['count'] > 0:
                referrers.append({
                    'user_id': user_id, 'username': data.get('username', ''),
                    'count': data['count'], 'auto_restart': data.get('auto_restart_enabled', False)
                })
        referrers.sort(key=lambda x: x['count'], reverse=True)
        return referrers[:limit]

    def get_user_rank(self, user_id):
        referrers = self.get_top_referrers(limit=1000)
        for i, referrer in enumerate(referrers, 1):
            if referrer['user_id'] == user_id:
                return i
        return None

    def update_user_username(self, user_id, username):
        if user_id in referral_data:
            referral_data[user_id]['username'] = username or ''
            self.save_referrals()

referral_system = ReferralSystem()
referral_system.load_referrals()

class ProgressAnimation:
    @staticmethod
    def execute_animation():
        return [B("⚡ 𝑬𝒙𝒆𝒄𝒖𝒕𝒊𝒏𝒈: ■□□□□□□□□□ 0%"), B("⚡ 𝑬𝒙𝒆𝒄𝒖𝒕𝒊𝒏𝒈: ■■□□□□□□□□ 20%"), B("⚡ 𝑬𝒙𝒆𝒄𝒖𝒕𝒊𝒏𝒈: ■■■□□□□□□□ 40%"), B("⚡ 𝑬𝒙𝒆𝒄𝒖𝒕𝒊𝒏𝒈: ■■■■□□□□□□ 50%"), B("⚡ 𝑬𝒙𝒆𝒄𝒖𝒕𝒊𝒏𝒈: ■■■■■□□□□□ 60%"), B("⚡ 𝑬𝒙𝒆𝒄𝒖𝒕𝒊𝒏𝒈: ■■■■■■■□□□ 80%"), B("✅ 𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆: ■■■■■■■■■■ 100%")]
    @staticmethod
    def upload_animation():
        return [B("📤 𝑼𝒑𝒍𝒐𝒂𝒅𝒊𝒏𝒈: ■□□□□□□□□□ 0%"), B("📤 𝑼𝒑𝒍𝒐𝒂𝒅𝒊𝒏𝒈: ■■■□□□□□□□ 30%"), B("📤 𝑼𝒑𝒍𝒐𝒂𝒅𝒊𝒏𝒈: ■■■■■■□□□□ 60%"), B("📤 𝑼𝒑𝒍𝒐𝒂𝒅𝒊𝒏𝒈: ■■■■■■■■■□ 90%"), B("✅ 𝑼𝒑𝒍𝒐𝒂𝒅 𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆: ■■■■■■■■■■ 100%")]
    @staticmethod
    def recovery_animation():
        return [B("🔄 𝑹𝒆𝒄𝒐𝒗𝒆𝒓𝒚: ■□□□□□□□□□ 0%"), B("🔄 𝑹𝒆𝒄𝒐𝒗𝒆𝒓𝒚: ■■■□□□□□□□ 30%"), B("🔄 𝑹𝒆𝒄𝒐𝒗𝒆𝒓𝒚: ■■■■■■□□□□ 60%"), B("🔄 𝑹𝒆𝒄𝒐𝒗𝒆𝒓𝒚: ■■■■■■■■■□ 90%"), B("✅ 𝑹𝒆𝒄𝒐𝒗𝒆𝒓𝒚 𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆: ■■■■■■■■■■ 100%")]
    @staticmethod
    def restart_animation():
        return [B("🔄 𝑹𝒆𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈: ■□□□□□□□□□ 0%"), B("🔄 𝑹𝒆𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈: ■■■□□□□□□□ 30%"), B("🔄 𝑹𝒆𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈: ■■■■■■□□□□ 60%"), B("🔄 𝑹𝒆𝒔𝒕𝒂𝒓𝒕𝒊𝒏𝒈: ■■■■■■■■■□ 90%"), B("✅ 𝑹𝒆𝒔𝒕𝒂𝒓𝒕𝒆𝒅: ■■■■■■■■■■ 100%")]

class AutoRecoverySystem:
    def __init__(self):
        self.running_scripts_file = RUNNING_SCRIPTS_DB

    def save_running_script(self, user_id, file_name, file_path, process_pid):
        try:
            if os.path.exists(self.running_scripts_file):
                with open(self.running_scripts_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"running_scripts": []}
            data["running_scripts"] = [s for s in data["running_scripts"]
                                     if not (s["user_id"] == user_id and s["file_name"] == file_name)]
            script_info = {
                "user_id": user_id, "file_name": file_name, "file_path": file_path,
                "process_pid": process_pid, "start_time": datetime.now().isoformat(),
                "status": "running", "last_updated": datetime.now().isoformat()
            }
            data["running_scripts"].append(script_info)
            with open(self.running_scripts_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving running script: {e}")

    def remove_running_script(self, user_id, file_name):
        try:
            if os.path.exists(self.running_scripts_file):
                with open(self.running_scripts_file, 'r') as f:
                    data = json.load(f)
                data["running_scripts"] = [s for s in data["running_scripts"]
                                         if not (s["user_id"] == user_id and s["file_name"] == file_name)]
                with open(self.running_scripts_file, 'w') as f:
                    json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error removing script: {e}")

    def recover_all_scripts(self):
        try:
            if not os.path.exists(self.running_scripts_file):
                return []
            with open(self.running_scripts_file, 'r') as f:
                data = json.load(f)
            recovered = []
            for script in data.get("running_scripts", []):
                try:
                    user_id = script["user_id"]
                    file_name = script["file_name"]
                    file_path = script["file_path"]
                    if not os.path.exists(file_path):
                        continue
                    user_has_file = False
                    for fname, ftype in user_files.get(user_id, []):
                        if fname == file_name:
                            user_has_file = True
                            break
                    if not user_has_file:
                        continue
                    tier = get_user_tier(user_id)
                    auto_restart_enabled = TIER_SYSTEM[tier]['auto_restart']
                    if tier == 'free':
                        auto_restart_enabled = referral_system.is_auto_restart_enabled(user_id)
                    if not auto_restart_enabled:
                        continue
                    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
                    file_ext = os.path.splitext(file_name)[1].lower()
                    if file_ext == '.py':
                        threading.Thread(target=self._restart_py_script,
                                       args=(user_id, file_path, user_folder, file_name)).start()
                    elif file_ext == '.js':
                        threading.Thread(target=self._restart_js_script,
                                       args=(user_id, file_path, user_folder, file_name)).start()
                    recovered.append({"user_id": user_id, "file_name": file_name, "status": "recovering"})
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error in recovery: {e}")
            return recovered
        except Exception as e:
            logger.error(f"Error in recovery system: {e}")
            return []

    def _restart_py_script(self, user_id, file_path, user_folder, file_name):
        try:
            script_key = f"{user_id}_{file_name}"
            if script_key in bot_scripts:
                return
            log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            log_file = open(log_file_path, 'a', encoding='utf-8', errors='ignore')
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env.setdefault('PYTHONUNBUFFERED', '1')
            process = subprocess.Popen(
                [sys.executable, file_path], cwd=user_folder,
                stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                startupinfo=startupinfo, encoding='utf-8', errors='ignore',
                env=env
            )
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'user_id': user_id, 'start_time': datetime.now(), 'type': 'py', 'script_key': script_key
            }
            self.save_running_script(user_id, file_name, file_path, process.pid)
        except Exception as e:
            logger.error(f"Error restarting Python: {e}")

    def _restart_js_script(self, user_id, file_path, user_folder, file_name):
        try:
            script_key = f"{user_id}_{file_name}"
            if script_key in bot_scripts:
                return
            log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            log_file = open(log_file_path, 'a', encoding='utf-8', errors='ignore')
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env.setdefault('PYTHONUNBUFFERED', '1')
            process = subprocess.Popen(
                ['node', file_path], cwd=user_folder,
                stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                startupinfo=startupinfo, encoding='utf-8', errors='ignore',
                env=env
            )
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'user_id': user_id, 'start_time': datetime.now(), 'type': 'js', 'script_key': script_key
            }
            self.save_running_script(user_id, file_name, file_path, process.pid)
        except Exception as e:
            logger.error(f"Error restarting JS: {e}")

    def get_running_count(self):
        try:
            if os.path.exists(self.running_scripts_file):
                with open(self.running_scripts_file, 'r') as f:
                    data = json.load(f)
                return len(data.get("running_scripts", []))
            return 0
        except:
            return 0

recovery_system = AutoRecoverySystem()

def init_db():
    logger.info(f"📊 Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT, tier TEXT, created_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT, uploaded_at TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY, username TEXT, first_join TEXT, last_seen TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY, added_by INTEGER, added_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                     (user_id INTEGER PRIMARY KEY, uploads_count INTEGER,
                      scripts_run INTEGER, total_upload_size INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pending_approvals
                     (pending_id TEXT PRIMARY KEY, user_id INTEGER, file_name TEXT,
                      file_path TEXT, file_ext TEXT, status TEXT, submitted_at TEXT,
                      reviewed_by INTEGER, reviewed_at TEXT)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)',
                  (OWNER_ID, OWNER_ID, datetime.now().isoformat()))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)',
                      (ADMIN_ID, OWNER_ID, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized.")
    except Exception as e:
        logger.error(f"Database error: {e}", exc_info=True)

def load_data():
    logger.info("📥 Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id, expiry, tier FROM subscriptions')
        for user_id, expiry, tier in c.fetchall():
            try:
                user_subscriptions[user_id] = {
                    'expiry': datetime.fromisoformat(expiry) if expiry else None, 'tier': tier or 'free'
                }
            except:
                pass
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))
        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())
        conn.close()
        logger.info(f"✅ Data loaded: {len(active_users)} users, {sum(len(v) for v in user_files.values())} files")
    except Exception as e:
        logger.error(f"Loading error: {e}", exc_info=True)

init_db()
load_data()

def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_tier(user_id):
    if user_id == OWNER_ID:
        return "owner"
    elif user_id in admin_ids:
        return "owner"
    elif user_id in user_subscriptions:
        sub = user_subscriptions[user_id]
        if sub.get('expiry') and sub['expiry'] > datetime.now():
            return sub.get('tier', 'premium')
    return "free"

def get_user_file_limit(user_id):
    return TIER_SYSTEM[get_user_tier(user_id)]["upload_limit"]

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def is_bot_running(user_id, file_name):
    script_key = f"{user_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info is None:
        return False
    if isinstance(script_info, dict):
        proc = script_info.get('process')
    else:
        proc = script_info
    if proc is None:
        return False
    if not hasattr(proc, 'pid'):
        return False
    try:
        if HAS_PSUTIL:
            p = psutil.Process(proc.pid)
            return p.is_running() and p.status() not in [
                psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD, psutil.STATUS_STOPPED
            ]
        else:
            try:
                os.kill(proc.pid, 0)
                return True
            except OSError:
                return False
    except:
        if script_key in bot_scripts:
            if 'log_file' in bot_scripts[script_key] and bot_scripts[script_key]['log_file']:
                try: bot_scripts[script_key]['log_file'].close()
                except: pass
            del bot_scripts[script_key]
        recovery_system.remove_running_script(user_id, file_name)
        if user_id in terminal_sessions and file_name in terminal_sessions[user_id]:
            del terminal_sessions[user_id][file_name]
        return False

def kill_process_tree(process_info):
    try:
        if isinstance(process_info, dict):
            process = process_info.get('process')
            log_file = process_info.get('log_file')
        else:
            process = process_info
            log_file = None
        if process and hasattr(process, 'pid'):
            pid = process.pid
            try:
                if HAS_PSUTIL:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    for child in children:
                        try:
                            child.terminate()
                        except:
                            try: child.kill()
                            except: pass
                    try:
                        parent.terminate()
                        parent.wait(timeout=3)
                    except:
                        try: parent.kill()
                        except: pass
                else:
                    try:
                        os.kill(pid, 15)
                        time.sleep(0.5)
                        os.kill(pid, 9)
                    except:
                        pass
                if isinstance(process_info, dict) and 'user_id' in process_info and 'file_name' in process_info:
                    recovery_system.remove_running_script(process_info['user_id'], process_info['file_name'])
                    uid = process_info['user_id']
                    fname = process_info['file_name']
                    if uid in terminal_sessions and fname in terminal_sessions[uid]:
                        del terminal_sessions[uid][fname]
                        if not terminal_sessions[uid]:
                            del terminal_sessions[uid]
            except:
                pass
            finally:
                if log_file:
                    try: log_file.close()
                    except: pass
    except Exception as e:
        logger.error(f"Kill error: {e}")

def send_restart_notification():
    logger.info("📢 Sending restart notifications...")
    notification_text = """⚠️ IMPORTANT ANNOUNCEMENT

🔄 Bot is restarting for maintenance.
Your scripts will be auto-restarted if:
✅ Premium/Owner
✅ 3+ referrals

⏱️ Back in 30 seconds"""
    for user_id in list(active_users):
        try:
            bot.send_message(user_id, notification_text)
        except:
            pass
        time.sleep(0.1)

def safe_notify_user(user_id, text, reply_markup=None, parse_mode=None):
    try:
        bot.send_message(user_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
        return True
    except Exception as e:
        logger.warning(f"Could not notify user {user_id}: {e}. Storing notification.")
        pending_notifications[user_id] = {
            'text': text, 'reply_markup': reply_markup, 'parse_mode': parse_mode
        }
        return False

def flush_pending_notifications(user_id):
    if user_id in pending_notifications:
        notif = pending_notifications.pop(user_id)
        try:
            bot.send_message(user_id, notif['text'],
                           reply_markup=notif['reply_markup'],
                           parse_mode=notif['parse_mode'])
            return True
        except Exception as e:
            logger.error(f"Still cannot notify {user_id}: {e}")
    return False

# ================================
# BUTTON LAYOUTS — FULL COLOR
# ================================

def _menu_button(text, callback_data=None, url=None, style='primary'):
    kwargs = {}
    if callback_data is not None:
        kwargs['callback_data'] = callback_data
    if url is not None:
        kwargs['url'] = url
    return make_colored_button(B(text), style=style, **kwargs)

def _add_two_column_rows(markup, buttons):
    if markup is None:
        return markup
    if not buttons:
        return markup
    for index in range(0, len(buttons), 2):
        row = buttons[index:index + 2]
        if row:
            markup.row(*row)
    return markup

def create_main_menu_inline(user_id):
    buttons = [
        _menu_button('📢 Updates', url=UPDATE_CHANNEL, style='primary'),
        _menu_button('👥 Join Group', url=UPDATE_GROUP, style='primary'),
        _menu_button('📤 Upload', callback_data='upload', style='primary'),
        _menu_button('📂 My Files', callback_data='check_files', style='primary'),
        _menu_button('⚡ Speed', callback_data='speed', style='primary'),
        _menu_button('📊 Stats', callback_data='stats', style='primary'),
        _menu_button('👤 Profile', callback_data='profile', style='primary'),
        _menu_button('🤝 Refer', callback_data='refer', style='success'),
        _menu_button('🏆 Leaderboard', callback_data='leaderboard', style='primary'),
        _menu_button('🐙 GitHub', callback_data='github', style='primary'),
        _menu_button('🔄 Restart All', callback_data='restart_all', style='danger'),
        _menu_button('📞 Contact', url=f"https://t.me/{str(YOUR_USERNAME).lstrip('@')}", style='primary'),
    ]
    if user_id in admin_ids:
        buttons.extend([
            _menu_button('👑 Admin', callback_data='admin_panel', style='danger'),
            _menu_button('💳 Subscription', callback_data='subscription', style='primary'),
            _menu_button('📢 Broadcast', callback_data='broadcast', style='success'),
            _menu_button('🔒 Lock' if not bot_locked else '🔓 Unlock',
                        callback_data='lock_bot' if not bot_locked else 'unlock_bot',
                        style='danger' if not bot_locked else 'success'),
            _menu_button('🔄 Recover', callback_data='recover_all', style='primary'),
            _menu_button('📈 Analytics', callback_data='analytics', style='primary'),
            _menu_button('🚀 Restart Bot', callback_data='restart_bot', style='danger'),
            _menu_button('⏳ Pending', callback_data='view_pending', style='primary'),
        ])
    try:
        markup = InlineKeyboardMarkup(row_width=2)
    except (TypeError, ValueError):
        markup = InlineKeyboardMarkup([])
    return _add_two_column_rows(markup, buttons)

def create_reply_keyboard_main_menu(user_id):
    if user_id in admin_ids:
        items = [
            ('📢 Updates', 'primary'), ('👥 Join Group', 'primary'),
            ('📤 Upload', 'primary'), ('📂 My Files', 'primary'),
            ('⚡ Speed', 'primary'), ('📊 Stats', 'primary'),
            ('👤 Profile', 'primary'), ('🤝 Refer', 'success'),
            ('🏆 Leaderboard', 'primary'), ('🐙 GitHub', 'primary'),
            ('🔄 Restart All', 'danger'), ('📞 Contact', 'primary'),
            ('👑 Admin', 'danger'), ('💳 Subscription', 'primary'),
            ('📢 Broadcast', 'success'), ('🔄 Recover', 'success'),
            ('🚀 Restart Bot', 'danger'), ('⏳ Pending', 'primary'),
            ('🔒 Lock' if not bot_locked else '🔓 Unlock',
             'danger' if not bot_locked else 'success'),
        ]
    else:
        items = [
            ('📢 Updates', 'primary'), ('👥 Join Group', 'primary'),
            ('📤 Upload', 'primary'), ('📂 My Files', 'primary'),
            ('⚡ Speed', 'primary'), ('📊 Stats', 'primary'),
            ('👤 Profile', 'primary'), ('🤝 Refer', 'success'),
            ('🏆 Leaderboard', 'primary'), ('🐙 GitHub', 'primary'),
            ('🔄 Restart All', 'danger'), ('📞 Contact', 'primary'),
        ]
    try:
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=False,
            is_persistent=True, input_field_placeholder='Choose an option…',
            row_width=2,
        )
    except (TypeError, ValueError):
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=False, row_width=2,
        )
    for index in range(0, len(items), 2):
        row = items[index:index + 2]
        buttons = []
        for label, style in row:
            try:
                buttons.append(KeyboardButton(B(label), style=_normalize_button_style(style)))
            except (TypeError, ValueError):
                buttons.append(KeyboardButton(B(label)))
        if buttons:
            markup.row(*buttons)
    return markup

def create_control_buttons(user_id, file_name, is_running=True):
    try:
        markup = InlineKeyboardMarkup(row_width=2)
    except (TypeError, ValueError):
        markup = InlineKeyboardMarkup([])
    if is_running:
        k_stop = cb_store('stop', user_id, file_name)
        k_restart = cb_store('restart', user_id, file_name)
        k_delete = cb_store('delete', user_id, file_name)
        k_logs = cb_store('logs', user_id, file_name)
        k_terminal = cb_store('terminal', user_id, file_name)
        markup.row(
            make_colored_button(B("🔴 Stop"), style="danger", callback_data=f'p:{k_stop}'),
            make_colored_button(B("🔄 Restart"), style="primary", callback_data=f'r:{k_restart}')
        )
        markup.row(
            make_colored_button(B("🗑️ Delete"), style="danger", callback_data=f'd:{k_delete}'),
            make_colored_button(B("📜 Logs"), style="primary", callback_data=f'l:{k_logs}')
        )
        markup.row(
            make_colored_button(B("💻 Terminal"), style="success", callback_data=f't:{k_terminal}')
        )
    else:
        k_start = cb_store('start', user_id, file_name)
        k_delete = cb_store('delete', user_id, file_name)
        k_logs = cb_store('logs', user_id, file_name)
        markup.row(
            make_colored_button(B("🟢 Start"), style="success", callback_data=f's:{k_start}'),
            make_colored_button(B("🗑️ Delete"), style="danger", callback_data=f'd:{k_delete}')
        )
        markup.row(
            make_colored_button(B("📜 View Logs"), style="primary", callback_data=f'l:{k_logs}')
        )
    markup.row(
        make_colored_button(B("🔙 Back"), style="primary", callback_data='check_files')
    )
    return markup

def create_admin_panel():
    markup = InlineKeyboardMarkup([])
    markup.row(
        make_colored_button(B('➕ Add Admin'), style="success", callback_data='add_admin'),
        make_colored_button(B('➖ Remove Admin'), style="danger", callback_data='remove_admin')
    )
    markup.row(
        make_colored_button(B('📋 List Admins'), style="primary", callback_data='list_admins'),
        make_colored_button(B('📊 System Stats'), style="primary", callback_data='system_stats')
    )
    markup.row(
        make_colored_button(B('⏳ Pending Approvals'), style="primary", callback_data='view_pending')
    )
    markup.row(
        make_colored_button(B('🚫 Ban User'), style="danger", callback_data='ban_user'),
        make_colored_button(B('✅ Unban User'), style="success", callback_data='unban_user')
    )
    markup.row(
        make_colored_button(B('📋 Banned List'), style="primary", callback_data='banned_list')
    )
    markup.row(
        make_colored_button(B('📁 All Files'), style="primary", callback_data='all_files')
    )
    markup.row(
        make_colored_button(B('🔙 Back'), style="primary", callback_data='back_to_main')
    )
    return markup

def create_subscription_menu():
    markup = InlineKeyboardMarkup([])
    markup.row(
        make_colored_button(B('➕ Add Sub'), style="success", callback_data='add_subscription'),
        make_colored_button(B('➖ Remove Sub'), style="danger", callback_data='remove_subscription')
    )
    markup.row(
        make_colored_button(B('🔍 Check Sub'), style="primary", callback_data='check_subscription')
    )
    markup.row(
        make_colored_button(B('🔙 Back'), style="primary", callback_data='back_to_main')
    )
    return markup

def create_referral_menu(user_id):
    markup = InlineKeyboardMarkup([])
    referral_code = referral_system.get_referral_code(user_id)
    bot_username = bot.get_me().username
    referral_link = f"https://t.me/{str(bot_username).lstrip('@')}?start={referral_code}"
    markup.row(
        make_colored_button(B('🔗 Copy Link'), style="primary", callback_data=f'copy_referral_{user_id}'),
        make_colored_button(B('📊 My Referrals'), style="primary", callback_data=f'check_referrals_{user_id}')
    )
    markup.row(
        make_colored_button(B('🏆 Leaderboard'), style="primary", callback_data='leaderboard'),
        make_colored_button(B('📋 QR Code'), style="success", callback_data=f'qr_referral_{user_id}')
    )
    markup.row(
        make_colored_button(B('🔙 Back'), style="primary", callback_data='back_to_main')
    )
    return markup, referral_link

def create_leaderboard_markup():
    markup = InlineKeyboardMarkup([])
    markup.row(
        make_colored_button(B('🔄 Refresh'), style="primary", callback_data='refresh_leaderboard'),
        make_colored_button(B('🏆 My Rank'), style="primary", callback_data='my_rank')
    )
    markup.row(
        make_colored_button(B('🤝 Refer'), style="success", callback_data='refer'),
        make_colored_button(B('🔙 Back'), style="primary", callback_data='back_to_main')
    )
    return markup

# ================================
# APPROVAL SYSTEM
# ================================
def generate_pending_id():
    return f"APPR{int(time.time())}{random.randint(1000,9999)}"

def handle_file_upload(message):
    user_id = message.from_user.id
    if user_id in admin_ids:
        _process_approved_upload(message)
        return
    if bot_locked:
        bot.reply_to(message, B("⚠️ Bot is locked."))
        return
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        bot.reply_to(message, B(f"⚠️ File limit reached ({current_files}/{file_limit})."))
        return
    doc = message.document
    if not doc.file_name:
        bot.reply_to(message, B("⚠️ No file name."))
        return
    file_ext = os.path.splitext(doc.file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, B("⚠️ Only .py, .js, .zip allowed."))
        return
    msg = bot.reply_to(message, ProgressAnimation.upload_animation()[0])
    try:
        for i, frame in enumerate(ProgressAnimation.upload_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        pending_id = generate_pending_id()
        pending_file_path = os.path.join(PENDING_DIR, f"{pending_id}_{doc.file_name}")
        with open(pending_file_path, 'wb') as f:
            f.write(downloaded_file)
        pending_files[pending_id] = {
            'user_id': user_id, 'file_name': doc.file_name,
            'file_path': pending_file_path, 'file_ext': file_ext,
            'owner_msg_id': None, 'user_msg_id': msg.message_id,
            'status': 'pending', 'submitted_at': datetime.now().isoformat()
        }
        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('''INSERT INTO pending_approvals
                         (pending_id, user_id, file_name, file_path, file_ext, status, submitted_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (pending_id, user_id, doc.file_name, pending_file_path, file_ext,
                       'pending', datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB error for pending: {e}")
        bot.edit_message_text(
            f"📤 File {doc.file_name} uploaded for approval.\n⏳ Please wait for owner to approve.",
            message.chat.id, msg.message_id
        )
        owner_text = f"""⏳ NEW APPROVAL REQUEST

👤 User: {message.from_user.first_name}
🆔 User ID: {user_id}
📁 File: {doc.file_name}
📂 Type: {file_ext}
📊 Files: {current_files}/{file_limit}
🎫 Tier: {TIER_SYSTEM[get_user_tier(user_id)]['icon']} {TIER_SYSTEM[get_user_tier(user_id)]['name']}

Please approve or reject:"""
        owner_markup = InlineKeyboardMarkup(row_width=2)
        owner_markup.row(
            make_colored_button(B('✅ Approve'), style="success", callback_data=f'approve_{pending_id}'),
            make_colored_button(B('❌ Reject'), style="danger", callback_data=f'reject_{pending_id}')
        )
        owner_markup.row(
            make_colored_button(B('👤 User Profile'), style="primary", callback_data=f'view_user_{user_id}')
        )
        owner_msg = bot.send_document(
            OWNER_ID, doc.file_id, caption=owner_text,
            reply_markup=owner_markup
        )
        pending_files[pending_id]['owner_msg_id'] = owner_msg.message_id
    except Exception as e:
        logger.error(f"Upload error: {e}")
        bot.edit_message_text(f"❌ Error: {str(e)[:200]}", message.chat.id, msg.message_id)

def _process_approved_upload(message):
    user_id = message.from_user.id
    doc = message.document
    if not doc.file_name:
        bot.reply_to(message, B("⚠️ No file name."))
        return
    file_ext = os.path.splitext(doc.file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, B("⚠️ Only .py, .js, .zip allowed."))
        return
    msg = bot.reply_to(message, ProgressAnimation.upload_animation()[0])
    try:
        for i, frame in enumerate(ProgressAnimation.upload_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, doc.file_name)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        if file_ext == '.zip':
            handle_zip_file(downloaded_file, doc.file_name, user_id, user_folder, message)
        elif file_ext == '.py':
            save_user_file(user_id, doc.file_name, 'py')
            threading.Thread(target=run_script, args=(file_path, user_id, user_folder, doc.file_name, message)).start()
        elif file_ext == '.js':
            save_user_file(user_id, doc.file_name, 'js')
            threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, doc.file_name, message)).start()
        bot.edit_message_text(f"✅ File {doc.file_name} uploaded and hosted directly!", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)[:200]}", message.chat.id, msg.message_id)

def handle_zip_file(file_content, file_name, user_id, user_folder, message):
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, file_name)
        with open(zip_path, 'wb') as f:
            f.write(file_content)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        extracted_files = os.listdir(temp_dir)
        py_files = [f for f in extracted_files if f.endswith('.py')]
        js_files = [f for f in extracted_files if f.endswith('.js')]
        main_script = None
        file_type = None
        for name in ['main.py', 'bot.py', 'app.py']:
            if name in py_files:
                main_script = name
                file_type = 'py'
                break
        if not main_script and py_files:
            main_script = py_files[0]
            file_type = 'py'
        elif not main_script and js_files:
            for name in ['index.js', 'main.js', 'bot.js']:
                if name in js_files:
                    main_script = name
                    file_type = 'js'
                    break
            if not main_script and js_files:
                main_script = js_files[0]
                file_type = 'js'
        if not main_script:
            bot.reply_to(message, B("❌ No .py or .js found in ZIP."))
            return
        for item in os.listdir(temp_dir):
            src = os.path.join(temp_dir, item)
            dst = os.path.join(user_folder, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        save_user_file(user_id, main_script, file_type)
        main_script_path = os.path.join(user_folder, main_script)
        if file_type == 'py':
            threading.Thread(target=run_script, args=(main_script_path, user_id, user_folder, main_script, message)).start()
        else:
            threading.Thread(target=run_js_script, args=(main_script_path, user_id, user_folder, main_script, message)).start()
    except Exception as e:
        bot.reply_to(message, B(f"❌ ZIP error: {str(e)[:200]}"))
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# ================================
# TERMINAL SYSTEM
# ================================
def generate_otp():
    return str(random.randint(100000, 999999))

def _create_terminal_markup(user_id, file_name):
    markup = InlineKeyboardMarkup(row_width=2)
    k_close = cb_store('close_terminal', user_id, file_name)
    k_stop = cb_store('stop', user_id, file_name)
    k_logs = cb_store('logs', user_id, file_name)
    k_refresh = cb_store('refresh_terminal', user_id, file_name)
    markup.row(
        make_colored_button(B('🔴 Close Terminal'), style="danger", callback_data=f'ct:{k_close}'),
        make_colored_button(B('⏹️ Stop Script'), style="danger", callback_data=f'p:{k_stop}')
    )
    markup.row(
        make_colored_button(B('📜 View Logs'), style="primary", callback_data=f'l:{k_logs}'),
        make_colored_button(B('🔄 Refresh'), style="primary", callback_data=f'rf:{k_refresh}')
    )
    return markup

def handle_terminal_access(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'terminal':
            return
        action, user_id, file_name = resolved
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        if not is_bot_running(user_id, file_name):
            bot.answer_callback_query(call.id, B("❌ Script is not running"), show_alert=True)
            return
        if user_id not in terminal_sessions:
            terminal_sessions[user_id] = {}
        if file_name in terminal_sessions[user_id] and terminal_sessions[user_id][file_name].get('authenticated'):
            _show_terminal_interface(call, user_id, file_name)
            return
        otp = generate_otp()
        terminal_sessions[user_id][file_name] = {
            'authenticated': False, 'otp': otp,
            'otp_expiry': time.time() + 120, 'file_name': file_name
        }
        k_cancel = cb_store('cancel_terminal', user_id, file_name)
        otp_markup = InlineKeyboardMarkup()
        otp_markup.add(make_colored_button(B('❌ Cancel Terminal'), style="danger", callback_data=f'cc:{k_cancel}'))
        bot.answer_callback_query(call.id, B("🔑 OTP Sent! Check your chat."))
        bot.send_message(
            call.message.chat.id,
            f"""🔐 TERMINAL AUTHENTICATION

📁 File: {file_name}
🔑 Your OTP: {otp}

Enter the 6-digit OTP to authenticate:

⚠️ OTP expires in 2 minutes
""", reply_markup=otp_markup
        )
        bot.register_next_step_handler_by_chat_id(
            call.message.chat.id,
            lambda m: _process_otp_input(m, user_id, file_name, call.message.chat.id)
        )
    except Exception as e:
        logger.error(f"Terminal error: {e}")
        bot.answer_callback_query(call.id, B("❌ Error"))

def _process_otp_input(message, user_id, file_name, chat_id):
    try:
        if user_id not in terminal_sessions or file_name not in terminal_sessions[user_id]:
            bot.reply_to(message, B("❌ Session expired. Use Terminal again."))
            return
        session = terminal_sessions[user_id][file_name]
        if session.get('authenticated'):
            _forward_to_terminal(message, user_id, file_name)
            return
        if time.time() > session.get('otp_expiry', 0):
            bot.reply_to(message, B("❌ OTP expired. Use /terminal to get a new one."))
            if user_id in terminal_sessions and file_name in terminal_sessions[user_id]:
                del terminal_sessions[user_id][file_name]
            return
        input_otp = message.text.strip()
        stored_otp = session.get('otp', '')
        if input_otp == stored_otp:
            session['authenticated'] = True
            del session['otp']
            bot.reply_to(message, f"""✅ Authentication Successful!

💻 Terminal active for: {file_name}

You can now send commands to the script's stdin.

Available commands:
• exit or close - Close Terminal
• !stop - Stop Script
• !logs - View Logs
Any other text goes to stdin
""")
            _show_terminal_interface_simple(message, user_id, file_name)
        else:
            bot.reply_to(message, B(f"❌ Wrong OTP! Try again."))
            bot.register_next_step_handler_by_chat_id(
                message.chat.id,
                lambda m: _process_otp_input(m, user_id, file_name, message.chat.id)
            )
    except Exception as e:
        logger.error(f"OTP error: {e}")
        bot.reply_to(message, B(f"❌ Error: {str(e)[:200]}"))

def _show_terminal_interface(call, user_id, file_name):
    markup = _create_terminal_markup(user_id, file_name)
    bot.edit_message_text(
        f"""💻 TERMINAL ACTIVE

📁 File: {file_name}
🟢 Status: Connected

Send any command to execute. Use buttons below:""",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup
    )

def _show_terminal_interface_simple(message, user_id, file_name):
    markup = _create_terminal_markup(user_id, file_name)
    bot.send_message(
        message.chat.id,
        f"""💻 TERMINAL ACTIVE

📁 File: {file_name}
🟢 Status: Connected

Send any text to send to stdin.
Use buttons to control:""",
        reply_markup=markup
    )

def _forward_to_terminal(message, user_id, file_name):
    try:
        text = message.text.strip()
        if text.lower() in ['exit', 'close', 'quit']:
            bot.reply_to(message, B("🔴 Terminal Closed."))
            if user_id in terminal_sessions and file_name in terminal_sessions[user_id]:
                del terminal_sessions[user_id][file_name]
            return
        if text.lower() == '!stop':
            script_key = f"{user_id}_{file_name}"
            if script_key in bot_scripts:
                kill_process_tree(bot_scripts[script_key])
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            bot.reply_to(message, B("⏹️ Script Stopped."))
            if user_id in terminal_sessions and file_name in terminal_sessions[user_id]:
                del terminal_sessions[user_id][file_name]
            return
        if text.lower() == '!logs':
            user_folder = get_user_folder(user_id)
            log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                if len(content) > 3500:
                    content = content[-3500:]
                bot.reply_to(message, f"📜 Logs:\n```\n{content}\n```")
            else:
                bot.reply_to(message, B("📭 No logs found."))
            return
        script_key = f"{user_id}_{file_name}"
        script_info = bot_scripts.get(script_key)
        if script_info:
            if isinstance(script_info, dict):
                proc = script_info.get('process')
            else:
                proc = script_info
            if hasattr(proc, 'stdin') and proc.stdin:
                try:
                    proc.stdin.write(text + '\n')
                    proc.stdin.flush()
                    bot.reply_to(message, f"✅ Command sent: {text}")
                    time.sleep(0.3)
                    user_folder = get_user_folder(user_id)
                    log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
                    if os.path.exists(log_path):
                        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                            lines = f.readlines()
                        tail = ''.join(lines[-10:])
                        if tail.strip():
                            bot.send_message(message.chat.id, f"📤 Output (tail):\n```\n{tail[:2000]}\n```")
                except Exception as e:
                    bot.reply_to(message, f"❌ Error: {str(e)[:100]}")
            else:
                bot.reply_to(message, B("❌ Process not available."))
        else:
            bot.reply_to(message, B("❌ Script not running."))
    except Exception as e:
        logger.error(f"Terminal forward error: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# ================================
# DATABASE OPERATIONS
# ================================
DB_LOCK = threading.Lock()

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('''INSERT OR REPLACE INTO user_files
                         (user_id, file_name, file_type, uploaded_at)
                         VALUES (?, ?, ?, ?)''',
                      (user_id, file_name, file_type, datetime.now().isoformat()))
            conn.commit()
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
            logger.info(f"✅ Saved file for user {user_id}: {file_name} ({file_type})")
        except Exception as e:
            logger.error(f"DB save error: {e}")
        finally:
            conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]:
                    del user_files[user_id]
            recovery_system.remove_running_script(user_id, file_name)
            logger.info(f"🗑️ Removed file for user {user_id}: {file_name}")
        except Exception as e:
            logger.error(f"DB remove error: {e}")
        finally:
            conn.close()

def add_active_user(user_id, username=None):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('''INSERT OR REPLACE INTO active_users
                         (user_id, username, first_join, last_seen)
                         VALUES (?, ?, COALESCE((SELECT first_join FROM active_users WHERE user_id = ?), ?), ?)''',
                      (user_id, username, user_id, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            logger.error(f"DB active user error: {e}")
        finally:
            conn.close()

def save_subscription(user_id, expiry, tier='premium'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            expiry_str = expiry.isoformat() if expiry else None
            c.execute('''INSERT OR REPLACE INTO subscriptions
                         (user_id, expiry, tier, created_at)
                         VALUES (?, ?, ?, ?)''',
                      (user_id, expiry_str, tier, datetime.now().isoformat()))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry, 'tier': tier}
        except Exception as e:
            logger.error(f"DB sub save error: {e}")
        finally:
            conn.close()

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions:
                del user_subscriptions[user_id]
        except Exception as e:
            logger.error(f"DB remove sub error: {e}")
        finally:
            conn.close()

# ================================
# SCRIPT RUNNING SYSTEM
# ================================
TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI', 'telegram': 'python-telegram-bot',
    'aiogram': 'aiogram', 'pyrogram': 'pyrogram', 'telethon': 'telethon',
    'requests': 'requests', 'flask': 'Flask', 'qrcode': 'qrcode',
    'pillow': 'Pillow', 'cryptography': 'cryptography',
    'bs4': 'beautifulsoup4', 'pandas': 'pandas', 'numpy': 'numpy'
}

def attempt_install_pip(module_name, message):
    package_name = TELEGRAM_MODULES.get(module_name.lower(), module_name)
    if package_name is None:
        return False
    try:
        bot.reply_to(message, B(f"🐍 Installing {module_name}..."))
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name],
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            bot.reply_to(message, B(f"✅ {package_name} installed."))
            return True
        else:
            bot.reply_to(message, B(f"❌ Failed {package_name}."))
            return False
    except Exception as e:
        bot.reply_to(message, B(f"❌ {str(e)[:100]}"))
        return False

def run_script(script_path, user_id, user_folder, file_name, message):
    try:
        msg = bot.reply_to(message, ProgressAnimation.execute_animation()[0])
        for i, frame in enumerate(ProgressAnimation.execute_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        if not os.path.exists(script_path):
            bot.edit_message_text(f"❌ File not found: {file_name}", message.chat.id, msg.message_id)
            return
        check_command = [sys.executable, script_path]
        check_proc = None
        try:
            check_proc = subprocess.Popen(check_command, cwd=user_folder,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, encoding='utf-8', errors='ignore')
            stdout, stderr = check_proc.communicate(timeout=5)
            if stderr:
                match = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                if match:
                    module_name = match.group(1)
                    if attempt_install_pip(module_name, message):
                        time.sleep(2)
                        run_script(script_path, user_id, user_folder, file_name, message)
                        return
        except subprocess.TimeoutExpired:
            if check_proc:
                check_proc.kill()
                check_proc.communicate()
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        process = subprocess.Popen(
            [sys.executable, script_path], cwd=user_folder,
            stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
            startupinfo=startupinfo, encoding='utf-8', errors='ignore',
            env=env
        )
        script_key = f"{user_id}_{file_name}"
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'user_id': user_id, 'start_time': datetime.now(), 'type': 'py', 'script_key': script_key
        }
        recovery_system.save_running_script(user_id, file_name, script_path, process.pid)
        bot.edit_message_text(
            f"✅ {file_name} started!\n📊 PID: {process.pid}\n💻 Use /terminal to access",
            message.chat.id, msg.message_id
        )
    except Exception as e:
        bot.reply_to(message, B(f"❌ {str(e)[:200]}"))

def run_js_script(script_path, user_id, user_folder, file_name, message):
    try:
        msg = bot.reply_to(message, ProgressAnimation.execute_animation()[0])
        for i, frame in enumerate(ProgressAnimation.execute_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        if not os.path.exists(script_path):
            bot.edit_message_text(f"❌ File not found: {file_name}", message.chat.id, msg.message_id)
            return
        check_command = ['node', script_path]
        check_proc = None
        try:
            check_proc = subprocess.Popen(check_command, cwd=user_folder,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, encoding='utf-8', errors='ignore')
            stdout, stderr = check_proc.communicate(timeout=5)
            if stderr and 'Cannot find module' in stderr:
                match = re.search(r"Cannot find module '(.+?)'", stderr)
                if match:
                    module_name = match.group(1)
                    bot.reply_to(message, B(f"📦 Installing {module_name}..."))
                    try:
                        subprocess.run(['npm', 'install', module_name], cwd=user_folder,
                                     capture_output=True, text=True, check=True)
                        bot.reply_to(message, B(f"✅ {module_name} installed."))
                        time.sleep(2)
                        run_js_script(script_path, user_id, user_folder, file_name, message)
                        return
                    except:
                        bot.reply_to(message, B(f"❌ Failed {module_name}."))
        except subprocess.TimeoutExpired:
            if check_proc:
                check_proc.kill()
                check_proc.communicate()
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        process = subprocess.Popen(
            ['node', script_path], cwd=user_folder,
            stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
            startupinfo=startupinfo, encoding='utf-8', errors='ignore',
            env=env
        )
        script_key = f"{user_id}_{file_name}"
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'user_id': user_id, 'start_time': datetime.now(), 'type': 'js', 'script_key': script_key
        }
        recovery_system.save_running_script(user_id, file_name, script_path, process.pid)
        bot.edit_message_text(
            f"✅ {file_name} (JS) started!\n📊 PID: {process.pid}",
            message.chat.id, msg.message_id
        )
    except Exception as e:
        bot.reply_to(message, B(f"❌ {str(e)[:200]}"))

# ================================
# COMMAND HANDLERS
# ================================
@bot.message_handler(commands=['start'])
def command_send_welcome(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        bot.reply_to(message, B("🚫 You are banned from using this bot."))
        return
    username = message.from_user.username
    add_active_user(user_id, username)
    notify_owner_new_user(user_id, message.from_user.first_name, message.from_user.username)
    if user_id not in admin_ids:
        not_joined = check_force_sub(user_id)
        if not_joined:
            markup = InlineKeyboardMarkup(row_width=1)
            for channel_tag, channel_link, channel_name in not_joined:
                markup.add(make_colored_button(f"🔵 Join {channel_name}", style="primary", url=channel_link))
            markup.add(make_colored_button("✅ Click Here After Joining ✅", style="success", callback_data='check_force_sub_start'))
            bot.reply_to(message, B("⚠️ FORCE SUBSCRIBE REQUIRED\n\nYou must join these channels:"),
                        reply_markup=markup)
            return
    referral_system.update_user_username(user_id, username)
    flush_pending_notifications(user_id)
    referral_code = None
    if len(message.text.split()) > 1:
        referral_code = message.text.split()[1].strip()
    if referral_code and referral_code.startswith('CYBERX'):
        try:
            referrer_id = int(referral_code[6:-4])
            if referrer_id != user_id:
                if referral_system.add_referral(referrer_id, user_id, username):
                    bot.reply_to(message, B(f"🎉 You were referred by user ID: {referrer_id}"))
                    try:
                        bot.send_message(
                            referrer_id,
                            f"""🎉 New Referral!

👤 A new user joined using your referral link!
🆔 User ID: {user_id}
👤 Name: {message.from_user.first_name}

📊 Total Referrals: {referral_system.get_referral_count(referrer_id)}/3

Keep sharing to unlock Auto-Restart! 🚀"""
                        )
                    except Exception as e:
                        logger.warning(f"Could not notify referrer {referrer_id}: {e}")
                        safe_notify_user(
                            referrer_id,
                            f"🎉 New Referral!\n👤 Someone joined using your link!\n📊 Total: {referral_system.get_referral_count(referrer_id)}/3"
                        )
        except Exception as e:
            logger.error(f"Referral parse error: {e}")
    tier = get_user_tier(user_id)
    tier_info = TIER_SYSTEM[tier]
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    user_rank = referral_system.get_user_rank(user_id)
    welcome_text = B(f"""
🚀 CYBERX HOSTING BOT V3.5
📌 FULL COLOR + ALL FIXES

👤 Welcome, {message.from_user.first_name}!
🆔 User ID: {user_id}
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}
🤝 Referrals: {referral_count}/3
🏆 Rank: #{user_rank if user_rank else "Not ranked"}
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

📢 Updates: {UPDATE_CHANNEL}
📞 Contact: {YOUR_USERNAME}
""")
    try:
        bot.send_message(message.chat.id, welcome_text,
                        reply_markup=create_reply_keyboard_main_menu(user_id))
    except Exception as e:
        bot.send_message(message.chat.id, welcome_text,
                        reply_markup=create_reply_keyboard_main_menu(user_id))

# ================================
# APPROVAL CALLBACKS
# ================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def callback_approve(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin only"), show_alert=True)
        return
    pending_id = call.data.split('_')[1]
    if pending_id not in pending_files:
        bot.answer_callback_query(call.id, B("❌ Pending ID not found"), show_alert=True)
        return
    info = pending_files[pending_id]
    user_id = info['user_id']
    file_name = info['file_name']
    file_path = info['file_path']
    file_ext = info['file_ext']
    try:
        user_folder = get_user_folder(user_id)
        dest_path = os.path.join(user_folder, file_name)
        shutil.move(file_path, dest_path)
        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('''UPDATE pending_approvals SET status = ?, reviewed_by = ?, reviewed_at = ?
                         WHERE pending_id = ?''',
                      ('approved', call.from_user.id, datetime.now().isoformat(), pending_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB approve error: {e}")
        file_type = file_ext.replace('.', '')
        save_user_file(user_id, file_name, file_type)
        user_markup = InlineKeyboardMarkup(row_width=2)
        k_normal = cb_store('host_normal', user_id, file_name)
        k_terminal = cb_store('host_terminal', user_id, file_name)
        user_markup.row(
            make_colored_button(B('🚀 Host Now'), style="success", callback_data=f'hn:{k_normal}'),
            make_colored_button(B('💻 Host in Terminal'), style="primary", callback_data=f'ht:{k_terminal}')
        )
        notified = safe_notify_user(
            user_id,
            f"""✅ File Approved!

📁 File: {file_name}
📂 Type: {file_type}

Choose how to host your file:""",
            reply_markup=user_markup
        )
        status_text = "✅ APPROVED" + ("\n📬 User notified." if notified else "\n⏳ Notification stored (user hasn't started bot yet).")
        bot.edit_message_caption(
            f"{status_text}\n\n👤 User: {user_id}\n📁 File: {file_name}",
            call.message.chat.id, info.get('owner_msg_id') or call.message.message_id
        )
        bot.answer_callback_query(call.id, B("✅ Approved! User will choose Host or Terminal."), show_alert=True)
        del pending_files[pending_id]
    except Exception as e:
        logger.error(f"Approval error: {e}")
        bot.answer_callback_query(call.id, B(f"❌ Error: {str(e)[:50]}"), show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def callback_reject(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin only"), show_alert=True)
        return
    pending_id = call.data.split('_')[1]
    if pending_id not in pending_files:
        bot.answer_callback_query(call.id, B("❌ Pending not found"), show_alert=True)
        return
    info = pending_files[pending_id]
    user_id = info['user_id']
    file_name = info['file_name']
    file_path = info['file_path']
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('''UPDATE pending_approvals SET status = ?, reviewed_by = ?, reviewed_at = ?
                         WHERE pending_id = ?''',
                      ('rejected', call.from_user.id, datetime.now().isoformat(), pending_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB reject error: {e}")
        safe_notify_user(user_id,
            f"❌ File Rejected\n\n📁 {file_name}\nYour file was not approved.\n\n📞 Contact @{YOUR_USERNAME.replace('@','')} for more info.")
        bot.edit_message_caption(
            f"❌ REJECTED\n\n👤 User: {user_id}\n📁 File: {file_name}",
            call.message.chat.id, info['owner_msg_id']
        )
        bot.answer_callback_query(call.id, B("❌ File rejected."), show_alert=True)
        del pending_files[pending_id]
    except Exception as e:
        logger.error(f"Rejection error: {e}")
        bot.answer_callback_query(call.id, B(f"❌ Error: {str(e)[:50]}"), show_alert=True)

# ================================
# HOST CHOICE CALLBACKS
# ================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('hn:'))
def callback_host_normal(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'host_normal':
            return
        action, user_id, file_name = resolved
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, B("❌ File not found"), show_alert=True)
            return
        file_type = 'py'
        for fname, ftype in user_files.get(user_id, []):
            if fname == file_name:
                file_type = ftype
                break
        bot.answer_callback_query(call.id, B("🚀 Hosting Now..."))
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
        bot.edit_message_text(
            f"🚀 Hosting {file_name}\n✅ Script is starting...\n📂 Check My Files to control it.",
            call.message.chat.id, call.message.message_id
        )
    except Exception as e:
        logger.error(f"Host normal error: {e}")
        bot.answer_callback_query(call.id, B("❌ Error"), show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ht:'))
def callback_host_terminal(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'host_terminal':
            return
        action, user_id, file_name = resolved
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, B("❌ File not found"), show_alert=True)
            return
        file_type = 'py'
        for fname, ftype in user_files.get(user_id, []):
            if fname == file_name:
                file_type = ftype
                break
        bot.answer_callback_query(call.id, B("💻 Hosting with Terminal..."))
        bot.edit_message_text(
            f"💻 Starting {file_name} with Terminal access...",
            call.message.chat.id, call.message.message_id
        )
        if file_type == 'py':
            thread = threading.Thread(target=_start_and_authenticate_terminal,
                                    args=(file_path, user_id, user_folder, file_name, call.message, call))
        elif file_type == 'js':
            thread = threading.Thread(target=_start_js_and_authenticate_terminal,
                                    args=(file_path, user_id, user_folder, file_name, call.message, call))
        thread.start()
    except Exception as e:
        logger.error(f"Host terminal error: {e}")
        bot.answer_callback_query(call.id, B("❌ Error"), show_alert=True)

def _start_and_authenticate_terminal(script_path, user_id, user_folder, file_name, message, call):
    try:
        msg = bot.send_message(message.chat.id, ProgressAnimation.execute_animation()[0])
        for i, frame in enumerate(ProgressAnimation.execute_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        process = subprocess.Popen(
            [sys.executable, script_path], cwd=user_folder,
            stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
            startupinfo=startupinfo, encoding='utf-8', errors='ignore',
            env=env
        )
        script_key = f"{user_id}_{file_name}"
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'user_id': user_id, 'start_time': datetime.now(), 'type': 'py', 'script_key': script_key
        }
        recovery_system.save_running_script(user_id, file_name, script_path, process.pid)
        if user_id not in terminal_sessions:
            terminal_sessions[user_id] = {}
        terminal_sessions[user_id][file_name] = {
            'authenticated': True, 'file_name': file_name
        }
        bot.edit_message_text(
            f"✅ {file_name} started with Terminal access!\n📊 PID: {process.pid}\n\n💻 Terminal is already active!\nSend any command below to interact with your script.\n\n• Type exit to close terminal\n• Type !stop to stop script\n• Type !logs to view logs",
            message.chat.id, msg.message_id
        )
        time.sleep(0.5)
        _show_terminal_interface_simple(message, user_id, file_name)
    except Exception as e:
        logger.error(f"Start terminal script error: {e}")
        bot.send_message(message.chat.id, B(f"❌ Error: {str(e)[:200]}"))

def _start_js_and_authenticate_terminal(script_path, user_id, user_folder, file_name, message, call):
    try:
        msg = bot.send_message(message.chat.id, ProgressAnimation.execute_animation()[0])
        for i, frame in enumerate(ProgressAnimation.execute_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        process = subprocess.Popen(
            ['node', script_path], cwd=user_folder,
            stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
            startupinfo=startupinfo, encoding='utf-8', errors='ignore',
            env=env
        )
        script_key = f"{user_id}_{file_name}"
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'user_id': user_id, 'start_time': datetime.now(), 'type': 'js', 'script_key': script_key
        }
        recovery_system.save_running_script(user_id, file_name, script_path, process.pid)
        if user_id not in terminal_sessions:
            terminal_sessions[user_id] = {}
        terminal_sessions[user_id][file_name] = {
            'authenticated': True, 'file_name': file_name
        }
        bot.edit_message_text(
            f"✅ {file_name} (JS) started with Terminal access!\n📊 PID: {process.pid}\n\n💻 Terminal is already active!\nSend any command below.",
            message.chat.id, msg.message_id
        )
        time.sleep(0.5)
        _show_terminal_interface_simple(message, user_id, file_name)
    except Exception as e:
        logger.error(f"Start JS terminal script error: {e}")
        bot.send_message(message.chat.id, B(f"❌ Error: {str(e)[:200]}"))

# ================================
# PENDING VIEW CALLBACK
# ================================
@bot.callback_query_handler(func=lambda call: call.data == 'view_pending')
def callback_view_pending(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin only"), show_alert=True)
        return
    if not pending_files:
        bot.answer_callback_query(call.id, B("📭 No pending approvals"), show_alert=True)
        return
    text = "⏳ PENDING APPROVALS\n\n"
    markup = InlineKeyboardMarkup(row_width=1)
    for pid, info in pending_files.items():
        text += f"🆔 {pid}\n👤 User: {info['user_id']}\n📁 {info['file_name']}\n⏰ {info['submitted_at'][:19]}\n\n"
        markup.add(make_colored_button(
            B(f"📁 {info['file_name'][:20]} (User {info['user_id']}) | ✅"),
            style="primary",
            callback_data=f'approve_{pid}'
        ))
    markup.add(make_colored_button(B('🔙 Back'), style="primary", callback_data='admin_panel'))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                         reply_markup=markup)

# ================================
# TERMINAL CALLBACKS
# ================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('t:'))
def callback_terminal(call):
    handle_terminal_access(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ct:'))
def callback_close_terminal(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'close_terminal':
            return
        action, user_id, file_name = resolved
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        if user_id in terminal_sessions and file_name in terminal_sessions[user_id]:
            del terminal_sessions[user_id][file_name]
            if not terminal_sessions[user_id]:
                del terminal_sessions[user_id]
        bot.answer_callback_query(call.id, B("🔴 Terminal Closed."))
        bot.edit_message_text(
            f"🔴 Terminal Closed\n\n📁 {file_name}\nSession terminated.",
            call.message.chat.id, call.message.message_id
        )
    except Exception as e:
        logger.error(f"Close terminal error: {e}")
        bot.answer_callback_query(call.id, B("❌ Error"))

@bot.callback_query_handler(func=lambda call: call.data.startswith('cc:'))
def callback_cancel_terminal(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'cancel_terminal':
            return
        action, user_id, file_name = resolved
        if user_id in terminal_sessions and file_name in terminal_sessions[user_id]:
            del terminal_sessions[user_id][file_name]
            if not terminal_sessions[user_id]:
                del terminal_sessions[user_id]
        bot.answer_callback_query(call.id, B("❌ Terminal authentication cancelled."))
        bot.edit_message_text(
            f"❌ Terminal Authentication Cancelled\n\n📁 {file_name}",
            call.message.chat.id, call.message.message_id
        )
    except Exception as e:
        logger.error(f"Cancel terminal error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('rf:'))
def callback_refresh_terminal(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'refresh_terminal':
            return
        action, user_id, file_name = resolved
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        user_folder = get_user_folder(user_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        output_text = f"💻 Terminal - {file_name}\n\n"
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                last_lines = lines[-20:] if len(lines) > 20 else lines
                output_text += "📜 Latest Output:\n```\n"
                output_text += ''.join(last_lines)[:2000]
                output_text += "\n```\n"
        else:
            output_text += "📭 No logs yet.\n"
        output_text += f"\n🟢 Status: {'Running' if is_bot_running(user_id, file_name) else 'Stopped'}"
        bot.answer_callback_query(call.id, B("🔄 Refreshed."))
        bot.edit_message_text(
            output_text,
            call.message.chat.id, call.message.message_id,
            reply_markup=_create_terminal_markup(user_id, file_name)
        )
    except Exception as e:
        logger.error(f"Refresh terminal error: {e}")
        bot.answer_callback_query(call.id, B("❌ Error"))

# ================================
# MESSAGE HANDLER FOR TERMINAL INPUT
# ================================
@bot.message_handler(func=lambda message: _is_terminal_active(message.from_user.id, message.text))
def handle_terminal_command(message):
    user_id = message.from_user.id
    active_file = None
    if user_id in terminal_sessions:
        for fname, session in terminal_sessions[user_id].items():
            if session.get('authenticated'):
                active_file = fname
                break
    if active_file:
        _forward_to_terminal(message, user_id, active_file)

def _is_terminal_active(user_id, text):
    if user_id in terminal_sessions:
        for fname, session in terminal_sessions[user_id].items():
            if session.get('authenticated'):
                if text and text.startswith('/'):
                    return False
                return True
    return False

# ================================
# TEXT HANDLERS (Reply Keyboard)
# ================================
BUTTON_HANDLERS = {
    B("📢 Updates"): lambda m: bot.reply_to(m, f"📢 Update Channel: {UPDATE_CHANNEL}\n👥 Join Group: {UPDATE_GROUP}"),
    B("👥 Join Group"): lambda m: bot.reply_to(m, f"👥 Join Group: {UPDATE_GROUP}"),
    B("📤 Upload"): lambda m: bot.reply_to(m, B("📤 Send your .py, .js, or .zip file.")),
    B("📂 My Files"): lambda m: show_user_files(m),
    B("⚡ Speed"): lambda m: check_speed(m),
    B("📊 Stats"): lambda m: command_stats(m),
    B("👤 Profile"): lambda m: show_profile(m),
    B("🤝 Refer"): lambda m: command_refer(m),
    B("🏆 Leaderboard"): lambda m: command_leaderboard(m),
    B("🔄 Restart All"): lambda m: command_restart_all(m),
    B("👑 Admin"): lambda m: show_admin_panel(m),
    B("💳 Subscription"): lambda m: show_subscription_panel(m),
    B("📢 Broadcast"): lambda m: start_broadcast(m),
    B("🔄 Recover"): lambda m: command_recover_scripts(m),
    B("🚀 Restart Bot"): lambda m: command_restart_bot(m),
    B("⏳ Pending"): lambda m: _inline_view_pending(m),
    B("📞 Contact"): lambda m: bot.reply_to(m, f"📞 Contact: @{YOUR_USERNAME.replace('@', '')}"),
    B("🐙 GitHub"): lambda m: start_github_deploy(m),
}

def _inline_view_pending(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only"))
        return
    if not pending_files:
        bot.reply_to(message, B("📭 No pending approvals."))
        return
    text = "⏳ PENDING APPROVALS\n\n"
    for pid, info in pending_files.items():
        text += f"🆔 {pid}\n👤 User: {info['user_id']}\n📁 {info['file_name']}\n\n"
    markup = InlineKeyboardMarkup()
    markup.add(make_colored_button(B('🔙 Back'), style="primary", callback_data='back_to_main'))
    bot.reply_to(message, text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in BUTTON_HANDLERS)
def handle_button_click(message):
    handler = BUTTON_HANDLERS.get(message.text)
    if handler:
        handler(message)

def show_admin_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    bot.reply_to(message, B("👑 ADMIN PANEL"), reply_markup=create_admin_panel())

def show_subscription_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    bot.reply_to(message, B("💳 SUBSCRIPTION MANAGEMENT"), reply_markup=create_subscription_menu())

def start_broadcast(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    bot.reply_to(message, B("📢 Send the message to broadcast."))
    bot.register_next_step_handler(message, process_broadcast_message)

def process_broadcast_message(message):
    if message.from_user.id not in admin_ids:
        return
    broadcast_text = message.text or message.caption
    if not broadcast_text:
        bot.reply_to(message, B("⚠️ No message."))
        return
    markup = InlineKeyboardMarkup()
    markup.add(
        make_colored_button(B('✅ Confirm'), style="success", callback_data=f'broadcast_confirm_{message.message_id}'),
        make_colored_button(B('❌ Cancel'), style="danger", callback_data='broadcast_cancel')
    )
    preview = broadcast_text[:1000].strip() if broadcast_text else "(Media)"
    bot.reply_to(message, f"📢 Broadcast to {len(active_users)} users?\n\n{preview}", reply_markup=markup)

def check_force_sub(user_id):
    not_joined = []
    for i, channel in enumerate(FORCE_SUB_CHANNELS):
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked', 'banned']:
                not_joined.append((channel, FORCE_SUB_CHANNEL_LINKS[i], FORCE_SUB_CHANNEL_NAMES[i]))
        except:
            not_joined.append((channel, FORCE_SUB_CHANNEL_LINKS[i], FORCE_SUB_CHANNEL_NAMES[i]))
    return not_joined

# ================================
# CALLBACK FUNCTIONS
# ================================
def upload_callback(call):
    user_id = call.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        bot.answer_callback_query(call.id, B(f"⚠️ Limit reached ({current_files}/{file_limit})"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("📤 Send your .py, .js, or .zip file."))

def check_files_callback(call):
    user_id = call.from_user.id
    files = user_files.get(user_id, [])
    if not files:
        bot.answer_callback_query(call.id, B("📭 No files"), show_alert=True)
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in files:
        is_running = is_bot_running(user_id, file_name)
        status = "🟢 Running" if is_running else "🔴 Stopped"
        k = cb_store('file', user_id, file_name)
        markup.add(make_colored_button(B(f"{file_name} ({file_type}) - {status}"),
                                        style="success" if is_running else "danger",
                                        callback_data=f'f:{k}'))
    markup.add(make_colored_button(B("🔙 Back"), style="primary", callback_data='back_to_main'))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(B("📂 Your Files:"), call.message.chat.id, call.message.message_id, reply_markup=markup)

def file_control_callback(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'file':
            return
        action, uid, file_name = resolved
        if call.from_user.id != uid and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        is_running = is_bot_running(uid, file_name)
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"⚙️ Controls for: {file_name}\n📊 Status: {'🟢 Running' if is_running else '🔴 Stopped'}",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(uid, file_name, is_running)
        )
    except Exception as e:
        logger.error(f"File control error: {e}")

def start_bot_callback(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'start':
            return
        action, uid, file_name = resolved
        if call.from_user.id != uid and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        if is_bot_running(uid, file_name):
            bot.answer_callback_query(call.id, B("✅ Already running"), show_alert=True)
            return
        user_folder = get_user_folder(uid)
        file_path = os.path.join(user_folder, file_name)
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, B("❌ File not found"), show_alert=True)
            return
        file_type = 'py'
        for fname, ftype in user_files.get(uid, []):
            if fname == file_name:
                file_type = ftype
                break
        bot.answer_callback_query(call.id, B("🚀 Starting..."))
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, uid, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, uid, user_folder, file_name, call.message)).start()
    except Exception as e:
        logger.error(f"Start error: {e}")

def stop_bot_callback(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'stop':
            return
        action, uid, file_name = resolved
        if call.from_user.id != uid and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        if not is_bot_running(uid, file_name):
            bot.answer_callback_query(call.id, B("✅ Already stopped"), show_alert=True)
            return
        script_key = f"{uid}_{file_name}"
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            if script_key in bot_scripts:
                del bot_scripts[script_key]
        bot.answer_callback_query(call.id, B("🛑 Stopped"))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(uid, file_name, False))
    except Exception as e:
        logger.error(f"Stop error: {e}")

def restart_bot_callback(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'restart':
            return
        action, uid, file_name = resolved
        if call.from_user.id != uid and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        if is_bot_running(uid, file_name):
            script_key = f"{uid}_{file_name}"
            if script_key in bot_scripts:
                kill_process_tree(bot_scripts[script_key])
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            time.sleep(1)
        user_folder = get_user_folder(uid)
        file_path = os.path.join(user_folder, file_name)
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, B("❌ File not found"), show_alert=True)
            return
        file_type = 'py'
        for fname, ftype in user_files.get(uid, []):
            if fname == file_name:
                file_type = ftype
                break
        bot.answer_callback_query(call.id, B("🔄 Restarting..."))
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, uid, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, uid, user_folder, file_name, call.message)).start()
    except Exception as e:
        logger.error(f"Restart error: {e}")

def delete_bot_callback(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'delete':
            return
        action, uid, file_name = resolved
        if call.from_user.id != uid and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        if is_bot_running(uid, file_name):
            script_key = f"{uid}_{file_name}"
            if script_key in bot_scripts:
                kill_process_tree(bot_scripts[script_key])
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
        user_folder = get_user_folder(uid)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(log_path):
            os.remove(log_path)
        remove_user_file_db(uid, file_name)
        if uid in terminal_sessions and file_name in terminal_sessions[uid]:
            del terminal_sessions[uid][file_name]
            if not terminal_sessions[uid]:
                del terminal_sessions[uid]
        bot.answer_callback_query(call.id, B("🗑️ Deleted"))
        check_files_callback(call)
    except Exception as e:
        logger.error(f"Delete error: {e}")

def logs_bot_callback(call):
    try:
        resolved = cb_resolve(call.data)
        if not resolved or resolved[0] != 'logs':
            return
        action, uid, file_name = resolved
        if call.from_user.id != uid and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        user_folder = get_user_folder(uid)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, B("📭 No logs"), show_alert=True)
            return
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        if len(content) > 3000:
            content = content[-3000:]
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📜 Logs for {file_name}:\n```\n{content}\n```")
    except Exception as e:
        logger.error(f"Logs error: {e}")

def speed_callback(call):
    start_time = time.time()
    bot.answer_callback_query(call.id)
    latency = round((time.time() - start_time) * 1000, 2)
    bot.edit_message_text(f"⚡ Bot Speed\n\n⏱️ Latency: {latency}ms\n🔒 Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}", call.message.chat.id, call.message.message_id)

def stats_callback(call):
    total_users = _get_db_user_count()
    total_files = sum(len(files) for files in user_files.values())
    running_scripts = len([k for k, v in bot_scripts.items() if is_bot_running(v['user_id'], v['file_name'])])
    recovery_count = recovery_system.get_running_count()
    referral_users = 0
    auto_restart_enabled = 0
    for uid in active_users:
        if referral_system.get_referral_count(uid) > 0:
            referral_users += 1
        if referral_system.is_auto_restart_enabled(uid):
            auto_restart_enabled += 1
    stats_text = f"""
📊 SYSTEM STATS
👥 Total Users: {total_users}
📁 Total Files: {total_files}
🟢 Running: {running_scripts}
💾 Recovery: {recovery_count}
🔒 Bot: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}
🤝 Referring: {referral_users}
🔄 Auto-Recovery: {auto_restart_enabled}
⏳ Pending: {len(pending_files)}
"""
    bot.answer_callback_query(call.id)
    bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id)

def profile_callback(call):
    user_id = call.from_user.id
    tier = get_user_tier(user_id)
    tier_info = TIER_SYSTEM[tier]
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    user_rank = referral_system.get_user_rank(user_id)
    profile_text = f"""
👤 PROFILE
🆔 ID: {user_id}
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}
🤝 Referrals: {referral_count}/3
🏆 Rank: #{user_rank if user_rank else 'N/A'}
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}
"""
    bot.answer_callback_query(call.id)
    bot.edit_message_text(profile_text, call.message.chat.id, call.message.message_id)

def refer_callback(call):
    user_id = call.from_user.id
    tier = get_user_tier(user_id)
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    markup, referral_link = create_referral_menu(user_id)
    refer_text = f"""
🤝 REFERRAL SYSTEM
🆔 Your ID: {user_id}
📊 Count: {referral_count}/3
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}
🔗 Link: {referral_link}
"""
    bot.answer_callback_query(call.id)
    bot.edit_message_text(refer_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def leaderboard_callback(call):
    command_leaderboard(call.message)
    bot.answer_callback_query(call.id)

def refresh_leaderboard_callback(call):
    leaderboard_callback(call)

def my_rank_callback(call):
    user_id = call.from_user.id
    user_rank = referral_system.get_user_rank(user_id)
    referral_count = referral_system.get_referral_count(user_id)
    rank_text = f"🏆 Rank: #{user_rank if user_rank else 'N/A'}\n👥 Referrals: {referral_count}/3"
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, rank_text)

def copy_referral_callback(call):
    try:
        user_id = int(call.data.split('_')[2])
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        code = referral_system.get_referral_code(user_id)
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={code}"
        bot.answer_callback_query(call.id, B("🔗 Copied!"), show_alert=True)
        bot.send_message(call.message.chat.id, f"🔗 Your Referral Link:\n{link}")
    except Exception as e:
        logger.error(f"Copy error: {e}")

def qr_referral_callback(call):
    try:
        user_id = int(call.data.split('_')[2])
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        code = referral_system.get_referral_code(user_id)
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={code}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        bot.answer_callback_query(call.id, B("📱 Generating QR..."))
        bot.send_photo(call.message.chat.id, photo=bio, caption=f"📱 QR Code\n{link}")
    except Exception as e:
        logger.error(f"QR error: {e}")

def check_referrals_callback(call):
    try:
        user_id = int(call.data.split('_')[2])
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
            return
        count = referral_system.get_referral_count(user_id)
        auto_restart = referral_system.is_auto_restart_enabled(user_id)
        text = f"👥 Referrals: {count}/3\n🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}\n\n📌 Need: {max(0, 3 - count)} more"
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text)
    except Exception as e:
        logger.error(f"Check referrals error: {e}")

def restart_all_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    msg = bot.send_message(call.message.chat.id, B("🔄 Restarting all..."))
    restarted = 0
    for uid, files in user_files.items():
        for fname, ftype in files:
            if is_bot_running(uid, fname):
                sk = f"{uid}_{fname}"
                if sk in bot_scripts:
                    kill_process_tree(bot_scripts[sk])
                    del bot_scripts[sk]
            uf = get_user_folder(uid)
            fp = os.path.join(uf, fname)
            if os.path.exists(fp):
                if ftype == 'py':
                    threading.Thread(target=run_script, args=(fp, uid, uf, fname, call.message)).start()
                elif ftype == 'js':
                    threading.Thread(target=run_js_script, args=(fp, uid, uf, fname, call.message)).start()
                restarted += 1
                time.sleep(0.5)
    bot.edit_message_text(B(f"✅ Restarted {restarted} scripts."), call.message.chat.id, msg.message_id)
    bot.answer_callback_query(call.id)

def admin_panel_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(B("👑 ADMIN PANEL"), call.message.chat.id, call.message.message_id, reply_markup=create_admin_panel())

def subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(B("💳 SUBSCRIPTION MANAGEMENT"), call.message.chat.id, call.message.message_id, reply_markup=create_subscription_menu())

def broadcast_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("📢 Send message to broadcast."))
    bot.register_next_step_handler(call.message, process_broadcast_message)

def lock_bot_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    global bot_locked
    bot_locked = True
    bot.answer_callback_query(call.id, B("🔒 Locked"))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))

def unlock_bot_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    global bot_locked
    bot_locked = False
    bot.answer_callback_query(call.id, B("🔓 Unlocked"))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))

def recover_all_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    msg = bot.send_message(call.message.chat.id, ProgressAnimation.recovery_animation()[0])
    for i, frame in enumerate(ProgressAnimation.recovery_animation()):
        try:
            bot.edit_message_text(frame, call.message.chat.id, msg.message_id)
            time.sleep(0.3)
        except:
            pass
    recovered = recovery_system.recover_all_scripts()
    if recovered:
        bot.edit_message_text(B(f"✅ Recovered {len(recovered)} scripts."), call.message.chat.id, msg.message_id)
    else:
        bot.edit_message_text(B("📭 Nothing to recover."), call.message.chat.id, msg.message_id)
    bot.answer_callback_query(call.id)

def analytics_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    total_users = len(active_users)
    total_files = sum(len(files) for files in user_files.values())
    running_scripts = len([k for k, v in bot_scripts.items() if is_bot_running(v['user_id'], v['file_name'])])
    referral_users = 0
    auto_restart_enabled = 0
    total_referrals = 0
    for uid in active_users:
        count = referral_system.get_referral_count(uid)
        if count > 0:
            referral_users += 1
            total_referrals += count
        if referral_system.is_auto_restart_enabled(uid):
            auto_restart_enabled += 1
    text = f"""
📈 ANALYTICS
👥 Users: {total_users}
📁 Files: {total_files}
🟢 Running: {running_scripts}
🤝 Referrals: {total_referrals}
🔄 Auto-Restart: {auto_restart_enabled}
⏳ Pending: {len(pending_files)}
"""
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

def add_admin_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, B("⚠️ Owner only"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("👑 Enter user ID to add as admin:"))
    bot.register_next_step_handler(call.message, process_add_admin)

def process_add_admin(message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        admin_id = int(message.text.strip())
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)',
                      (admin_id, message.from_user.id, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        admin_ids.add(admin_id)
        bot.reply_to(message, B(f"✅ {admin_id} added as admin."))
    except:
        bot.reply_to(message, B("❌ Invalid ID."))

def remove_admin_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, B("⚠️ Owner only"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("👑 Enter user ID to remove from admin:"))
    bot.register_next_step_handler(call.message, process_remove_admin)

def process_remove_admin(message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        admin_id = int(message.text.strip())
        if admin_id == OWNER_ID:
            bot.reply_to(message, B("❌ Cannot remove owner."))
            return
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
            conn.commit()
            conn.close()
        admin_ids.discard(admin_id)
        bot.reply_to(message, B(f"✅ {admin_id} removed from admin."))
    except:
        bot.reply_to(message, B("❌ Invalid ID."))

def ban_user_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, B("⚠️ Owner only"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("🚫 Enter user ID to ban:"))
    bot.register_next_step_handler(call.message, process_ban_user)

def process_ban_user(message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        uid = int(message.text.strip())
        if uid == OWNER_ID:
            bot.reply_to(message, B("❌ Cannot ban owner."))
            return
        ban_user(uid)
        bot.reply_to(message, B(f"🚫 User {uid} banned. All their scripts stopped."))
        try:
            bot.send_message(uid, B("🚫 You have been banned from this bot."))
        except:
            pass
    except:
        bot.reply_to(message, B("❌ Invalid ID."))

def unban_user_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, B("⚠️ Owner only"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("✅ Enter user ID to unban:"))
    bot.register_next_step_handler(call.message, process_unban_user)

def process_unban_user(message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        uid = int(message.text.strip())
        unban_user(uid)
        bot.reply_to(message, B(f"✅ User {uid} unbanned."))
    except:
        bot.reply_to(message, B("❌ Invalid ID."))

def banned_list_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, B("⚠️ Owner only"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    if not banned_users:
        bot.send_message(call.message.chat.id, B("📭 No banned users."))
    else:
        text = "🚫 BANNED USERS\n\n" + "\n".join(f"• {uid}" for uid in sorted(banned_users))
        bot.send_message(call.message.chat.id, text)

def list_admins_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    admin_list = "\n".join([f"• {a} {'👑' if a == OWNER_ID else ''}" for a in sorted(admin_ids)])
    bot.answer_callback_query(call.id)
    bot.edit_message_text(f"👑 Admins:\n{admin_list}", call.message.chat.id, call.message.message_id)

def system_stats_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    cpu = 0
    mem_percent = 0
    mem_used = 0
    mem_total = 0
    disk_percent = 0
    disk_used = 0
    disk_total = 0
    if HAS_PSUTIL:
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            mem_percent = mem.percent
            mem_used = round(mem.used/1024**3,1)
            mem_total = round(mem.total/1024**3,1)
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = round(disk.used/1024**3,1)
            disk_total = round(disk.total/1024**3,1)
        except:
            pass
    text = f"""
🖥️ SYSTEM STATS
💻 CPU: {cpu}%
🧠 Memory: {mem_percent}% ({mem_used}/{mem_total}GB)
💾 Disk: {disk_percent}% ({disk_used}/{disk_total}GB)
🧵 Threads: {threading.active_count()}
"""
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

def all_files_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, B("⚠️ Owner only"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id, file_name, file_type FROM user_files ORDER BY user_id, file_name')
        db_files = c.fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"DB fetch error in all_files: {e}")
        bot.edit_message_text(B("❌ Database error."), call.message.chat.id, call.message.message_id)
        return
    if not db_files:
        bot.edit_message_text(B("📭 No files on server."), call.message.chat.id, call.message.message_id)
        return
    markup = InlineKeyboardMarkup(row_width=1)
    text = "📁 ALL FILES ON SERVER\n\n"
    current_uid = None
    total = 0
    for uid, fname, ftype in db_files:
        if uid != current_uid:
            if current_uid is not None:
                text += "\n"
            text += f"👤 User: {uid}\n"
            current_uid = uid
        total += 1
        running = is_bot_running(uid, fname)
        status = "🟢" if running else "🔴"
        text += f"  {status} {fname} ({ftype})\n"
        k = cb_store('file', uid, fname)
        markup.add(make_colored_button(B(f"{status} {fname} ({ftype})"),
                                        style="success" if running else "danger",
                                        callback_data=f'f:{k}'))
    text += f"\n━━━━━━━━━━━━━━\n📊 Total Files: {total}"
    markup.add(make_colored_button(B('🔙 Back'), style="primary", callback_data='admin_panel'))
    try:
        if len(text) > 3500:
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
        else:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    except Exception as e:
        logger.error(f"all_files display error: {e}")
        bot.send_message(call.message.chat.id, text, reply_markup=markup)

def add_subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("💳 Enter user_ID days (e.g. 12345 30):"))
    bot.register_next_step_handler(call.message, process_add_subscription)

def process_add_subscription(message):
    if message.from_user.id not in admin_ids:
        return
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            bot.reply_to(message, B("❌ Format: user_ID days"))
            return
        uid = int(parts[0])
        days = int(parts[1])
        expiry = datetime.now() + timedelta(days=days)
        save_subscription(uid, expiry, 'premium')
        bot.reply_to(message, B(f"✅ Sub for {uid} until {expiry.strftime('%Y-%m-%d')}"))
    except:
        bot.reply_to(message, B("❌ Invalid."))

def remove_subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("💳 Enter user ID to remove subscription:"))
    bot.register_next_step_handler(call.message, process_remove_subscription)

def process_remove_subscription(message):
    if message.from_user.id not in admin_ids:
        return
    try:
        uid = int(message.text.strip())
        remove_subscription_db(uid)
        bot.reply_to(message, B(f"✅ Subscription removed for {uid}"))
    except:
        bot.reply_to(message, B("❌ Invalid."))

def check_subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("💳 Enter user ID to check subscription:"))
    bot.register_next_step_handler(call.message, process_check_subscription)

def process_check_subscription(message):
    if message.from_user.id not in admin_ids:
        return
    try:
        uid = int(message.text.strip())
        if uid in user_subscriptions:
            sub = user_subscriptions[uid]
            expiry = sub.get('expiry')
            tier = sub.get('tier', 'premium')
            if expiry and expiry > datetime.now():
                days = (expiry - datetime.now()).days
                bot.reply_to(message, f"✅ Active Subscription\n🎫 Tier: {tier}\n📅 Expires: {expiry.strftime('%Y-%m-%d')}\n⏳ Days left: {days}")
            else:
                bot.reply_to(message, B(f"⚠️ Expired"))
                remove_subscription_db(uid)
        else:
            bot.reply_to(message, B("📭 No subscription found."))
    except:
        bot.reply_to(message, B("❌ Invalid."))

def view_user_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    try:
        uid = int(call.data.split('_')[2])
        tier = get_user_tier(uid)
        files = user_files.get(uid, [])
        running = len([1 for f in files if is_bot_running(uid, f[0])])
        text = f"""
👤 USER INFO
🆔 ID: {uid}
🎫 Tier: {TIER_SYSTEM[tier]['icon']} {tier}
📁 Files: {len(files)}
🟢 Running: {running}
🤝 Referrals: {referral_system.get_referral_count(uid)}
"""
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text)
    except Exception as e:
        logger.error(f"View user error: {e}")

def broadcast_confirm_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    try:
        original = call.message.reply_to_message
        if not original:
            bot.answer_callback_query(call.id, B("❌ No message"), show_alert=True)
            return
        bot.answer_callback_query(call.id, B("🚀 Broadcasting..."))
        sent = 0
        failed = 0
        for uid in list(active_users):
            try:
                if original.text:
                    bot.send_message(uid, original.text)
                elif original.caption:
                    if original.photo:
                        bot.send_photo(uid, original.photo[-1].file_id, caption=original.caption)
                    elif original.document:
                        bot.send_document(uid, original.document.file_id, caption=original.caption)
                sent += 1
            except:
                failed += 1
            time.sleep(0.1)
        bot.edit_message_text(f"✅ Broadcast done\n📤 Sent: {sent}\n❌ Failed: {failed}", call.message.chat.id, call.message.message_id)
    except Exception as e:
        logger.error(f"Broadcast error: {e}")

def broadcast_cancel_callback(call):
    bot.answer_callback_query(call.id, B("❌ Cancelled"))
    bot.delete_message(call.message.chat.id, call.message.message_id)

def restart_bot_callback_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Denied"), show_alert=True)
        return
    bot.answer_callback_query(call.id, B("🔄 Restarting..."))
    msg = bot.send_message(call.message.chat.id, B("🔄 Bot is restarting..."))
    time.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)

def back_to_main_callback(call):
    bot.answer_callback_query(call.id)
    try:
        user_id = call.from_user.id
        user_name = call.from_user.first_name or "User"
        tier = get_user_tier(user_id)
        tier_info = TIER_SYSTEM[tier]
        referral_count = referral_system.get_referral_count(user_id)
        text = B(f"""
🚀 CYBERX HOSTING BOT V3.5 🚀

━━━━━━━━━━━━━━━━
👤 Welcome, {user_name}!
🆔 ID: {user_id}
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}
🤝 Referrals: {referral_count}/3
🔄 Auto-Restart: {'✅' if (tier != 'free' or referral_system.is_auto_restart_enabled(user_id)) else '❌'}
━━━━━━━━━━━━━━━━

📤 Send .py / .js to host
👑 Owner: {YOUR_USERNAME}
""")
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                            reply_markup=create_main_menu_inline(user_id))
    except Exception as e:
        logger.error(f"Back to main error: {e}")

# ================================
# TEXT COMMAND HANDLERS (Reply Keyboard)
# ================================
@bot.message_handler(func=lambda m: m.text == B("📁 My Files") or m.text == B("📂 My Files") or m.text == "My Files")
def text_myfiles(message):
    show_user_files(message)

@bot.message_handler(func=lambda m: m.text == B("📤 Upload") or m.text == "Upload")
def text_upload(message):
    bot.reply_to(message, B("📤 Send your .py or .js file."))

@bot.message_handler(func=lambda m: m.text == B("👤 Profile") or m.text == "Profile")
def text_profile(message):
    show_profile(message)

@bot.message_handler(func=lambda m: m.text == B("🤝 Refer") or m.text == "Refer")
def text_refer(message):
    command_refer(message)

@bot.message_handler(func=lambda m: m.text == B("🏆 Leaderboard") or m.text == "Leaderboard")
def text_leaderboard(message):
    command_leaderboard(message)

@bot.message_handler(func=lambda m: m.text == B("⚡ Speed") or m.text == "Speed")
def text_speed(message):
    check_speed(message)

@bot.message_handler(func=lambda m: m.text == B("📊 Stats") or m.text == "Stats")
def text_stats(message):
    command_stats(message)

@bot.message_handler(func=lambda m: m.text == B("👑 Admin") or m.text == "Admin" or m.text == B("👑 Admin Panel"))
def text_admin(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    show_admin_panel(message)

@bot.message_handler(func=lambda m: m.text == B("🔒 Lock") or m.text == B("🔓 Unlock"))
def text_lock(message):
    global bot_locked
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    bot_locked = not bot_locked
    status = "🔒 Locked" if bot_locked else "🔓 Unlocked"
    bot.reply_to(message, B(f"✅ Bot {status}"))

@bot.message_handler(func=lambda m: m.text == B("🔄 Restart All"))
def text_restart_all(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    command_restart_all(message)

@bot.message_handler(func=lambda m: m.text == B("🔄 Recover"))
def text_recover(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    command_recover_scripts(message)

@bot.message_handler(func=lambda m: m.text == B("🚀 Restart Bot"))
def text_restart_bot(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    command_restart_bot(message)

@bot.message_handler(func=lambda m: m.text == B("📢 Updates"))
def text_updates(message):
    bot.reply_to(message, f"📢 Updates: {UPDATE_CHANNEL}\n👥 Group: {UPDATE_GROUP}")

@bot.message_handler(func=lambda m: m.text == B("📞 Contact"))
def text_contact(message):
    bot.reply_to(message, f"📞 Contact: {YOUR_USERNAME}")

@bot.message_handler(func=lambda m: m.text == B("📈 Analytics"))
def text_analytics(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    analytics_callback(None)

@bot.message_handler(func=lambda m: m.text == B("💳 Subscription") or m.text == B("💳 Subscriptions"))
def text_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    show_subscription_panel(message)

@bot.message_handler(func=lambda m: m.text == B("📢 Broadcast"))
def text_broadcast(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    start_broadcast(message)

@bot.message_handler(func=lambda m: m.text == B("⏳ Pending"))
def text_pending(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin only."))
        return
    _inline_view_pending(message)

@bot.message_handler(func=lambda m: m.text == B("👥 Join Group"))
def text_join(message):
    bot.reply_to(message, f"👥 Join: {UPDATE_GROUP}")

@bot.message_handler(func=lambda m: m.text == B("🐙 GitHub"))
def text_github(message):
    start_github_deploy(message)

# ================================
# COMMAND HELPERS
# ================================
def show_user_files(message):
    user_id = message.from_user.id
    files = user_files.get(user_id, [])
    if not files:
        bot.reply_to(message, B("📭 No files uploaded yet.\n\nSend a .py or .js file to get started!"))
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in files:
        running = is_bot_running(user_id, file_name)
        status = "🟢" if running else "🔴"
        k = cb_store('file', user_id, file_name)
        markup.add(make_colored_button(B(f"{status} {file_name} ({file_type})"),
                                        style="success" if running else "danger",
                                        callback_data=f'f:{k}'))
    markup.add(make_colored_button(B("🔙 Back"), style="primary", callback_data='back_to_main'))
    bot.reply_to(message, B("📂 Your Files:"), reply_markup=markup)

def show_profile(message):
    user_id = message.from_user.id
    tier = get_user_tier(user_id)
    tier_info = TIER_SYSTEM[tier]
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    running, total = get_running_status(user_id)
    rank = referral_system.get_user_rank(user_id)
    text = f"""
👤 YOUR PROFILE
━━━━━━━━━━━━━━━━
🆔 ID: {user_id}
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}
🟢 Running: {running}/{total}
🤝 Referrals: {referral_count}/3
🏆 Rank: #{rank if rank else 'N/A'}
🔄 Auto-Restart: {'✅ Enabled ✅' if auto_restart else '❌ Disabled ❌'}
━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, text)

def get_running_status(user_id):
    files = user_files.get(user_id, [])
    running = 0
    for fname, ftype in files:
        if is_bot_running(user_id, fname):
            running += 1
    return running, len(files)

def check_speed(message):
    start = time.time()
    msg = bot.reply_to(message, B("⚡ Checking speed..."))
    elapsed = round((time.time() - start) * 1000, 2)
    bot.edit_message_text(f"⚡ Bot Speed\n\n⏱️ Latency: {elapsed}ms\n🔒 Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}",
                        message.chat.id, msg.message_id)

def command_stats(message):
    total_users = _get_db_user_count()
    total_files = sum(len(f) for f in user_files.values())
    running = len([k for k, v in bot_scripts.items() if is_bot_running(v['user_id'], v['file_name'])])
    text = f"""
📊 SYSTEM STATS
━━━━━━━━━━━━━━━━
👥 Users: {total_users}
📁 Files: {total_files}
🟢 Running: {running}
🔒 Bot: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}
⏳ Pending: {len(pending_files)}
━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, text)

def command_refer(message):
    user_id = message.from_user.id
    count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id)
    markup, link = create_referral_menu(user_id)
    text = f"""
🤝 REFERRAL SYSTEM
━━━━━━━━━━━━━━━━
📊 Your Referrals: {count}/3
🔄 Auto-Restart: {'✅ Unlocked ✅' if auto_restart else '❌ Locked (need 3)'}
━━━━━━━━━━━━━━━━
🔗 Your Link: {link}
━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, text, reply_markup=markup)

def command_leaderboard(message):
    top = referral_system.get_top_referrers(10)
    text = "🏆 LEADERBOARD\n━━━━━━━━━━━━━━━━\n"
    if not top:
        text += "📭 No referrals yet.\n"
    else:
        for i, entry in enumerate(top, 1):
            medal = ""
            if i == 1: medal = "🥇"
            elif i == 2: medal = "🥈"
            elif i == 3: medal = "🥉"
            uname = entry.get('username', '') or f"User {entry['user_id']}"
            text += f"{medal} #{i} | {uname[:15]} | 👥 {entry['count']}\n"
    text += "━━━━━━━━━━━━━━━━\nRefer 3 to unlock Auto-Restart!"
    markup = create_leaderboard_markup()
    bot.reply_to(message, text, reply_markup=markup)

def command_restart_all(message):
    bot.reply_to(message, B("🔄 Restarting all scripts..."))
    restarted = 0
    for uid, files in user_files.items():
        for fname, ftype in files:
            script_key = f"{uid}_{fname}"
            if script_key in bot_scripts:
                try:
                    kill_process_tree(bot_scripts[script_key])
                except:
                    pass
                del bot_scripts[script_key]
            user_folder = get_user_folder(uid)
            file_path = os.path.join(user_folder, fname)
            if os.path.exists(file_path):
                log_path = os.path.join(user_folder, f"{os.path.splitext(fname)[0]}.log")
                log_file = open(log_path, 'a', encoding='utf-8', errors='ignore')
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                interpreter = [sys.executable] if ftype == 'py' else ['node']
                proc = subprocess.Popen(
                    interpreter + [file_path],
                    cwd=user_folder,
                    stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                    startupinfo=startupinfo, encoding='utf-8', errors='ignore',
                    env=env
                )
                bot_scripts[script_key] = {
                    'process': proc, 'log_file': log_file, 'file_name': fname,
                    'user_id': uid, 'start_time': datetime.now(),
                    'type': ftype, 'script_key': script_key
                }
                recovery_system.save_running_script(uid, fname, file_path, proc.pid)
                restarted += 1
                time.sleep(0.3)
    bot.send_message(message.chat.id, B(f"✅ {restarted} scripts restarted."))

def command_recover_scripts(message):
    msg = bot.reply_to(message, ProgressAnimation.recovery_animation()[0])
    for i, frame in enumerate(ProgressAnimation.recovery_animation()):
        try:
            bot.edit_message_text(frame, message.chat.id, msg.message_id)
            time.sleep(0.3)
        except:
            pass
    recovered = recovery_system.recover_all_scripts()
    bot.edit_message_text(f"✅ Recovered {len(recovered)} scripts." if recovered else "📭 Nothing to recover.",
                        message.chat.id, msg.message_id)

def command_restart_bot(message):
    msg = bot.reply_to(message, B("🔄 Restarting bot..."))
    send_restart_notification()
    time.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)

# ================================
# FILE UPLOAD HANDLER
# ================================
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        bot.reply_to(message, B("🚫 You are banned."))
        return
    not_joined = check_force_sub(user_id)
    if not_joined:
        markup = InlineKeyboardMarkup(row_width=1)
        for channel_tag, channel_link, channel_name in not_joined:
            markup.add(make_colored_button(f"🔵 Join {channel_name}", style="primary", url=channel_link))
        markup.add(make_colored_button("✅ Click Here After Joining ✅", style="success", callback_data='check_force_sub_start'))
        bot.reply_to(message, B("⚠️ JOIN CHANNELS FIRST\n\nYou must join these channels to upload:"), reply_markup=markup)
        return
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, B("🔒 Bot is locked. Try again later."))
        return
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        bot.reply_to(message, B(f"⚠️ File limit reached ({current_files}/{file_limit}).\nDelete some files or upgrade tier."))
        return
    doc = message.document
    if not doc.file_name:
        bot.reply_to(message, B("⚠️ No file name found."))
        return
    file_ext = os.path.splitext(doc.file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, B("⚠️ Only .py, .js, or .zip files allowed."))
        return
    msg = bot.reply_to(message, B("⏳ Downloading file..."))
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        if user_id in admin_ids:
            user_folder = get_user_folder(user_id)
            file_path = os.path.join(user_folder, doc.file_name)
            with open(file_path, 'wb') as f:
                f.write(downloaded)
            if file_ext == '.zip':
                import io
                z = zipfile.ZipFile(io.BytesIO(downloaded))
                z.extractall(user_folder)
                py_files = [f for f in z.namelist() if f.endswith('.py')]
                js_files = [f for f in z.namelist() if f.endswith('.js')]
                main_file = None
                main_type = None
                for name in ['main.py', 'bot.py', 'app.py']:
                    if name in py_files:
                        main_file = name
                        main_type = 'py'
                        break
                if not main_file and py_files:
                    main_file = py_files[0]
                    main_type = 'py'
                elif not main_file and js_files:
                    for name in ['index.js', 'main.js', 'bot.js']:
                        if name in js_files:
                            main_file = name
                            main_type = 'js'
                            break
                    if not main_file and js_files:
                        main_file = js_files[0]
                        main_type = 'js'
                if main_file:
                    save_user_file(user_id, main_file, main_type)
                    file_path = os.path.join(user_folder, main_file)
                    bot.edit_message_text(f"✅ ZIP extracted. Starting {main_file}...", message.chat.id, msg.message_id)
                    if main_type == 'py':
                        threading.Thread(target=run_script, args=(file_path, user_id, user_folder, main_file, message)).start()
                    else:
                        threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, main_file, message)).start()
                else:
                    bot.edit_message_text(B("❌ No .py or .js found in ZIP."), message.chat.id, msg.message_id)
            else:
                if file_ext == '.py':
                    save_user_file(user_id, doc.file_name, 'py')
                    bot.edit_message_text(f"✅ Uploaded. Starting {doc.file_name}...", message.chat.id, msg.message_id)
                    threading.Thread(target=run_script, args=(file_path, user_id, user_folder, doc.file_name, message)).start()
                elif file_ext == '.js':
                    save_user_file(user_id, doc.file_name, 'js')
                    bot.edit_message_text(f"✅ Uploaded. Starting {doc.file_name}...", message.chat.id, msg.message_id)
                    threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, doc.file_name, message)).start()
        else:
            pending_id = f"P{int(time.time())}{random.randint(100,999)}"
            pending_file_path = os.path.join(PENDING_DIR, f"{pending_id}_{doc.file_name}")
            with open(pending_file_path, 'wb') as f:
                f.write(downloaded)
            pending_files[pending_id] = {
                "user_id": user_id,
                "file_name": doc.file_name,
                "file_path": pending_file_path,
                "file_ext": file_ext,
                "status": "pending",
                "submitted_at": datetime.now().isoformat()
            }
            owner_markup = InlineKeyboardMarkup(row_width=2)
            owner_markup.add(
                make_colored_button(B("✅ Approve"), style="success", callback_data=f'approve_{pending_id}'),
                make_colored_button(B("❌ Reject"), style="danger", callback_data=f'reject_{pending_id}')
            )
            owner_text = f"""
⏳ NEW APPROVAL REQUEST
━━━━━━━━━━━━━━━━
👤 User: {user_id}
📁 File: {doc.file_name}
📂 Type: {file_ext}
📊 Files: {current_files}/{file_limit}
🎫 Tier: {TIER_SYSTEM[get_user_tier(user_id)]['icon']}
━━━━━━━━━━━━━━━━
"""
            bot.send_document(OWNER_ID, doc.file_id, caption=owner_text, reply_markup=owner_markup)
            bot.edit_message_text(f"📤 File Sent for Approval!\n\n📁 {doc.file_name}\n⏳ Waiting for owner to approve...\n\nYou'll be notified when approved.",
                                message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Upload Error: {str(e)[:200]}", message.chat.id, msg.message_id)
        logger.error(f"Upload error: {e}")

# ================================
# SINGLE CATCH-ALL CALLBACK QUERY HANDLER
# ================================
@bot.callback_query_handler(func=lambda call: True)
def main_callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    if is_user_banned(user_id):
        try:
            bot.answer_callback_query(call.id, B("🚫 You are banned."), show_alert=True)
        except:
            pass
        return
    try:
        if data == "check_files":
            check_files_callback(call)
        elif data == "upload":
            bot.answer_callback_query(call.id, B("📤 Send a .py, .js, or .zip file."))
        elif data == "profile":
            profile_callback(call)
        elif data == "refer":
            refer_callback(call)
        elif data == "leaderboard":
            leaderboard_callback(call)
        elif data == "refresh_leaderboard":
            refresh_leaderboard_callback(call)
        elif data == "github":
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, B("🐙 GitHub Deployment\n\nSend me your GitHub repository URL:"))
            bot.register_next_step_handler(call.message, process_github_url)
        elif data == "my_rank":
            my_rank_callback(call)
        elif data == "speed":
            speed_callback(call)
        elif data == "stats":
            stats_callback(call)
        elif data == "admin_panel":
            admin_panel_callback(call)
        elif data == "subscription":
            subscription_callback(call)
        elif data == "broadcast":
            broadcast_callback(call)
        elif data == "lock_bot":
            lock_bot_callback(call)
        elif data == "unlock_bot":
            unlock_bot_callback(call)
        elif data == "recover_all":
            recover_all_callback(call)
        elif data == "analytics":
            analytics_callback(call)
        elif data == "add_admin":
            add_admin_callback(call)
        elif data == "remove_admin":
            remove_admin_callback(call)
        elif data == "list_admins":
            list_admins_callback(call)
        elif data == "system_stats":
            system_stats_callback(call)
        elif data == "add_subscription":
            add_subscription_callback(call)
        elif data == "remove_subscription":
            remove_subscription_callback(call)
        elif data == "check_subscription":
            check_subscription_callback(call)
        elif data == "restart_bot":
            restart_bot_callback_callback(call)
        elif data == "restart_all":
            restart_all_callback(call)
        elif data == "back_to_main":
            back_to_main_callback(call)
        elif data == "view_pending":
            callback_view_pending(call)
        elif data.startswith("approve_"):
            callback_approve(call)
        elif data.startswith("reject_"):
            callback_reject(call)
        elif data.startswith("view_user_"):
            view_user_callback(call)
        elif data.startswith("broadcast_confirm_"):
            broadcast_confirm_callback(call)
        elif data == "broadcast_cancel":
            broadcast_cancel_callback(call)
        elif data.startswith("copy_referral_"):
            copy_referral_callback(call)
        elif data.startswith("qr_referral_"):
            qr_referral_callback(call)
        elif data.startswith("check_referrals_"):
            check_referrals_callback(call)
        elif data.startswith("check_force_sub"):
            not_joined = check_force_sub(user_id)
            if not_joined:
                markup = InlineKeyboardMarkup(row_width=1)
                for channel_tag, channel_link, channel_name in not_joined:
                    markup.add(make_colored_button(f"🔵 Join {channel_name}", style="primary", url=channel_link))
                markup.add(make_colored_button("✅ Click Here After Joining ✅", style="success", callback_data='check_force_sub_start'))
                bot.answer_callback_query(call.id, B("❌ Not all joined!"), show_alert=True)
                try:
                    bot.edit_message_text(B("⚠️ FORCE SUBSCRIBE\n\nYou must join:"), call.message.chat.id, call.message.message_id, reply_markup=markup)
                except:
                    pass
            else:
                bot.answer_callback_query(call.id, B("✅ Verified!"))
                msg = call.message
                msg.text = "/start"
                command_send_welcome(msg)
        elif data.startswith("f:"):
            file_control_callback(call)
        elif data.startswith("s:"):
            start_bot_callback(call)
        elif data.startswith("p:"):
            stop_bot_callback(call)
        elif data.startswith("r:"):
            restart_bot_callback(call)
        elif data.startswith("d:"):
            delete_bot_callback(call)
        elif data.startswith("l:"):
            logs_bot_callback(call)
        elif data.startswith("t:"):
            callback_terminal(call)
        elif data.startswith("ct:"):
            callback_close_terminal(call)
        elif data.startswith("cc:"):
            callback_cancel_terminal(call)
        elif data.startswith("rf:"):
            callback_refresh_terminal(call)
        elif data.startswith("hn:"):
            callback_host_normal(call)
        elif data.startswith("ht:"):
            callback_host_terminal(call)
        elif data == "ban_user":
            ban_user_callback(call)
        elif data == "unban_user":
            unban_user_callback(call)
        elif data == "banned_list":
            banned_list_callback(call)
        elif data == "all_files":
            all_files_callback(call)
        else:
            bot.answer_callback_query(call.id, "❓ Unknown")
    except Exception as e:
        logger.error(f"Callback error: {e}", exc_info=True)
        try:
            bot.answer_callback_query(call.id, "❌ Error")
        except:
            pass

# ================================
# SILENT RESTART FUNCTION
# ================================
def _restart_script_silent(script_path, user_id, user_folder, file_name, file_type='py'):
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'a', encoding='utf-8', errors='ignore')
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        if file_type == 'py':
            process = subprocess.Popen(
                [sys.executable, script_path], cwd=user_folder,
                stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                startupinfo=startupinfo, encoding='utf-8', errors='ignore', env=env
            )
        else:
            process = subprocess.Popen(
                ['node', script_path], cwd=user_folder,
                stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                startupinfo=startupinfo, encoding='utf-8', errors='ignore', env=env
            )
        script_key = f"{user_id}_{file_name}"
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'user_id': user_id, 'start_time': datetime.now(),
            'type': file_type, 'script_key': script_key
        }
        recovery_system.save_running_script(user_id, file_name, script_path, process.pid)
        logger.info(f"✅ Silent restart: {file_name} (PID: {process.pid})")
    except Exception as e:
        logger.error(f"Silent restart failed for {file_name}: {e}")

# ================================
# HEALTH MONITOR THREAD
# ================================
def health_monitor():
    while True:
        try:
            for script_key in list(bot_scripts.keys()):
                try:
                    script_info = bot_scripts.get(script_key)
                    if not script_info:
                        continue
                    uid = script_info['user_id']
                    fname = script_info['file_name']
                    proc = script_info.get('process')
                    is_alive = False
                    if proc and hasattr(proc, 'pid'):
                        try:
                            if HAS_PSUTIL:
                                p = psutil.Process(proc.pid)
                                is_alive = p.is_running() and p.status() != psutil.STATUS_ZOMBIE
                            else:
                                try:
                                    os.kill(proc.pid, 0)
                                    is_alive = True
                                except OSError:
                                    is_alive = False
                        except:
                            is_alive = False
                    if not is_alive:
                        logger.warning(f"Script died: {script_key}")
                        recovery_system.remove_running_script(uid, fname)
                        if 'log_file' in script_info and script_info['log_file']:
                            try: script_info['log_file'].close()
                            except: pass
                        del bot_scripts[script_key]
                        if uid in terminal_sessions and fname in terminal_sessions[uid]:
                            del terminal_sessions[uid][fname]
                        tier = get_user_tier(uid)
                        should_restart = False
                        if tier in ['owner', 'premium']:
                            should_restart = TIER_SYSTEM[tier]['auto_restart']
                        elif tier == 'free':
                            should_restart = referral_system.is_auto_restart_enabled(uid)
                        if should_restart:
                            user_folder = get_user_folder(uid)
                            file_path = os.path.join(user_folder, fname)
                            if os.path.exists(file_path):
                                file_type = 'py'
                                for fn, ft in user_files.get(uid, []):
                                    if fn == fname:
                                        file_type = ft
                                        break
                                threading.Thread(
                                    target=_restart_script_silent,
                                    args=(file_path, uid, user_folder, fname, file_type)
                                ).start()
                except Exception as e:
                    logger.error(f"Health monitor check error: {e}")
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
        time.sleep(30)

# ================================
# GITHUB DEPLOYMENT SYSTEM
# ================================
_github_sessions = {}

def start_github_deploy(message):
    user_id = message.from_user.id
    _github_sessions[user_id] = {'step': 'url'}
    bot.reply_to(message, B("🐙 GitHub Deployment\n\nStep 1/2: Send me the GitHub repository URL.\n\nExample: https://github.com/username/repo\nOr: username/repo"))
    bot.register_next_step_handler(message, process_github_url)

def process_github_url(message):
    user_id = message.from_user.id
    url = message.text.strip()
    if url.startswith('https://github.com/'):
        repo_path = url.replace('https://github.com/', '').rstrip('/')
    elif url.startswith('github.com/'):
        repo_path = url.replace('github.com/', '').rstrip('/')
    elif '/' in url and not url.startswith('http'):
        repo_path = url.rstrip('/')
    else:
        bot.reply_to(message, B("❌ Invalid URL.\nSend like: username/repo or full GitHub URL"))
        bot.register_next_step_handler(message, process_github_url)
        return
    _github_sessions[user_id] = {'step': 'filename', 'repo': repo_path}
    bot.reply_to(message, B(f"✅ Repo: {repo_path}\n\nStep 2/2: Send the main file name to run.\n\nExample: main.py or bot.js"))
    bot.register_next_step_handler(message, process_github_filename)

def process_github_filename(message):
    user_id = message.from_user.id
    file_name = message.text.strip()
    session = _github_sessions.get(user_id)
    if not session or 'repo' not in session:
        bot.reply_to(message, B("❌ Session expired. Use 🐙 GitHub button again."))
        return
    repo_path = session['repo']
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ['.py', '.js']:
        bot.reply_to(message, B("❌ Only .py or .js files can be hosted."))
        return
    del _github_sessions[user_id]
    msg = bot.reply_to(message, B(f"🐙 Cloning {repo_path} and deploying {file_name}...\n⏳ Please wait..."))
    threading.Thread(target=deploy_from_github, args=(user_id, repo_path, file_name, file_ext, message, msg)).start()

def deploy_from_github(user_id, repo_path, file_name, file_ext, original_message, status_message):
    try:
        chat_id = status_message.chat.id
        msg_id = status_message.message_id
        user_folder = get_user_folder(user_id)
        parts = repo_path.split('/')
        username = parts[0]
        reponame = parts[1].replace('.git', '')
        branch = 'main'
        if len(parts) > 2 and parts[2] == 'tree':
            branch = parts[3] if len(parts) > 3 else 'main'
        raw_url = f"https://raw.githubusercontent.com/{username}/{reponame}/{branch}/{file_name}"
        bot.edit_message_text(f"📥 Downloading {file_name} from {username}/{reponame}...", chat_id, msg_id)
        try:
            response = requests.get(raw_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (compatible; CYBERXBot/3.5)'})
        except Exception as e:
            bot.edit_message_text(f"❌ Download failed: {str(e)[:100]}\n\nTry: {raw_url}", chat_id, msg_id)
            return
        if response.status_code != 200:
            if branch == 'main':
                raw_url = f"https://raw.githubusercontent.com/{username}/{reponame}/master/{file_name}"
                try:
                    response = requests.get(raw_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (compatible; CYBERXBot/3.5)'})
                except:
                    pass
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}"
                if response.status_code == 404:
                    error_msg = f"File {file_name} not found in {username}/{reponame} (branch: {branch})"
                elif response.status_code == 403:
                    error_msg = "Rate limited by GitHub. Wait 1 min or use a token."
                bot.edit_message_text(f"❌ {error_msg}", chat_id, msg_id)
                return
        dest_path = os.path.join(user_folder, file_name)
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        save_user_file(user_id, file_name, file_ext.replace('.', ''))
        bot.edit_message_text(f"✅ Downloaded! Starting {file_name}...", chat_id, msg_id)
        if file_ext == '.py':
            threading.Thread(target=run_script, args=(dest_path, user_id, user_folder, file_name, original_message)).start()
        else:
            threading.Thread(target=run_js_script, args=(dest_path, user_id, user_folder, file_name, original_message)).start()
    except Exception as e:
        logger.error(f"GitHub deploy error: {e}")
        try:
            bot.edit_message_text(f"❌ Deploy error: {str(e)[:200]}", status_message.chat.id, status_message.message_id)
        except:
            pass

# ================================
# GLOBAL ERROR LOGGER
# ================================
def _log_bot_error(exception):
    try:
        logger.error("Telegram handler error: %s", exception, exc_info=True)
    except Exception:
        pass

# ================================
# BOT STARTUP
# ================================
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║   CYBERX HOSTING BOT V3.5             ║
    ║   ✓ ANDROID/TERMUX COMPATIBLE         ║
    ║   ✓ FULL COLOR BUTTONS                ║
    ║   ✓ AUTO-RESTART FOR SCRIPTS          ║
    ║   ✓ HEALTH MONITOR THREAD             ║
    ║   ✓ SAFE POLLING / STARTUP            ║
    ╚═══════════════════════════════════════╝
    """)

    try:
        print("🔎 Checking Telegram API...")
        me = bot.get_me()
        if not me or not getattr(me, 'id', None):
            raise RuntimeError("Telegram getMe() returned no bot information")
        print(f"✅ Connected as @{getattr(me, 'username', None) or 'unknown'} (ID: {me.id})")
        try:
            result = bot.delete_webhook(drop_pending_updates=False)
            print(f"✅ Webhook cleared: {result}")
        except TypeError:
            bot.delete_webhook()
            print("✅ Webhook cleared.")
        except Exception as webhook_error:
            logger.warning("Webhook cleanup warning: %s", webhook_error)
        bot.get_me()
    except Exception as startup_error:
        logger.exception("Telegram startup check failed")
        print(f"❌ Telegram startup failed: {startup_error}")
        print("   Check BOT_TOKEN, internet access, and whether another instance is running.")
        sys.exit(1)

    try:
        keep_alive()
        print("✅ Flask Keep-Alive Started.")
    except Exception as e:
        logger.exception("Keep-alive failed")
        print(f"⚠️ Keep-Alive disabled: {e}")

    try:
        recovered = recovery_system.recover_all_scripts()
        if recovered:
            print(f"✅ Recovered {len(recovered)} scripts from last session.")
    except Exception as e:
        logger.exception("Recovery startup failed")
        print(f"⚠️ Recovery skipped: {e}")

    try:
        monitor_thread = threading.Thread(target=health_monitor, daemon=True)
        monitor_thread.start()
        print("✅ Health Monitor started (30s interval)")
    except Exception as e:
        logger.exception("Health monitor failed")
        print(f"⚠️ Health Monitor disabled: {e}")

    def start_polling_with_retry():
        retry_delay = 2
        while True:
            try:
                print("🔄 Telegram polling started — send /start now.")
                try:
                    bot.delete_webhook(drop_pending_updates=False)
                except TypeError:
                    bot.delete_webhook()
                bot.infinity_polling(
                    timeout=60,
                    long_polling_timeout=60,
                    skip_pending=False,
                    allowed_updates=['message', 'callback_query', 'edited_message', 'channel_post']
                )
                print("⚠️ Polling stopped unexpectedly; restarting...")
                retry_delay = 2
            except KeyboardInterrupt:
                print("👋 Bot stopped by user.")
                for script_key, script_info in list(bot_scripts.items()):
                    try:
                        kill_process_tree(script_info)
                        if script_info.get('log_file'):
                            try:
                                script_info['log_file'].close()
                            except Exception:
                                pass
                    except Exception:
                        pass
                bot_scripts.clear()
                sys.exit(0)
            except Exception as e:
                logger.exception("❌ Polling error")
                print(f"❌ Polling error: {e}")
                if '409' in str(e) or 'Conflict' in str(e):
                    print("⚠️ Telegram says another bot instance is using getUpdates.")
                    print("   Stop the other CYBERX process/device before starting this one.")
                elif '401' in str(e) or 'Unauthorized' in str(e):
                    print("⚠️ BOT_TOKEN is invalid/revoked. Create a new token with BotFather.")
                    break
                print(f"🔄 Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)

    start_polling_with_retry()
