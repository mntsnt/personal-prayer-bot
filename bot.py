import random
import requests
import logging
import pytz

from datetime import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from config import TOKEN, CHAT_ID
from songs_list import songs

# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ----------------------------
# Random Song Logic
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
# Bible Verse Logic
# ----------------------------
def get_random_verse():
    try:
        res = requests.get("https://bible-api.com/?random=verse")
        data = res.json()

        verse = data["text"].strip()
        reference = data["reference"]

        return f"📖 {reference}\n{verse}"

    except Exception as e:
        logging.error(f"Verse fetch error: {e}")
        return "📖 Unable to fetch verse right now."

# ----------------------------
# Daily Message Function
# ----------------------------
async def send_morning(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Sending morning message...")

    verse = get_random_verse()
    song = get_random_song()

    message = f"""
☀️ Good Morning

{verse}

🎧 Worship:
{song}
"""
    await context.bot.send_message(chat_id=CHAT_ID, text=message)


async def send_evening(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Sending evening message...")

    verse = get_random_verse()
    song = get_random_song()

    message = f"""
🌙 Good Evening

{verse}

🎧 Worship:
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
# Main App
# ----------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verse", verse_command))
    app.add_handler(CommandHandler("song", song_command))

    # ----------------------------
    # Scheduler (Addis Ababa Timezone)
    # ----------------------------
    tz = pytz.timezone("Africa/Addis_Ababa")

    # Morning at 6:00 AM
    app.job_queue.run_daily(
        send_morning,
        time=time(hour=6, minute=0, tzinfo=tz)
    )

    # Evening at 6:00 PM
    app.job_queue.run_daily(
        send_evening,
        time=time(hour=18, minute=0, tzinfo=tz)
    )

    logging.info("Bot started successfully...")
    app.run_polling()

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    main()