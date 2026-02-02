# main.py - Telegram Course Bot (Replit-ready)
import os
import time
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ------------------ CONFIG ------------------
BOT_TOKEN = os.getenv(7856522676:AAEgPkOq0-_7-1e5pop2Wu4aBPskJwxY5aw) 
ADMIN_ID = 6185091342
UPI_ID = "factzone3741@oksbi"
RECEIVER_NAME = "ROHIT ROHIT"

COURSES = {
    "basic": {"name": "XYRO BASIC", "price": 1999, "group_id": -1002877715442},
    "pro": {"name": "XYRO PRO", "price": 6999, "group_id": -1003621018377}
}

LINK_EXPIRY_SECONDS = 10 * 60  # 10 minutes
pending_payments = {}

# ------------------ TELEGRAM HANDLERS ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("XYRO BASIC – ₹1999", callback_data="course_basic")],
        [InlineKeyboardButton("XYRO PRO – ₹6999", callback_data="course_pro")]
    ]
    await update.message.reply_text(
        "📚 *Select a Course:*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def course_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    course_key = query.data.split("_")[1]
    course = COURSES[course_key]
    pending_payments[query.from_user.id] = {"course_key": course_key}
    await query.message.reply_text(
        f"💰 *Payment Details*\n\n"
        f"📘 Course: *{course['name']}*\n"
        f"💵 Price: *₹{course['price']}*\n\n"
        f"🔹 UPI ID: `{UPI_ID}`\n"
        f"🔹 Receiver: *{RECEIVER_NAME}*\n\n"
        f"✅ Pay and send:\n1️⃣ UTR Number\n2️⃣ Screenshot",
        parse_mode="Markdown"
    )

async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in pending_payments:
        return
    pending_payments[user_id]["utr"] = update.message.caption or update.message.text
    pending_payments[user_id]["photo"] = update.message.photo[-1].file_id
    pending_payments[user_id]["username"] = update.message.from_user.username
    data = pending_payments[user_id]
    course = COURSES[data["course_key"]]
    kb = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]
    await context.bot.send_photo(
        ADMIN_ID,
        photo=data["photo"],
        caption=(
            f"💳 *New Payment*\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"👤 Username: @{data['username']}\n"
            f"📘 Course: {course['name']}\n"
            f"💰 Amount: ₹{course['price']}\n"
            f"🔢 UTR: `{data['utr']}`"
        ),
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    await update.message.reply_text("⏳ Payment submitted. Waiting for admin approval.")

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, user_id = query.data.split("_")
    user_id = int(user_id)
    if user_id not in pending_payments:
        await query.message.edit_caption("❌ Request expired.")
        return
    data = pending_payments.pop(user_id)
    course = COURSES[data["course_key"]]
    if action == "reject":
        await context.bot.send_message(user_id, "❌ Payment rejected.")
        await query.message.edit_caption("❌ Rejected.")
        return
    invite = await context.bot.create_chat_invite_link(
        chat_id=course["group_id"],
        member_limit=1,
        expire_date=int(time.time()) + LINK_EXPIRY_SECONDS
    )
    await context.bot.send_message(
        user_id,
        f"✅ *Payment Approved!*\n\n"
        f"📘 {course['name']}\n"
        f"🔗 Join link (10 min):\n{invite.invite_link}",
        parse_mode="Markdown"
    )
    await query.message.edit_caption("✅ Approved & link sent.")

# ------------------ WEB SERVER FOR UPTIME ------------------
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run).start()

# ------------------ MAIN ------------------
def main():
    app_bot = ApplicationBuilder().token(7856522676:AAEgPkOq0-_7-1e5pop2Wu4aBPskJwxY5aw).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(course_select, pattern="^course_"))
    app_bot.add_handler(CallbackQueryHandler(admin_action, pattern="^(approve|reject)_"))
    app_bot.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, receive_payment))
    print("Bot is running...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
