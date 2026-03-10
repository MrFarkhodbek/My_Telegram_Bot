import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# Logging sozlash
logging.basicConfig(level=logging.INFO)

# Bot tokenini olish
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Flask ilovasi
app = Flask(__name__)

# Bot va dispatcher
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# Handlerlar
def start(update, context):
    update.message.reply_text("Assalomu alaykum! Bot ishga tushdi.")

def echo(update, context):
    update.message.reply_text(update.message.text)

# Handlerlarni ro'yxatdan o'tkazish
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route('/')
def index():
    return "Bot ishga tushdi!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
