
import os
from urllib.parse import urlparse

import requests
from flask import Flask, request, abort

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
API = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text):
    requests.post(
        f"{API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=15,
    ).raise_for_status()


def is_tiktok_url(value):
    try:
        parsed = urlparse(value)
        host = (parsed.hostname or "").lower()

        return (
            parsed.scheme == "https"
            and (host == "tiktok.com"
                 or host.endswith(".tiktok.com"))
        )
    except ValueError:
        return False


@app.get("/")
def home():
    return "TikTok bot is running!"


@app.post("/webhook")
def webhook():
    if request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    ) != WEBHOOK_SECRET:
        abort(403)

    update = request.get_json(silent=True) or {}
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id:
        return "OK"

    if text.startswith("/start"):
        send_message(
            chat_id,
            "أهلاً بيك! 👋\n"
            "أرسل رابط فيديو TikTok عام.\n"
            "راح أساعدك توصل لطريقة الحفظ الرسمية."
        )

    elif text.startswith("https://") and is_tiktok_url(text):
        send_message(
            chat_id,
            "✅ الرابط يبدو تابعاً لـ TikTok:\n"
            + text
            + "\n\n"
            "لحفظ الفيديو:\n"
            "1- افتح الفيديو داخل TikTok.\n"
            "2- اضغط مشاركة.\n"
            "3- اختر حفظ الفيديو إذا كان متاحاً.\n\n"
            "إذا خيار الحفظ غير موجود، فاحترم إعدادات "
            "صاحب المقطع."
        )

    else:
        send_message(
            chat_id,
            "أرسل رابط TikTok يبدأ بـ https://\n"
            "هذا البوت لا يقبل روابط مواقع أخرى."
        )

    return "OK"


# تسجيل Webhook تلقائياً عند التشغيل على Render
base_url = os.getenv("RENDER_EXTERNAL_URL")

if base_url:
    response = requests.post(
        f"{API}/setWebhook",
        json={
            "url": base_url.rstrip("/") + "/webhook",
            "secret_token": WEBHOOK_SECRET,
            "allowed_updates": ["message"],
        },
        timeout=15,
    )
    response.raise_for_status()
