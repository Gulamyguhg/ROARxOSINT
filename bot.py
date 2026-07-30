import os
import requests
import json
import time

# ---------- Environment Variables (set these in your hosting platform) ----------
BOT_TOKEN = os.environ.get("8895631051: AAG93LsbEz
PwJ8mb4NkHWcØNFNBKjK-
z05g")
API_URL = os.environ.get("apis-
the-best.vercel.app/ api")

if not BOT_TOKEN or not API_URL:
    raise ValueError("BOT_TOKEN and API_URL must be set in environment variables.")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None):
    url = f"{TELEGRAM_API}/getUpdates"
    params = {"timeout": 30, "offset": offset} if offset else {"timeout": 30}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching updates: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return None

def build_keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def is_valid_number(text):
    return text.isdigit() and len(text) == 10

def lookup_phone(number):
    try:
        url = f"{API_URL}?type=number&mobile={number}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def main():
    print("Bot started. Polling for updates...")
    last_update_id = 0
    while True:
        updates = get_updates(offset=last_update_id + 1 if last_update_id else None)
        if not updates or not updates.get("ok"):
            time.sleep(1)
            continue
        for update in updates.get("result", []):
            last_update_id = update["update_id"]
            if "message" not in update:
                continue
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            if text == "/start":
                welcome = "👋 Welcome to the Phone Lookup Bot!\nUse the button below to look up any mobile number."
                send_message(chat_id, welcome, reply_markup=build_keyboard())
                continue
            if text == "📱 Phone Lookup":
                send_message(chat_id, "📞 Send 10 digit mobile number:")
                continue
            if is_valid_number(text):
                result = lookup_phone(text)
                formatted = json.dumps(result, indent=2, ensure_ascii=False)
                send_message(chat_id, f"<pre>{formatted}</pre>")
            else:
                send_message(chat_id, "❌ Invalid input. Please send exactly 10 digits (numbers only).")
        time.sleep(1)

if __name__ == "__main__":
    main()
