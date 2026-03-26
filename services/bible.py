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
    # reference like 'John 3:16' => book='John', chapter='3'
    if not reference:
        raise ValueError('Reference required')

    # parse book/chapter from reference
    # e.g. '1 Chronicles 5:2', 'John 3:16', 'Song of Solomon 2:4'
    import re
    m = re.match(r'^(.+?)\s+(\d+):\d+$', reference)
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


def get_random_verse():
    try:
        random_verse = _fetch_random_verse()
    except Exception:
        return "📖 Unable to fetch chapter right now."

    reference = random_verse.get('reference')
    if not reference:
        return "📖 Unable to fetch chapter right now."

    try:
        english = _fetch_chapter(reference)
    except Exception:
        return "📖 Unable to fetch chapter right now."

    eng_text = english.get('text', '')

    message = f"📖 {reference}\n{eng_text}"

    return message