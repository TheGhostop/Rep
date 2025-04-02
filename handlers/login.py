import json
import os
import time
from telethon import TelegramClient, errors

# Define session storage file
SESSION_FILE = "sessions.json"

# Load existing sessions
if os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "r") as f:
        sessions = json.load(f)
else:
    sessions = {}

def save_sessions():
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=4)

def add_session(user_id, api_id, api_hash, session_string):
    """Adds a new session after verifying it."""
    try:
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        client.connect()

        if not client.is_user_authorized():
            print("Session is not authorized. Please log in again.")
            return False

        me = client.get_me()
        sessions[user_id] = {
            "session_string": session_string,
            "phone": me.phone,
            "last_checked": time.time()
        }
        save_sessions()
        print(f"Session added for {me.phone}")
        return True
    except errors.SessionExpiredError:
        print("Session expired. Please log in again.")
        return False
    except Exception as e:
        print(f"Error adding session: {e}")
        return False

def verify_sessions():
    """Checks all stored sessions and removes expired ones."""
    to_remove = []

    for user_id, data in sessions.items():
        try:
            client = TelegramClient(StringSession(data["session_string"]), API_ID, API_HASH)
            client.connect()

            if not client.is_user_authorized():
                print(f"Session for {data['phone']} is no longer valid.")
                to_remove.append(user_id)
        except Exception as e:
            print(f"Error verifying session for {data['phone']}: {e}")
            to_remove.append(user_id)

    for user_id in to_remove:
        del sessions[user_id]

    save_sessions()
    print("Session verification complete.")
