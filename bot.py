import os
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes,
    filters, ConversationHandler
)
from dotenv import load_dotenv

# Загрузка .env переменных
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")

if not BOT_TOKEN or not FIREBASE_DB_URL:
    raise ValueError("❌ Не заданы BOT_TOKEN или FIREBASE_DB_URL")

# Firebase инициализация
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})

# Состояния
WAITING_FOR_PLANT_NAME = 1
WAITING_FOR_DELETE_NAME = 2

# Главное меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📊 Статус"), KeyboardButton("➕ Добавить растение")],
        [KeyboardButton("❌ Удалить растение")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выбери действие:", reply_markup=reply_markup)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я SmartPlant 🌿")
    await show_main_menu(update, context)

# 📊 Статус
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plants_ref = db.reference("plants").get()
    if not plants_ref:
        await update.message.reply_text("😢 У вас пока нет ни одного растения.")
        return

    reply = "🌱 *Статус растений:*\n"
    for name, data in plants_ref.items():
        plant_data = data.get("data", {})
        temp = plant_data.get("temperature", "—")
        hum = plant_data.get("humidity", "—")
        soil = plant_data.get("soilMoisture", "—")
        reply += f"\n🔹 *{name}*\n🌡 {temp}°C | 💧 {hum}% | 🌱 {soil}%"

    await update.message.reply_text(reply, parse_mode='Markdown')
    await show_main_menu(update, context)

# ➕ Добавить
async def add_plant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя нового растения:")
    return WAITING_FOR_PLANT_NAME

async def save_new_plant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plant_name = update.message.text.strip()
    ref = db.reference(f"plants/{plant_name}")
    if ref.get():
        await update.message.reply_text("⚠ Растение с таким именем уже существует.")
    else:
        ref.set({
            "data": {
                "temperature": 0,
                "humidity": 0,
                "soilMoisture": 0
            }
        })
        await update.message.reply_text(f"✅ Растение *{plant_name}* добавлено!", parse_mode='Markdown')
    await show_main_menu(update, context)
    return ConversationHandler.END

# ❌ Удалить
async def delete_plant_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plants_ref = db.reference("plants").get()
    if not plants_ref:
        await update.message.reply_text("😢 У вас пока нет растений для удаления.")
        return ConversationHandler.END

    plant_names = list(plants_ref.keys())
    buttons = [[KeyboardButton(name)] for name in plant_names]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Введите имя растения, которое хотите удалить:", reply_markup=reply_markup)
    return WAITING_FOR_DELETE_NAME

async def confirm_delete_plant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plant_name = update.message.text.strip()
    ref = db.reference(f"plants/{plant_name}")
    if ref.get():
        ref.delete()
        await update.message.reply_text(f"🗑 Растение {plant_name} удалено.")
    else:
        await update.message.reply_text("❌ Растение не найдено.")
    await show_main_menu(update, context)
    return ConversationHandler.END

# 🚫 Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Действие отменено.")
    await show_main_menu(update, context)
    return ConversationHandler.END

# Запуск
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("📊 Статус"), status))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("➕ Добавить растение"), add_plant)],
        states={WAITING_FOR_PLANT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_plant)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("❌ Удалить растение"), delete_plant_request)],
        states={WAITING_FOR_DELETE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete_plant)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    print("✅ Бот SmartPlant запущен и слушает Telegram")
    app.run_polling()
