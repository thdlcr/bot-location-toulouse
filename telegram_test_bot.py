import os
import requests

TOKEN = os.getenv("7319987174:AAHXXyubAECWYSti4xMRnzX09503a7s0nUQ")
CHAT_ID = os.getenv("5195811569")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

# ✅ Envoi immédiat d’un message de test
send_telegram_message("✅ Bot bien démarré et envoie un message de test !")
