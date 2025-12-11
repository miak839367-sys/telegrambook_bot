from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

import os

TOKEN = os.environ["BOT_TOKEN"]
app = Flask(__name__)

# -----------------------------
# Telegram Bot Logic
# -----------------------------
async def start(update: Update, context):
    await update.message.reply_text("سلام! ربات روشنه 😊")

async def echo(update: Update, context):
    txt = update.message.text
    await update.message.reply_text(f"گفتی: {txt}")

# ساختن اپلیکیشن تلگرام
app_telegram = Application.builder().token(TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.TEXT, echo))

# -----------------------------
# Webhook Endpoint
# -----------------------------
@app.route("/", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, app_telegram.bot)
        app_telegram.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
