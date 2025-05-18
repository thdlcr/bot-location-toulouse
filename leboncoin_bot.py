import requests
from bs4 import BeautifulSoup
import time
import json
import os

from se_loger_scraper import fetch_se_loger_ads
from pap_scraper import fetch_pap_ads

def get_user_input():
    return {
        "ville": os.getenv("VILLE", "Toulouse"),
        "prix_max": int(os.getenv("PRIX_MAX", "1200")),
        "surface_min": int(os.getenv("SURFACE_MIN", "50")),
        "exterieur": os.getenv("EXT", "oui").lower() == "oui",
        "etage": os.getenv("ETAGE", "oui").lower() == "oui"
    }

def send_telegram_alert(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erreur envoi Telegram:", e)

def fetch_leboncoin_ads(config):
    base_url = "https://www.leboncoin.fr/recherche"
    params = {
        "category": "10",
        "locations": json.dumps([{"zipcode": "31000", "label": config["ville"], "city": config["ville"]}]),
        "real_estate_type": "1",
        "price": f"0-{config['prix_max']}",
        "square": f"{config['surface_min']}-"
    }
    try:
        res = requests.get(base_url, params=params)
        res.raise_for_status()
    except requests.RequestException as e:
        print("Erreur de récupération des annonces LeBonCoin :", e)
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/locations/" in href and href not in links:
            links.append("https://www.leboncoin.fr" + href)
    return links

def load_seen():
    if os.path.exists("seen.json"):
        with open("seen.json", "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open("seen.json", "w") as f:
        json.dump(list(seen), f)

def main():
    config = get_user_input()
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    seen = load_seen()

    while True:
        all_ads = []
        all_ads += fetch_leboncoin_ads(config)
        all_ads += fetch_se_loger_ads(config)
        all_ads += fetch_pap_ads(config)

        new_ads = [ad for ad in all_ads if ad not in seen]
        for ad in new_ads:
            send_telegram_alert(token, chat_id, f"Nouvelle annonce : {ad}")
            seen.add(ad)
        save_seen(seen)
        print(f"{len(new_ads)} nouvelles annonces envoyées.")
        time.sleep(600)

if __name__ == "__main__":
    main()
