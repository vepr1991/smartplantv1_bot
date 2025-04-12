import os
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")

if not BOT_TOKEN or not FIREBASE_DB_URL:
    raise ValueError("❌ Не заданы BOT_TOKEN или FIREBASE_DB_URL")

# Инициализация Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": FIREBASE_DB_URL
    })

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📊 Статус", "⚙ Настройки"],
        ["🔄 Обновить"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я SmartPlant 🌱\nВыбери действие:",
        reply_markup=reply_markup
    )

# Обработка reply-кнопок
async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Статус":
        try:
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
        except Exception as e:
            await update.message.reply_text(f"⚠ Ошибка при получении данных: {e}")

    elif text == "⚙ Настройки":
        await update.message.reply_text("⚙ Настройки пока не реализованы 🙂")

    else:
        await update.message.reply_text("🤖 Я не понял команду. Выбери кнопку ниже 👇")

# Запуск
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, reply_handler))

    print("✅ Бот SmartPlant запущен и слушает Telegram")
    app.run_polling()
