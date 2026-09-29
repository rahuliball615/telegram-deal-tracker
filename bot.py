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

    params = {"timeout": 20}

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

    if "amazon." in url or "amzn.in" in url:
        return "Amazon"

    if "flipkart.com" in url:
        return "Flipkart"

    if "croma.com" in url:
        return "Croma"

    if "reliancedigital.in" in url:
        return "Reliance Digital"

    return "Unknown"


def handle_message(message):
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    print("Message:", text)

    if text == "/start":
        send_message(
            chat_id,
            "Welcome to My Deal Tracker!\n\n"
            "Supported stores:\n"
            "- Amazon\n"
            "- Flipkart\n"
            "- Croma\n"
            "- Reliance Digital\n\n"
            "Product track karne ke liye:\n"
            "/track PRODUCT_LINK\n\n"
            "List ke liye:\n"
            "/list"
        )

    elif text.startswith("/track "):
        url = text[7:].strip()

        if not is_supported_url(url):
            send_message(
                chat_id,
                "Ye website supported nahi hai.\n\n"
                "Supported:\n"
                "Amazon\n"
                "Flipkart\n"
                "Croma\n"
                "Reliance Digital"
            )
            return

        site = get_site_name(url)

        send_message(
            chat_id,
            "Tracking started!\n\n"
            f"Store: {site}\n"
            f"Link: {url}\n\n"
            "Price checking next step mein add hoga."
        )

    elif text == "/list":
        send_message(
            chat_id,
            "Tracking system active hai.\n\n"
            "Price tracking next step mein add karenge."
        )

    else:
        send_message(
            chat_id,
            "Command samajh nahi aayi.\n\n"
            "Use:\n"
            "/track PRODUCT_LINK"
        )


def main():
    print("My Deal Tracker started")

    end_time = time.time() + 240

    while time.time() < end_time:
        updates = get_updates()

        for update in updates:
            message = update.get("message")

            if message:
                handle_message(message)

        time.sleep(1)

    print("Bot run finished")


if __name__ == "__main__":
    main()
