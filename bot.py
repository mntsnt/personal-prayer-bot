import random
import json
import requests
import logging
import pytz

from datetime import time, datetime
from pathlib import Path
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from config import TOKEN, CHAT_ID

# Day count persistence
DAY_COUNT_FILE = Path('day_count.txt')
LAST_DATE_FILE = Path('last_date.txt')

def load_day_count():
    if DAY_COUNT_FILE.exists():
        try:
            return int(DAY_COUNT_FILE.read_text().strip())
        except ValueError:
            return 1
    return 1

def save_day_count(count):
    DAY_COUNT_FILE.write_text(str(count))

def get_current_day():
    now = datetime.now(pytz.timezone("Africa/Addis_Ababa"))
    current_date = now.date()
    
    if LAST_DATE_FILE.exists():
        last_date_str = LAST_DATE_FILE.read_text().strip()
        last_date = datetime.fromisoformat(last_date_str).date()
        if current_date > last_date:
            day_count = load_day_count() + 1
            save_day_count(day_count)
            LAST_DATE_FILE.write_text(current_date.isoformat())
        else:
            day_count = load_day_count()
    else:
        day_count = 1
        save_day_count(1)
        LAST_DATE_FILE.write_text(current_date.isoformat())
    
    return day_count

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
    singer = song.get('singer', song.get('album', 'Unknown'))
    album = song.get('album', 'Unknown')

    return f"🎵 {title}\n👤 {singer}\n💿 {album}\n🔗 Find this song: https://t.me/mezmurarchive/7484"

# ----------------------------
# Bible Verse Logic
# ----------------------------
from services.bible import get_random_verse

# ----------------------------
# Daily Message Function
# ----------------------------
async def send_morning(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Sending morning message...")

    # Get day and count
    now = datetime.now(pytz.timezone("Africa/Addis_Ababa"))
    day_name = now.strftime("%A")
    day_count = get_current_day()

    verse = get_random_verse()
    song = get_random_song()

    message = f"""
☀️ Good Morning, {day_name}! Have a bright day. (Day {day_count})

{verse}

🎧 Worship:
{song}
"""
    await context.bot.send_message(chat_id=CHAT_ID, text=message)

    # Send approval buttons
    keyboard = [
        [InlineKeyboardButton("✅ Heard Music", callback_data="music_yes"),
         InlineKeyboardButton("❌ Didn't Hear", callback_data="music_no")],
        [InlineKeyboardButton("📖 Read Verse", callback_data="verse_yes"),
         InlineKeyboardButton("❌ Didn't Read", callback_data="verse_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=CHAT_ID, text="Did you hear the music and read the verse?", reply_markup=reply_markup)


async def send_evening(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Sending evening message...")

    # Get day and count
    now = datetime.now(pytz.timezone("Africa/Addis_Ababa"))
    day_name = now.strftime("%A")
    day_count = get_current_day()

    verse = get_random_verse()
    song = get_random_song()

    message = f"""
🌙 Good Evening, {day_name}! Have a good night. (Day {day_count})

{verse}

🎧 Worship:
{song}
"""
    await context.bot.send_message(chat_id=CHAT_ID, text=message)

    # Send approval buttons
    keyboard = [
        [InlineKeyboardButton("✅ Heard Music", callback_data="music_yes"),
         InlineKeyboardButton("❌ Didn't Hear", callback_data="music_no")],
        [InlineKeyboardButton("📖 Read Verse", callback_data="verse_yes"),
         InlineKeyboardButton("❌ Didn't Read", callback_data="verse_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=CHAT_ID, text="Did you hear the music and read the verse?", reply_markup=reply_markup)

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
# Callback Handler for Buttons
# ----------------------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "music_yes":
        response = "Great! Glad you heard the music. 🎵"
    elif data == "music_no":
        response = "No worries, try listening later. 🎵"
    elif data == "verse_yes":
        response = "Wonderful! Keep reading the Word. 📖"
    elif data == "verse_no":
        response = "That's okay, take your time with the verse. 📖"
    else:
        response = "Unknown action."

    await query.edit_message_text(text=response)

# ----------------------------
# Main App
# ----------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verse", verse_command))
    app.add_handler(CommandHandler("song", song_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    # ----------------------------
    # Scheduler (Addis Ababa Timezone)
    # ----------------------------
    tz = pytz.timezone("Africa/Addis_Ababa")

    # Morning at 11:30 AM
    app.job_queue.run_daily(
        send_morning,
        time=time(hour=5, minute=0, tzinfo=tz)
    )

    # Evening at 9:00 PM
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