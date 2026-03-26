import random
import json
import requests
import logging
import pytz

from datetime import time
from pathlib import Path
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from config import TOKEN, CHAT_ID

# Load songs list from JSON file
songs_file = Path('songs_list.json')
if not songs_file.exists():
    raise FileNotFoundError('songs_list.json not found; run convert_songs_to_json.py first')

with songs_file.open(encoding='utf-8') as f:
    songs = json.load(f)

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

    title = song.get('title', 'Unknown Title')
    artist = song.get('artist', 'Unknown')
    album = song.get('album', 'Unknown')
    path = song.get('file_path', '')

    return f"🎵 {title}\n👤 {artist}\n💿 {album}\n📁 {path}"

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
        time=time(hour=11, minute=30, tzinfo=tz)
    )

    # Evening at 6:00 PM
    app.job_queue.run_daily(
        send_evening,
        time=time(hour=21, minute=0, tzinfo=tz)
    )

    logging.info("Bot started successfully...")
    app.run_polling()

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    main()