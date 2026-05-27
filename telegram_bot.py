"""
Telegram Lookup Bot - Complete Ready to Run
------------------------------------------
Legal Features Only:
  - IFSC Lookup (Razorpay public API)
  - Pincode Lookup (India Post public API)
  - Vehicle Info (placeholder - use RTO public API)
  - Instagram Username Check (public)
  - Premium System (manual UPI activation by admin)

Setup:
  pip install python-telegram-bot requests
  
  1. BotFather se /newbot karke TOKEN lo
  2. Apna Telegram chat ID ADMIN_ID mein daalo
  3. python telegram_bot.py
"""

import logging
import sqlite3
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ─────────────────────────────────────────────
#  CONFIG — Yahan apna data daalo
# ─────────────────────────────────────────────
TOKEN = "8750048508:AAFMCAgD6U9JZSWnMG7jheylZ3f6DTALh2g"          # BotFather se liya hua token
ADMIN_ID = 123456789                   # Apna Telegram numeric ID
UPI_ID = "yourname@upi"               # Payment ke liye UPI ID
PREMIUM_PRICE = "₹99"                  # Premium ki price

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
DB = "bot_users.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id   INTEGER PRIMARY KEY,
            username  TEXT,
            is_premium INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_user(chat_id: int, username: str = ""):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)",
        (chat_id, username),
    )
    conn.commit()
    conn.close()

def check_premium(chat_id: int) -> bool:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT is_premium FROM users WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0] == 1)

def set_premium(chat_id: int, value: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,)
    )
    c.execute(
        "UPDATE users SET is_premium=? WHERE chat_id=?", (value, chat_id)
    )
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT chat_id, username, is_premium FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────────
#  KEYBOARDS
# ─────────────────────────────────────────────
def main_menu():
    kb = [
        [
            InlineKeyboardButton("🏦 IFSC LOOKUP",    callback_data="ifsc"),
            InlineKeyboardButton("📮 PINCODE LOOKUP", callback_data="pincode"),
        ],
        [
            InlineKeyboardButton("🚗 VEHICLE LOOKUP",   callback_data="vehicle"),
            InlineKeyboardButton("📸 INSTAGRAM LOOKUP", callback_data="instagram"),
        ],
        [
            InlineKeyboardButton("💰 BUY PREMIUM",      callback_data="buy_premium"),
            InlineKeyboardButton("✅ MY PREMIUM STATUS", callback_data="premium_status"),
        ],
    ]
    return InlineKeyboardMarkup(kb)

def back_btn():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    )

# ─────────────────────────────────────────────
#  LOOKUP FUNCTIONS
# ─────────────────────────────────────────────
def lookup_ifsc(code: str) -> str:
    try:
        r = requests.get(f"https://ifsc.razorpay.com/{code.upper()}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            return (
                f"🏦 *IFSC Lookup Result*\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🔑 *IFSC:* `{d.get('IFSC','N/A')}`\n"
                f"🏢 *Bank:* {d.get('BANK','N/A')}\n"
                f"🌿 *Branch:* {d.get('BRANCH','N/A')}\n"
                f"🏙️ *City:* {d.get('CITY','N/A')}\n"
                f"🗺️ *State:* {d.get('STATE','N/A')}\n"
                f"📍 *Address:* {d.get('ADDRESS','N/A')}\n"
                f"📞 *Contact:* {d.get('CONTACT','N/A')}\n"
                f"🌐 *MICR:* {d.get('MICR','N/A')}"
            )
        return "❌ Invalid IFSC Code. Please check and try again."
    except Exception as e:
        logger.error(f"IFSC error: {e}")
        return "⚠️ Server error. Try again later."


def lookup_pincode(pin: str) -> str:
    try:
        r = requests.get(
            f"https://api.postalpincode.in/pincode/{pin}", timeout=10
        )
        data = r.json()
        if data[0]["Status"] == "Success":
            offices = data[0]["PostOffice"]
            lines = [f"📮 *Pincode Lookup: {pin}*\n━━━━━━━━━━━━━━━━"]
            for po in offices[:5]:  # max 5 post offices
                lines.append(
                    f"\n📬 *{po['Name']}*\n"
                    f"   Type: {po['BranchType']}\n"
                    f"   District: {po['District']}\n"
                    f"   State: {po['State']}"
                )
            return "\n".join(lines)
        return "❌ Invalid Pincode. Please check and try again."
    except Exception as e:
        logger.error(f"Pincode error: {e}")
        return "⚠️ Server error. Try again later."


