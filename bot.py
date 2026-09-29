import os
import time
import requests

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

OFFSET = None


def send_message(chat_id, text):
    try:
        requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=20
        )
    except Exception as e:
        print("Send message error:", e)


def get_updates():
    global OFFSET

    params = {
        "timeout": 20
    }

    if OFFSET is not None:
        params["offset"] = OFFSET

    try:
        response = requests.get(
            f"{API}/getUpdates",
            params=params,
            timeout=30
        )

        data = response.json()

        if not data.get("ok"):
            print("Telegram API error:", data)
            return []

        updates = data.get("result", [])

        if updates:
            OFFSET = updates[-1]["update_id"] + 1

        return updates

    except Exception as e:
        print("Telegram error:", e)
        return []


def is_supported_url(url):
    supported_sites = [
        "amazon.",
        "amzn.in",
        "flipkart.com",
        "croma.com",
        "reliancedigital.in"
    ]

    return any(site in url.lower() for site in supported_sites)


def get_site_name(url):
    url = url.lower()

    if "amazon
