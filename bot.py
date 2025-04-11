import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Загрузка переменных
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH")

# Инициализация Firebase
cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_DB_URL
})

# 📲 Команда /start с постоянными кнопками
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

# 📊 Обработка команды /status
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

# 💬 Обработка статичных кнопок (текста)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "статус" in text:
        await status(update, context)
    elif "настройки" in text:
        await update.message.reply_text("⚙ Настройки пока не реализованы 🙂")
    else:
        await update.message.reply_text("🤖 Я пока понимаю только '📊 Статус' или '⚙ Настройки'.")

# 🔘 Обработка inline-кнопок (если хочешь оставить)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "status":
        ref = db.reference("plants/plant_001/data")
        data = ref.get() or {}
        temp = data.get("temperature", "—")
        hum = data.get("humidity", "—")
        soil = data.get("soilMoisture", "—")

        await query.edit_message_text(
            f"🌿 Состояние растения:\n"
            f"🌡 Температура: {temp}°C\n"
            f"💧 Влажность воздуха: {hum}%\n"
            f"🌱 Влажность почвы: {soil}%"
        )
    elif query.data == "settings":
        await query.edit_message_text("⚙ Настройки пока не реализованы 🙂")

# ▶️ Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Бот запущен со статичными кнопками")
    app.run_polling()
