import random
import requests
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from config import TOKEN, CHAT_ID
from songs_list import songs

# ----------------------------
# Logging (important for debugging)
# ----------------------------
logging.basicConfig(level=logging.INFO)

# ----------------------------
# Random Song Function
# ----------------------------
last_song = None

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

    except Exception as e:
        logging.error(f"Verse error: {e}")
        return "📖 Could not fetch verse."

# ----------------------------
# Daily Message Sender
# ----------------------------
async def send_daily(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Running scheduled task...")

    verse = get_random_verse()
    song = get_random_song()

    message = f"""
☀️ Daily Message

{verse}

{song}
"""

    await context.bot.send_message(chat_id=CHAT_ID, text=message)

# ----------------------------
# Commands
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running ✅")

async def verse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_random_verse())

async def song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_random_song())

# ----------------------------
# Main Function
# ----------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verse", verse_command))
    app.add_handler(CommandHandler("song", song_command))

    # ----------------------------
    # Scheduler (JobQueue)
    # ----------------------------

    # 🔥 TEST MODE (every 1 minute)
    app.job_queue.run_repeating(send_daily, interval=60, first=10)

    # ✅ PRODUCTION MODE (uncomment later)
    # app.job_queue.run_daily(send_daily, time=time(hour=6, minute=0))
    # app.job_queue.run_daily(send_daily, time=time(hour=18, minute=0))

    # ----------------------------
    # Run Bot
    # ----------------------------
    logging.info("Bot started...")
    app.run_polling()

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    main()