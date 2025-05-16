# Prerequisites
# !pip install google-generativeai

import os
import requests, time
import google.generativeai as genai

# Load required secret keys
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
            'gemini': 'GEMINI_KEY'
        }
        env_var = env_map.get(service_name, service_name.upper())
        key = os.getenv(env_var)

    if not key:
        raise ValueError(f"ERROR: Missing {env_var} key")

    return key

# Assign key values
TELEGRAM_TOKEN = retrieve_key('telegram')
GEMINI_KEY = retrieve_key('gemini')

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Base URL for Telegram Bot API
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# Get update message
def get_updates(offset=None, timeout=30):
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    resp = requests.get(BASE_URL + 'getUpdates', params=params)
    return resp.json().get('result', [])

# Reply message
def send_message(chat_id, text):
    params = {"chat_id": chat_id, "text": text}
    requests.get(BASE_URL + 'sendMessage', params=params)

# Main
if __name__ == '__main__':
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

                if text.lower() == 'quit':
                    send_message(chat_id, "Alright, feel free to ask me question anytime.")
                    continue  # ← back to polling

                # Otherwise, generate & send a Gemini reply
                try:
                    response = model.generate_content(text)
                    reply    = response.text
                except Exception as e:
                    reply = f"Error fetching from Gemini: {e}"

                send_message(chat_id, reply)

            time.sleep(1)
    except KeyboardInterrupt:
        print("Bot stopped by user.")
