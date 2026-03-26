import requests


def _fetch_verse(translation=None):
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


def get_random_verse():
    try:
        english = _fetch_verse()
    except Exception:
        return "📖 Unable to fetch verse right now."

    amharic = None
    try:
        amharic = _fetch_verse(translation='am')
    except Exception:
        amharic = None

    reference = english.get('reference', 'Unknown Reference')
    eng_text = english.get('text', '')
    am_text = amharic.get('text', '') if amharic and amharic.get('text') else None

    message = f"📖 {reference}\n{eng_text}"
    if am_text:
        message += f"\n\nአማርኛ:\n{am_text}"

    return message