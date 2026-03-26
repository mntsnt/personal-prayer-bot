import random
import os
import requests
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from config import TOKEN, CHAT_ID

# Import songs from another Python file
from songs_list import songs, last_song

# ----------------------------
# Random Song Function
# ----------------------------
def get_random_song():
    global last_song
    song = random.choice(songs)
    while song == last_song:
        song = random.choice(songs)
    last_song = song
    return f"🎵 {song}"

# ----------------------------
# Bible Verse Function
# ----------------------------
def get_random_verse():
    try:
        res = requests.get("https://bible-api.com/?random=verse")
        data = res.json()
        verse = data["text"].strip()
        reference = data["reference"]
        return f"📖 {reference}\n{verse}"
    except:
        return "📖 Could not fetch verse. Check your connection."

# ----------------------------
# Daily Message
# ----------------------------
def send_daily():
    verse = get_random_verse()
    song = get_random_song()
    message = f"☀️ Daily Message\n\n{verse}\n\n{song}"
    bot.send_message(chat_id=CHAT_ID, text=message)

# ----------------------------
# Telegram Commands
# ----------------------------
bot = Bot(token=TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running ✅")

async def verse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_random_verse())

async def song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_random_song())

# ----------------------------
# Scheduler (Morning & Evening)
# ----------------------------
scheduler = BackgroundScheduler()
# scheduler.add_job(send_daily, 'cron', hour=6)   # morning
# scheduler.add_job(send_daily, 'cron', hour=18)  # evening

scheduler.add_job(send_daily, 'interval', minutes=1)

scheduler.start()

send_daily()

# ----------------------------
# Run Bot
# ----------------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("verse", verse_command))
app.add_handler(CommandHandler("song", song_command))
app.run_polling()


scheduler.add_job(send_daily, 'interval', minutes=1)