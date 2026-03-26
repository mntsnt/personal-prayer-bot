import requests


from urllib.parse import quote_plus


def _fetch_random_verse(translation=None):
    url = "https://bible-api.com/?random=verse"
    if translation:
        url += f"&translation={translation}"

    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()

    return {
        'reference': data.get('reference'),
        'text': data.get('text', '').strip()
    }


def _fetch_chapter(reference):
    # reference like 'Genesis 1' => book='Genesis', chapter='1'
    if not reference:
        raise ValueError('Reference required')

    # parse book/chapter from reference
    # e.g. 'Genesis 1', 'John 3'
    import re
    m = re.match(r'^(.+?)\s+(\d+)$', reference)
    if not m:
        raise ValueError(f'Could not parse chapter from reference: {reference}')

    book = m.group(1).strip()
    chapter = m.group(2).strip()

    book_chapter = f"{book} {chapter}"
    url = f"https://bible-api.com/{quote_plus(book_chapter)}"

    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()

    text = data.get('text') or ''
    return {
        'reference': book_chapter,
        'text': text.strip()
    }


import random

# Bible books and their chapter counts (Old and New Testament)
BIBLE_BOOKS = {
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
    "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36, "Ezra": 10,
    "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalms": 150, "Proverbs": 31,
    "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66, "Jeremiah": 52, "Lamentations": 5,
    "Ezekiel": 48, "Daniel": 12, "Hosea": 14, "Joel": 3, "Amos": 9,
    "Obadiah": 1, "Jonah": 4, "Micah": 7, "Nahum": 3, "Habakkuk": 3,
    "Zephaniah": 3, "Haggai": 2, "Zechariah": 14, "Malachi": 4,
    "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21, "Acts": 28,
    "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6, "Ephesians": 6,
    "Philippians": 4, "Colossians": 4, "1 Thessalonians": 5, "2 Thessalonians": 3, "1 Timothy": 6,
    "2 Timothy": 4, "Titus": 3, "Philemon": 1, "Hebrews": 13, "James": 5,
    "1 Peter": 5, "2 Peter": 3, "1 John": 5, "2 John": 1, "3 John": 1,
    "Jude": 1, "Revelation": 22
}

def get_random_verse():
    try:
        # Select random book
        book = random.choice(list(BIBLE_BOOKS.keys()))
        max_chapter = BIBLE_BOOKS[book]
        chapter = random.randint(1, max_chapter)
        
        reference = f"{book} {chapter}"
        chapter_data = _fetch_chapter(reference)
    except Exception:
        return "📖 Unable to fetch chapter right now."

    text = chapter_data.get('text', '').strip()
    if not text:
        return "📖 Unable to fetch chapter right now."

    message = f"📖 {reference}\n{text}"

    return message