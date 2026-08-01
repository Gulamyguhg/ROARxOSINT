import requests
import json
import time

# ==========================================
# CONFIGURATION
# ==========================================

BOT_TOKEN = "8895631051:AAG93LsbEzPwJ8mb4NkHWc0NFNBKjK-zO5g"

PHONE_API_URL = "https://exploitsindia.site/osintanishexploits/api.php?key=SATVIRxSHUBHAM&type=number&num=9955878039"
AADHAAR_API_URL = "exploitsindia.site/osintanishexploits/api.php?key=SHUBHxANISH&type=aadhaar&aadhaar=962397300673"

# Dummy HTTPS server URL
DUMMY_HTTPS_SERVER = ""

TELEGRAM_API = "https://api.telegram.org/bot" + BOT_TOKEN


# ==========================================
# TELEGRAM API
# ==========================================

def send_message(chat_id, text, keyboard=None):
    url = TELEGRAM_API + "/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if keyboard is not None:
        data["reply_markup"] = json.dumps(keyboard)

    try:
        requests.post(
            url,
            data=data,
            timeout=15
        )
    except requests.RequestException:
        pass


def get_updates(offset):
    url = TELEGRAM_API + "/getUpdates"

    params = {
        "offset": offset,
        "timeout": 25
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        return response.json()

    except (requests.RequestException, ValueError):
        return {
            "ok": False,
            "result": []
        }


# ==========================================
# KEYBOARD
# ==========================================

MAIN_KEYBOARD = {
    "keyboard": [
        [
            {
                "text": "📱 Phone Lookup"
            }
        ],
        [
            {
                "text": "🪪 Aadhaar Verification"
            }
        ]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}


# ==========================================
# PHONE API
# ==========================================

def phone_lookup(number):

    if not PHONE_API_URL:
        return {
            "success": False,
            "error": "Phone verification API is not configured."
        }

    try:
        response = requests.get(
            PHONE_API_URL,
            params={
                "phone": number
            },
            timeout=20
        )

        try:
            return response.json()

        except ValueError:
            return {
                "success": False,
                "error": "API did not return valid JSON."
            }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": "API request failed.",
            "details": str(error)
        }


# ==========================================
# AADHAAR VERIFICATION API
# ==========================================

def aadhaar_verify(aadhaar):

    if not AADHAAR_API_URL:
        return {
            "success": False,
            "error": "Authorized Aadhaar verification API is not configured."
        }

    try:
        response = requests.get(
            AADHAAR_API_URL,
            params={
                "aadhaar": aadhaar
            },
            timeout=20
        )

        try:
            return response.json()

        except ValueError:
            return {
                "success": False,
                "error": "API did not return valid JSON."
            }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": "Verification request failed.",
            "details": str(error)
        }


# ==========================================
# JSON FORMATTER
# ==========================================

def format_json(data):

    formatted = json.dumps(
        data,
        indent=4,
        ensure_ascii=False
    )

    # Telegram HTML safety
    formatted = (
        formatted
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    return "<pre>" + formatted + "</pre>"


# ==========================================
# MAIN BOT
# ==========================================

def main():

    offset = 0
    mode = {}

    print("Bot started...")

    while True:

        updates = get_updates(offset)

        if not updates.get("ok"):
            time.sleep(2)
            continue

        for update in updates.get("result", []):

            offset = update["update_id"] + 1

            message = update.get("message")

            if not message:
                continue

            chat_id = message["chat"]["id"]

            text = message.get("text", "").strip()

            # ==================================
            # /start
            # ==================================

            if text == "/start":

                mode[chat_id] = None

                send_message(
                    chat_id,
                    "👋 <b>Welcome!</b>\n\n"
                    "Select an option below:",
                    MAIN_KEYBOARD
                )

                continue

            # ==================================
            # PHONE BUTTON
            # ==================================

            if text == "📱 Phone Lookup":

                mode[chat_id] = "phone"

                send_message(
                    chat_id,
                    "📞 Send 10 digit mobile number:"
                )

                continue

            # ==================================
            # AADHAAR BUTTON
            # ==================================

            if text == "🪪 Aadhaar Verification":

                mode[chat_id] = "aadhaar"

                send_message(
                    chat_id,
                    "🪪 Send 12 digit Aadhaar number for "
                    "authorized verification:"
                )

                continue

            # ==================================
            # PHONE MODE
            # ==================================

            if mode.get(chat_id) == "phone":

                if not text.isdigit() or len(text) != 10:

                    send_message(
                        chat_id,
                        "❌ <b>Invalid mobile number.</b>\n\n"
                        "Please send exactly 10 numeric digits."
                    )

                    continue

                send_message(
                    chat_id,
                    "⏳ Processing..."
                )

                result = phone_lookup(text)

                send_message(
                    chat_id,
                    format_json(result)
                )

                mode[chat_id] = None

                continue

            # ==================================
            # AADHAAR MODE
            # ==================================

            if mode.get(chat_id) == "aadhaar":

                if not text.isdigit() or len(text) != 12:

                    send_message(
                        chat_id,
                        "❌ <b>Invalid Aadhaar format.</b>\n\n"
                        "Please enter exactly 12 numeric digits."
                    )

                    continue

                send_message(
                    chat_id,
                    "⏳ Verifying..."
                )

                result = aadhaar_verify(text)

                send_message(
                    chat_id,
                    format_json(result)
                )

                mode[chat_id] = None

                continue

            # ==================================
            # UNKNOWN MESSAGE
            # ==================================

            send_message(
                chat_id,
                "❓ Please use /start and select an option.",
                MAIN_KEYBOARD
            )

        time.sleep(1)


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()