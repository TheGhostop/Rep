import json
import os
from telethon.sync import TelegramClient
from config import SESSIONS_FILE

def load_sessions():
    """Load session data from file."""
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    return {}

def check_admin_accounts(admin_id):
    """Return the number of accounts added by a specific admin."""
    sessions = load_sessions()
    return sum(1 for session in sessions.values() if session.get("admin_id") == admin_id)

def check_total_accounts():
    """Return the total number of logged-in accounts."""
    return len(load_sessions())
