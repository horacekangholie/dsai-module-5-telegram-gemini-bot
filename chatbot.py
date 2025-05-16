#!/usr/bin/env python3
"""
Long-polling Telegram ↔ Gemini bot wrapped in a Flask health-check endpoint
so it can deploy as a Web Service on Render.com, with a custom /start welcome.
"""

import os
import time
import threading

import requests
import google.generativeai as genai
from flask import Flask

app = Flask(__name__)

# ——— Customizable welcome message ———
def get_welcome_message() -> str:
    """
    Return the bot’s welcome text.
    In future, this could fetch from a database.
    """
    return "Hi there! Welcome to my bot. How can I help you today?"

# ——— Your existing key-loading logic ———
def retrieve_key(service_name: str) -> str:
    try:
        # Attempt to retrieve from Colab Secrets
        from google.colab import userdata
        key = userdata.get(service_name)
        env_var = service_name.upper()
    except ImportError:
        # Fallback to environment variables
        env_map = {
            'telegram': 'TELEGRAM_TOKEN',
            'gemini':   'GEMINI_KEY'
        }
        env_var = env_map.get(service_name, service_name.upper())
        key = os.getenv(env_var)

    if not key:
        raise ValueError(f"ERROR: Missing {env_var} key")

    return key

# ——— Assign key values ———
TELEGRAM_TOKEN = retrieve_key('telegram')
GEMINI_KEY     = retrieve_key('gemini')

# ——— Configure Gemini ———
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ——— Telegram API helpers ———
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

def get_updates(offset=None, timeout=30):
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    resp = requests.get(BASE_URL + 'getUpdates', params=params)
    resp.raise_for_status()
    return resp.json().get('result', [])

def send_message(chat_id, text):
    params = {"chat_id": chat_id, "text": text}
    resp = requests.get(BASE_URL + 'sendMessage', params=params)
    resp.raise_for_status()

# ——— Your long-polling bot loop, now in a background thread ———
def run_bot():
    print("Bot started. Press Ctrl+C to stop.")
    offset = None
    try:
        while True:
            updates = get_updates(offset)
            for update in updates:
                offset = update['update_id'] + 1
                message = update.get('message')
                if not message or 'text' not in message:
                    continue

                chat_id = message['chat']['id']
                text    = message['text'].strip()

                # Handle /start: custom welcome
                if text.lower() == '/start':
                    send_message(chat_id, get_welcome_message())
                    continue

                # Handle quit
                if text.lower() == 'quit':
                    send_message(chat_id, "Alright, feel free to ask me questions anytime.")
                    continue

                # Otherwise, forward to Gemini
                try:
                    response = model.generate_content(text)
                    reply    = response.text
                except Exception as e:
                    reply = f"Error fetching from Gemini: {e}"

                send_message(chat_id, reply)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Bot stopped by user.")

# ——— Health check endpoint for Render ———
@app.route('/healthz')
def health():
    return 'ok', 200

# ——— Entrypoint ———
if __name__ == '__main__':
    # Start bot in background
    threading.Thread(target=run_bot, daemon=True).start()

    # Start Flask on Render’s assigned port
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
