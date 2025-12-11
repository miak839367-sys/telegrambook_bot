import os
import requests
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ===============================
# Environment Variables
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Example: https://your-app.onrender.com/webhook

# ===============================
# Telegram Application
# ===============================
app_telegram = Application.builder().token(TOKEN).build()

# ===============================
# Handlers
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 Send a book name, author, or genre (English).")

async def search_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    if not query:
        await update.message.reply_text("Write something first :)")
        return

    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_API_KEY}"

    try:
        data = requests.get(url, timeout=10).json()
    except:
        await update.message.reply_text("❌ Connection error to Google Books.")
        return

    if "items" not in data:
        await update.message.reply_text("❌ No results found.")
        return

    for item in data["items"][:5]:
        info = item.get("volumeInfo", {})
        title = info.get("title", "Unknown")
        authors = ", ".join(info.get("authors", ["Unknown"]))
        desc = info.get("description", "No description")[:400]
        thumbnail = info.get("imageLinks", {}).get("thumbnail")
        buy_link = item.get("saleInfo", {}).get("buyLink", "No buy link available")

        text = (
            f"📖 *{title}*\n"
            f"👤 {authors}\n\n"
            f"{desc}...\n\n"
            f"🔗 More info:\n{buy_link}"
        )

        if thumbnail:
            await update.message.reply_photo(
                photo=thumbnail,
                caption=text,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(text, parse_mode="Markdown")

app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_book))

# ===============================
# Flask Web Server
# ===============================
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, app_telegram.bot)

    asyncio.run(app_telegram.process_update(update))
    return "OK"

# ===============================
# Set webhook when server starts
# ===============================
@app.before_first_request
def set_webhook():
    bot = Bot(token=TOKEN)
    bot.delete_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}")

# ===============================
# Run Server
# ===============================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
