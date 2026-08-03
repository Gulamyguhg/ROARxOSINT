import os
import logging
import json
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# ========== READ FROM ENVIRONMENT VARIABLES (FIXED .strip()) ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()   # <-- YAHAN .strip() ADD KIYA
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable missing!")

API_BASE = os.getenv("API_URL", "https://bronx-web-api.onrender.com/api/key-bronx")
TG_API_URL = os.getenv("TG_API_URL", "https://bronx-web-api.onrender.com/api/custom/telegram-scan")

PHONE_KEY = os.getenv("PHONE_KEY", "tg-99").strip()
AADHAAR_KEY = os.getenv("AADHAAR_KEY", "KEY").strip()
VEHICLE_KEY = os.getenv("VEHICLE_KEY", "tg-99").strip()
TG_KEY = os.getenv("TG_KEY", "tg-99").strip()

PHONE_API = f"{API_BASE}/numleak"
AADHAAR_API = f"{API_BASE}/aadhar"
VEHICLE_API = f"{API_BASE}/veh2num"

PHONE, AADHAAR, VEHICLE, TG_USERNAME = range(4)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_api(url, params):
    try:
        resp = requests.get(url, params=params, timeout=20)
        if resp.status_code != 200:
            return {"success": False, "error": f"HTTP {resp.status_code}", "body": resp.text}
        try:
            return resp.json()
        except:
            return {"success": False, "error": "Invalid JSON", "body": resp.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def phone_lookup(num):
    return call_api(PHONE_API, {"key": PHONE_KEY, "num": num})

def aadhaar_lookup(num):
    return call_api(AADHAAR_API, {"key": AADHAAR_KEY, "num": num})

def vehicle_lookup(vehicle):
    return call_api(VEHICLE_API, {"key": VEHICLE_KEY, "vehicle": vehicle.upper()})

def telegram_lookup(username):
    return call_api(TG_API_URL, {"key": TG_KEY, "id": username})

def format_result(data, title):
    if not data.get("success", False):
        error = data.get("error", "Unknown error")
        return f"❌ {title} failed:\n{error}"
    result = data.get("data", data)
    return f"✅ {title} result:\n```json\n{json.dumps(result, indent=2)}\n```"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📱 Phone Lookup", "🆔 Aadhaar Verification"],
        ["🚗 Vehicle Lookup", "📡 Telegram Scan"]
    ]
    await update.message.reply_text(
        "Welcome! Choose an option:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ConversationHandler.END

async def menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Phone" in text:
        await update.message.reply_text("📱 Send 10-digit number:")
        return PHONE
    elif "Aadhaar" in text:
        await update.message.reply_text("🆔 Send 12-digit Aadhaar:")
        return AADHAAR
    elif "Vehicle" in text:
        await update.message.reply_text("🚗 Send vehicle number (e.g. KL41V3504):")
        return VEHICLE
    elif "Telegram" in text:
        await update.message.reply_text("📡 Send username (without @):")
        return TG_USERNAME
    return ConversationHandler.END

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = update.message.text.strip()
    if not num.isdigit() or len(num) != 10:
        await update.message.reply_text("❌ Invalid 10-digit number.")
        return PHONE
    await update.message.reply_text("⏳ Processing...")
    result = phone_lookup(num)
    await update.message.reply_text(format_result(result, "Phone"), parse_mode="Markdown")
    return ConversationHandler.END

async def handle_aadhaar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = update.message.text.strip()
    if not num.isdigit() or len(num) != 12:
        await update.message.reply_text("❌ Invalid 12-digit Aadhaar.")
        return AADHAAR
    await update.message.reply_text("⏳ Processing...")
    result = aadhaar_lookup(num)
    await update.message.reply_text(format_result(result, "Aadhaar"), parse_mode="Markdown")
    return ConversationHandler.END

async def handle_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    veh = update.message.text.strip()
    if len(veh) < 4:
        await update.message.reply_text("❌ Invalid vehicle number.")
        return VEHICLE
    await update.message.reply_text("⏳ Processing...")
    result = vehicle_lookup(veh)
    await update.message.reply_text(format_result(result, "Vehicle"), parse_mode="Markdown")
    return ConversationHandler.END

async def handle_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().lstrip('@')
    if not username:
        await update.message.reply_text("❌ Invalid username.")
        return TG_USERNAME
    await update.message.reply_text("⏳ Processing...")
    result = telegram_lookup(username)
    await update.message.reply_text(format_result(result, "Telegram Scan"), parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            AADHAAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_aadhaar)],
            VEHICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vehicle)],
            TG_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tg)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_selection))
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
