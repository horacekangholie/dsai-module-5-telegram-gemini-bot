#!/usr/bin/env python3
"""
Long-polling Telegram ↔ Gemini bot, ready for Render.com.

Prerequisites (requirements.txt):
    google-generativeai
    requests
"""

import os
import time
import logging

import requests
import google.generativeai as genai

# ——— Configuration ———
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_KEY     = os.getenv('GEMINI_KEY')
GEMINI_MODEL   = 'gemini-2.0-flash'
POLL_INTERVAL  = 1     # seconds between Telegram polls
POLL_TIMEOUT   = 30    # long-poll timeout (secs)
QUIT_CMD       = 'quit'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# ——— Sanity Check for Secrets ———
if not TELEGRAM_TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")
if not GEMINI_KEY:
    raise RuntimeError("Missing GEMINI_KEY environment variable")

# ——— Configure Gemini ———
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# ——— Telegram Helpers ———
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

def get_updates(offset: int | None = None) -> list[dict]:
    params = {"timeout": POLL_TIMEOUT}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(BASE_URL + 'getUpdates', params=params)
    resp.raise_for_status()
    return resp.json().get('result', [])

def send_message(chat_id: int, text: str) -> None:
    params = {"chat_id": chat_id, "text": text}
    resp = requests.get(BASE_URL + 'sendMessage', params=params)
    resp.raise_for_status()

# ——— Main Loop ———
def main():
    logging.info("Bot started. Polling for updates...")
    offset = None

    try:
        while True:
            updates = get_updates(offset)
            for upd in updates:
                offset = upd['update_id'] + 1
                msg = upd.get('message', {})
                text = msg.get('text', '').strip()
                chat_id = msg.get('chat', {}).get('id')

                if not chat_id or not text:
                    continue

                # Handle a quit signal
                if text.lower() == QUIT_CMD:
                    send_message(chat_id, "Alright, feel free to ask me questions anytime.")
                    continue

                # Forward everything else to Gemini
                try:
                    resp = model.generate_content(text)
                    reply = resp.text
                except Exception as e:
                    logging.error("Gemini error: %s", e)
                    reply = f"Error fetching from Gemini: {e}"

                send_message(chat_id, reply)

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")


if __name__ == '__main__':
    main()
