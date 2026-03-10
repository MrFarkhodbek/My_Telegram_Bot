import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging sozlash
logging.basicConfig(level=logging.INFO)

# Render'dan atrof-muhit o'zgaruvchilarini olish
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# DeepSeek API sozlamalari
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Flask ilovasi
app = Flask(__name__)

# Bot va Application
bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Men DeepSeek AI bilan ishlaydigan botman. Savollaringizni yozing.")

# Xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Siz yordamchi AI botsiz."},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": False
            },
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        ai_response = data["choices"][0]["message"]["content"]
        await update.message.reply_text(ai_response)
        
    except requests.exceptions.Timeout:
        await update.message.reply_text("❌ So'rov vaqti tugadi. Qayta urinib ko'ring.")
    except Exception as e:
        logging.error(f"API xatosi: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.")

# Handlerlarni qo'shish
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f"/{TELEGRAM_TOKEN}", methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    update = Update.de_json(request.get_json(force=True), bot)
    application.process_update(update)
    return "OK", 200

@app.route('/')
def index():
    return "Bot ishga tushdi! DeepSeek API ulangan."

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
