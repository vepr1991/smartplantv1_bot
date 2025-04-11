import os
import json
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import firebase_admin
from firebase_admin import credentials, db

# === Загрузка переменных из .env ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")

# === Проверка обязательных переменных ===
if not TOKEN:
    raise ValueError("❌ Переменная BOT_TOKEN не задана")
if not FIREBASE_DB_URL:
    raise ValueError("❌ Переменная FIREBASE_DB_URL не задана")
if not FIREBASE_CREDENTIALS_JSON:
    raise ValueError("❌ Переменная FIREBASE_CREDENTIALS_JSON не задана")

# === Инициализация Firebase напрямую из JSON (многострочный формат работает) ===
try:
    firebase_dict = json.loads(FIREBASE_CREDENTIALS_JSON)
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DB_URL
    })
except Exception as e:
    raise ValueError(f"❌ Ошибка инициализации Firebase: {e}")

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📊 Статус", "⚙ Настройки"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Я бот SmartPlant 🌱", reply_markup=reply_markup)

# === Команда /status ===
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ref = db.reference("plants/plant_001/data")
    data = ref.get() or {}
    temp = data.get("temperature", "—")
    hum = data.get("humidity", "—")
    soil = data.get("soilMoisture", "—")
    await update.message.reply_text(
        f"🌿 Состояние растения:\n"
        f"🌡 Температура: {temp}°C\n"
        f"💧 Влажность воздуха: {hum}%\n"
        f"🌱 Влажность почвы: {soil}%"
    )

# === Обработка текстовых кнопок ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "статус" in text:
        await status(update, context)
    elif "настройки" in text:
        await update.message.reply_text("⚙ Настройки пока не реализованы 🙂")
    else:
        await update.message.reply_text("🤖 Я понимаю только '📊 Статус' и '⚙ Настройки'.")

# === Запуск бота ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Бот SmartPlant запущен и слушает Telegram")
    app.run_polling()
