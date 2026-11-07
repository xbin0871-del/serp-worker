import os
import re
import requests
from flask import Flask, request

TOKEN = os.getenv("TOKEN")  # 需在 Render 环境变量中配置新 Token
ADMIN_ID = 8385371786
ADMIN_USER = "xbin0871"

REPORTS = {}
PENDING = {}
USERNAME_RE = re.compile(r"^@[a-zA-Z0-9_]+")
TG = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)

def send(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        requests.post(f"{TG}/sendMessage", json=data, timeout=5)
    except Exception as e:
        print(f"[发送异常] {e}")

def answer_cb(q_id, text="已收到"):
    if not q_id:
        return
    requests.post(f"{TG}/answerCallbackQuery", json={"callback_query_id": q_id, "text": text}, timeout=5)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    u = request.json
    if not u:
        return "ok"

    if "message" in u:
        msg = u["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"].get("id")
        username = msg["from"].get("username", "")
        text = msg.get("text", "").strip()

        if text == "/start":
            send(chat_id, "皇冠")
        elif text == "/verify":
            send(chat_id, "✅ 服务正常")
        elif USERNAME_RE.match(text):
            # 业务占位逻辑（保留原有 @xxx 交互）
            send(chat_id, "已收到指令")

    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
