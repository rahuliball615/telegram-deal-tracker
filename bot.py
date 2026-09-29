import os
import time
import requests

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

OFFSET = None


def send_message(chat_id, text):
    requests.post(
        f"{API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=20
    )


def get_updates():
    global OFFSET

    params = {
        "timeout": 20
    }

    if OFFSET is not None:
        params["offset"] = OFFSET

    try:
        r = requests.get(
            f"{API}/getUpdates",
            params=params,
            timeout=30
        )

        data = r.json()

        if not data.get("ok"):
            return []

        updates = data.get("result", [])

        if updates:
            OFFSET = updates[-1]["update_id"] + 1

        return updates

    except Exception as e:
        print("Telegram error:", e)
        return []


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
            "👋 Welcome!\n\n"
            "Product track karne ke liye:\n"
            "/track PRODUCT_LINK\n\n"
            "List dekhne ke liye:\n"
            "/list"
        )

    elif text.startswith("/track "):
        url = text[7:].strip()

        if (
            "amazon." not in url
            and "amzn.in" not in url
            and "flipkart.com" not in url
        ):
            send_message(
                chat_id,
                "❌ Sirf Amazon ya Flipkart link bhejo."
            )
            return

        send_message(
            chat_id,
            "✅ Tracking started!\n\n" + url
        )

    elif text == "/list":
        send_message(
            chat_id,
            "📦 Abhi tracking system setup ho raha hai.\n"
            "Price tracking next step mein add karenge."
        )

    else:
        send_message(
            chat_id,
            "❓ Command samajh nahi aayi.\n\n"
            "Use:\n"
            "/track PRODUCT_LINK"
        )


def main():
    print("🤖 Bot started")

    # Telegram ke pending updates process karo
    # aur continuously ~4 minutes tak bot ko alive rakho.
    end_time = time.time() + 240

    while time.time() < end_time:
        updates = get_updates()

        for update in updates:
            message = update.get("message")

            if message:
                handle_message(message)

        time.sleep(1)

    print("⏹️ Bot run finished")


if __name__ == "__main__":
    main()
