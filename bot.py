import os
import json
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")

if not BOT_TOKEN or not FIREBASE_DB_URL:
    raise ValueError("❌ Не заданы BOT_TOKEN или FIREBASE_DB_URL")

try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})
except Exception as e:
    raise ValueError(f"❌ Ошибка инициализации Firebase: {e}")

# Команды Telegram-бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Статус", callback_data="status")],
        [InlineKeyboardButton("⚙ Настройки", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌿 Добро пожаловать в SmartPlant!", reply_markup=reply_markup)

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

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Бот SmartPlant запущен")
    app.run_polling()
