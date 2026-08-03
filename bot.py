import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# ========== CONFIGURATION ==========
BOT_TOKEN = "8895631051:AAG93LsbEzPwJ8mb4NkHWc0NFNBKjK-zO5g"  # 👈 Replace with your bot token

# Bronx API endpoints (fixed)
PHONE_API = "https://bronx-web-api.onrender.com/api/key-bronx/numleak"
AADHAAR_API = "https://bronx-web-api.onrender.com/api/key-bronx/aadhar"
VEHICLE_API = "https://bronx-web-api.onrender.com/api/key-bronx/veh2num"
TG_API = "https://bronx-web-api.onrender.com/api/custom/telegram-scan"

# API keys – update these with valid ones!
PHONE_KEY = "tg-99"        # Replace if needed
AADHAAR_KEY = "KEY"        # Replace if needed
VEHICLE_KEY = "tg-99"      # Replace if needed
TG_KEY = "tg-99"           # Replace if needed

# Conversation states
PHONE, AADHAAR, VEHICLE, TG_USERNAME = range(4)

# ========== LOGGING ==========
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ========== API CALL FUNCTIONS ==========
def call_api(url, params):
    """Generic API caller with error handling."""
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

def phone_lookup(number):
    return call_api(PHONE_API, {"key": PHONE_KEY, "num": number})

def aadhaar_lookup(number):
    return call_api(AADHAAR_API, {"key": AADHAAR_KEY, "num": number})

def vehicle_lookup(vehicle):
    return call_api(VEHICLE_API, {"key": VEHICLE_KEY, "vehicle": vehicle.upper()})

def telegram_lookup(username):
    return call_api(TG_API, {"key": TG_KEY, "id": username})

# ========== FORMAT RESULTS ==========
def format_result(data, title):
    """Pretty-print JSON result."""
    if not data.get("success", False):
        error = data.get("error", "Unknown error")
        return f"❌ {title} failed:\n{error}"
    # If success, show the data nicely
    result = data.get("data", data)  # some APIs wrap in 'data'
    import json
    return f"✅ {title} result:\n```json\n{json.dumps(result, indent=2)}\n```"

# ========== BOT HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with reply keyboard."""
    keyboard = [
        ["📱 Phone Lookup", "🆔 Aadhaar Verification"],
        ["🚗 Vehicle Lookup", "📡 Telegram Scan"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome! Choose an option below:",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks and set state."""
    text = update.message.text
    if "Phone" in text:
        await update.message.reply_text("📱 Send the 10-digit mobile number:")
        return PHONE
    elif "Aadhaar" in text:
        await update.message.reply_text("🆔 Send the 12-digit Aadhaar number:")
        return AADHAAR
    elif "Vehicle" in text:
        await update.message.reply_text("🚗 Send the vehicle number (e.g. KL41V3504):")
        return VEHICLE
    elif "Telegram" in text:
        await update.message.reply_text("📡 Send the Telegram username (without @):")
        return TG_USERNAME
    else:
        await update.message.reply_text("Please use the buttons below.", reply_markup=ReplyKeyboardMarkup(...))
        return ConversationHandler.END

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    if not number.isdigit() or len(number) != 10:
        await update.message.reply_text("❌ Please enter a valid 10-digit number.")
        return PHONE
    await update.message.reply_text("⏳ Processing...")
    result = phone_lookup(number)
    formatted = format_result(result, "Phone Lookup")
    await update.message.reply_text(formatted, parse_mode="Markdown")
    return ConversationHandler.END

async def handle_aadhaar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    if not number.isdigit() or len(number) != 12:
        await update.message.reply_text("❌ Please enter a valid 12-digit Aadhaar number.")
        return AADHAAR
    await update.message.reply_text("⏳ Processing...")
    result = aadhaar_lookup(number)
    formatted = format_result(result, "Aadhaar Verification")
    await update.message.reply_text(formatted, parse_mode="Markdown")
    return ConversationHandler.END

async def handle_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vehicle = update.message.text.strip()
    if len(vehicle) < 4:  # basic check
        await update.message.reply_text("❌ Please enter a valid vehicle number.")
        return VEHICLE
    await update.message.reply_text("⏳ Processing...")
    result = vehicle_lookup(vehicle)
    formatted = format_result(result, "Vehicle Lookup")
    await update.message.reply_text(formatted, parse_mode="Markdown")
    return ConversationHandler.END

async def handle_tg_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().lstrip('@')
    if not username:
        await update.message.reply_text("❌ Please enter a valid username.")
        return TG_USERNAME
    await update.message.reply_text("⏳ Processing...")
    result = telegram_lookup(username)
    formatted = format_result(result, "Telegram Scan")
    await update.message.reply_text(formatted, parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ========== MAIN ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            AADHAAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_aadhaar)],
            VEHICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vehicle)],
            TG_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tg_username)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    # Also handle menu button clicks from the main menu (if not in conversation)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_selection))

    logger.info("Bot started polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