def lookup_vehicle(reg: str) -> str:
    # RTO public data - placeholder
    # Real usage ke liye: https://www.vehicleinfo.in/ ya RapidAPI se RTO API lo
    return (
        f"🚗 *Vehicle Lookup: {reg.upper()}*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⚠️ Live RTO lookup ke liye premium RTO API key chahiye.\n\n"
        f"Free me check karo:\n"
        f"🌐 https://vahan.parivahan.gov.in/vahanservice/\n"
        f"(Official Govt Portal)"
    )


def lookup_instagram(username: str) -> str:
    try:
        url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return (
                f"📸 *Instagram Lookup*\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"👤 *Username:* @{username}\n"
                f"✅ *Status:* Account Exists\n"
                f"🔗 https://instagram.com/{username}"
            )
        elif r.status_code == 404:
            return f"❌ @{username} — Account does not exist or is deleted."
        else:
            return (
                f"📸 *Instagram Lookup*\n"
                f"👤 @{username}\n"
                f"ℹ️ Status could not be determined (Instagram rate limit).\n"
                f"🔗 https://instagram.com/{username}"
            )
    except Exception as e:
        logger.error(f"Instagram error: {e}")
        return "⚠️ Could not fetch. Try again later."

# ─────────────────────────────────────────────
#  HANDLERS
# ─────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    add_user(chat_id, user.username or "")
    premium = check_premium(chat_id)
    badge = "✅ Premium" if premium else "🆓 Free"
    await update.message.reply_text(
        f"👋 *Welcome to LookupBot!*\n\n"
        f"🆔 Your Chat ID: `{chat_id}`\n"
        f"🎖️ Plan: {badge}\n\n"
        f"Choose a lookup option below 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel — sirf admin ke liye"""
    if update.effective_chat.id != ADMIN_ID:
        return await update.message.reply_text("❌ You are not authorized.")
    users = get_all_users()
    total = len(users)
    premium = sum(1 for u in users if u[2] == 1)
    lines = [f"👑 *Admin Panel*\n━━━━━━━━━━━━━━━━"]
    lines.append(f"👥 Total Users: {total}")
    lines.append(f"💎 Premium: {premium}")
    lines.append(f"🆓 Free: {total - premium}\n")
    lines.append("Recent users:")
    for uid, uname, prem in users[-10:]:
        icon = "💎" if prem else "🆓"
        lines.append(f"{icon} `{uid}` — @{uname or 'N/A'}")
    await update.message.reply_text(
        "\n".join(lines), parse_mode="Markdown"
    )


async def cmd_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /activate <chat_id>"""
    if update.effective_chat.id != ADMIN_ID:
        return
    try:
        target_id = int(context.args[0])
        set_premium(target_id, 1)
        await update.message.reply_text(
            f"✅ Premium activated for `{target_id}`", parse_mode="Markdown"
        )
        # User ko notify karo
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="🎉 *Congratulations!*\n\nYour Premium has been activated! ✅\n\nEnjoy all features.",
                parse_mode="Markdown",
            )
        except Exception:
            pass
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /activate <chat_id>")


async def cmd_deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /deactivate <chat_id>"""
    if update.effective_chat.id != ADMIN_ID:
        return
    try:
        target_id = int(context.args[0])
        set_premium(target_id, 0)
        await update.message.reply_text(
            f"❌ Premium removed for `{target_id}`", parse_mode="Markdown"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /deactivate <chat_id>")


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /broadcast <message>"""
    if update.effective_chat.id != ADMIN_ID:
        return
    if not context.args:
        return await update.message.reply_text("Usage: /broadcast <message>")
    msg = " ".join(context.args)
    users = get_all_users()
    sent = 0
    for uid, _, _ in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 {msg}")
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Broadcast sent to {sent} users.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    data = query.data

    if data == "menu":
        await query.message.edit_text(
            f"🆔 Chat ID: `{chat_id}`\nChoose an option:",
            reply_markup=main_menu(),
            parse_mode="Markdown",
        )

    elif data == "premium_status":
        status = "✅ *PREMIUM USER*\nSabhi features unlock hain!" if check_premium(chat_id) else "❌ *FREE USER*\nPremium lene ke liye Buy Premium dabaao."
        await query.message.edit_text(
            f"🎖️ *Your Status*\n━━━━━━━━━━━━━━━━\n{status}",
            reply_markup=back_btn(),
            parse_mode="Markdown",
        )

    elif data == "buy_premium":
        await query.message.edit_text(
            f"💰 *Buy Premium - {PREMIUM_PRICE}*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"1️⃣ Pay *{PREMIUM_PRICE}* to UPI:\n"
            f"   `{UPI_ID}`\n\n"
            f"2️⃣ Screenshot lo payment ka\n\n"
            f"3️⃣ Screenshot *yahan* bhejo is chat mein\n\n"
            f"4️⃣ Admin verify karke activate karega ✅\n\n"
            f"⚠️ Fake payment reject hoga.\n"
            f"🆔 Your Chat ID: `{chat_id}`",
            reply_markup=back_btn(),
            parse_mode="Markdown",
        )

    elif data == "ifsc":
        context.user_data["waiting"] = "ifsc"
        await query.message.edit_text(
            "🏦 *IFSC Lookup*\n\nIFSC code enter karo:\nExample: `SBIN0001234`",
            reply_markup=back_btn(),
            parse_mode="Markdown",
        )

    elif data == "pincode":
        context.user_data["waiting"] = "pincode"
        await query.message.edit_text(
            "📮 *Pincode Lookup*\n\n6-digit pincode enter karo:\nExample: `110001`",
            reply_markup=back_btn(),
            parse_mode="Markdown",
        )

    elif data == "vehicle":
        context.user_data["waiting"] = "vehicle"
        await query.message.edit_text(
            "🚗 *Vehicle Lookup*\n\nRegistration number enter karo:\nExample: `MH12AB1234`",
            reply_markup=back_btn(),
            parse_mode="Markdown",
        )

    elif data == "instagram":
        context.user_data["waiting"] = "instagram"
        await query.message.edit_text(
            "📸 *Instagram Lookup*\n\nUsername enter karo (@ ke bina):\nExample: `username`",
            reply_markup=back_btn(),
            parse_mode="Markdown",
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    waiting = context.user_data.get("waiting")

    # Payment screenshot admin ko forward karo
    if update.message.photo:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 *Payment Screenshot Received*\n🆔 From: `{chat_id}`\n@{update.effective_user.username or 'N/A'}\n\nActivate: `/activate {chat_id}`",
            parse_mode="Markdown",
        )
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=chat_id,
            message_id=update.message.message_id,
        )
        await update.message.reply_text(
            "✅ Screenshot admin ko bhej diya gaya!\nVerification ke baad premium activate hoga. ⏳",
            reply_markup=back_btn(),
        )
        return

    if not waiting:
        await update.message.reply_text(
            "Menu se option choose karo 👇", reply_markup=main_menu()
        )
        return

    context.user_data["waiting"] = None
    await update.message.reply_text("🔍 Searching...", parse_mode="Markdown")

    if waiting == "ifsc":
        result = lookup_ifsc(text)
    elif waiting == "pincode":
        if not text.isdigit() or len(text) != 6:
            result = "❌ Valid 6-digit pincode enter karo."
        else:
            result = lookup_pincode(text)
    elif waiting == "vehicle":
        result = lookup_vehicle(text)
    elif waiting == "instagram":
        result = lookup_instagram(text)
    else:
        result = "❓ Unknown command."

    await update.message.reply_text(
        result, reply_markup=back_btn(), parse_mode="Markdown"
    )


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start", cmd_start))

    # Admin commands
    app.add_handler(CommandHandler("admin",      cmd_admin))
    app.add_handler(CommandHandler("activate",   cmd_activate))
    app.add_handler(CommandHandler("deactivate", cmd_deactivate))
    app.add_handler(CommandHandler("broadcast",  cmd_broadcast))

    # Buttons & messages
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )
    app.add_handler(
        MessageHandler(filters.PHOTO, message_handler)
    )

    logger.info("✅ Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
