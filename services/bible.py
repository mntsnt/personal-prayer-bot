import requests

def get_random_verse():
    url = "https://bible-api.com/?random=verse"
    res = requests.get(url)
    data = res.json()

    verse = data["text"].strip()
    reference = data["reference"]

    return f"📖 {reference}\n{verse}"