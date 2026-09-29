import os
import json
import requests

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"
DATA_FILE = "products.json"


def load_products():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)


def send_message(chat_id, text):
    requests.post(
        f"{API}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text
        },
        timeout=20
    )


def get_updates():
    response = requests.get(
        f"{API}/getUpdates",
        timeout=20
    )

    response.raise_for_status()
    return response.json()


def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if text == "/start":
        send_message(
            chat_id,
            "👋 Welcome!\n\n"
            "Product track karne ke liye:\n"
            "/track PRODUCT_LINK\n\n"
            "List dekhne ke liye:\n"
            "/list"
        )
        return

    if text.startswith("/track "):
        url = text[7:].strip()

        if "amazon." not in url and "flipkart.com" not in url:
            send_message(
                chat_id,
                "❌ Sirf Amazon ya Flipkart link bhejo."
            )
            return

        products = load_products()

        for product in products:
            if product["url"] == url:
                send_message(
                    chat_id,
                    "⚠️ Ye link already tracking mein hai."
                )
                return

        products.append({
            "url": url,
            "chat_id": chat_id,
            "last_price": None
        })

        save_products(products)

        send_message(
            chat_id,
            "✅ Tracking started!\n\n"
            f"🔗 {url}"
        )
        return

    if text == "/list":
        products = load_products()

        user_products = [
            p for p in products
            if str(p["chat_id"]) == str(chat_id)
        ]

        if not user_products:
            send_message(
                chat_id,
                "📭 Koi product tracking mein nahi hai."
            )
            return

        result = "📦 Your tracked products:\n\n"

        for number, product in enumerate(user_products, 1):
            result += f"{number}. {product['url']}\n\n"

        send_message(chat_id, result)
        return

    send_message(
        chat_id,
        "❓ Commands:\n\n"
        "/start\n"
        "/track LINK\n"
        "/list"
    )


def main():
    print("🤖 Checking Telegram updates...")

    result = get_updates()

    if not result.get("ok"):
        print("Telegram API error")
        return

    updates = result.get("result", [])

    for update in updates:
        message = update.get("message")

        if message:
            handle_message(message)

    print(f"Processed {len(updates)} update(s).")


if __name__ == "__main__":
    main()
