import os
import json
from io import StringIO
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === Загрузка переменных из окружения (.env или Render) ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")

if not TOKEN:
    raise ValueError("❌ Переменная BOT_TOKEN не задана")
if not FIREBASE_DB_URL:
    raise ValueError("❌ Переменная FIREBASE_DB_URL не задана")
if not FIREBASE_CREDENTIALS_JSON:
    raise ValueError("❌ Переменная FIREBASE_CREDENTIALS_JSON не задана")

# === Инициализация Firebase ===
cred = credentials.Certificate(json.load(StringIO(FIREBASE_CREDENTIALS_JSON)))
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_DB_URL
})


# === Команда /start с reply-кнопками ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📊 Статус", "⚙ Настройки"]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await update.message.reply_text(
        "Привет! Я бот SmartPlant 🌱\nВот, чем могу помочь:",
        reply_markup=reply_markup
    )


# === /status и кнопка “Статус” ===
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


# === Обработка обычных сообщений (reply-кнопки) ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "статус" in text:
        await status(update, context)
    elif "настройки" in text:
        await update.message.reply_text("⚙ Настройки пока не реализованы 🙂")
    else:
        await update.message.reply_text("🤖 Я понимаю только '📊 Статус' и '⚙ Настройки'")


# === Обработка inline-кнопок (если решишь оставить) ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "status":
        await status(query, context)
    elif query.data == "settings":
        await query.edit_message_text("⚙ Настройки пока не реализованы 🙂")


# === Запуск бота ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Бот SmartPlant запущен и слушает Telegram")
    app.run_polling()
