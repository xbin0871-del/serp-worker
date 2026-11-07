import os
import requests
from flask import Flask, request

TOKEN = "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA"
app = Flask(__name__)

# 按钮回调后的回复文字
ANSWER = {
    "ok": "✅ 已确认，客服跟进中",
    "check": "🔍 已标记核查",
    "reject": "❌ 已驳回",
}

@app.get("/")
def home():
    return "ok", 200

@app.post(f"/{TOKEN}")
def cb():
    d = request.get_json(silent=True) or {}
    chat_id = None

    # 1) 普通消息（/verify 等）
    msg = d.get("message")
    if msg:
        chat_id = msg.get("chat", {}).get("id")
        text = (msg.get("text") or "").strip()
        if text == "/verify":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": "✅ 验证已收到，服务正常运行中"},
                timeout=10,
            )
        return "ok", 200

    # 2) 按钮回调
    q = d.get("callback_query")
    if not q or "id" not in q:
        return "ok", 200

    act = q.get("data")
    chat_id = q.get("message", {}).get("chat", {}).get("id")

    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
            json={"callback_query_id": q["id"], "text": ANSWER.get(act, "已收到")},
            timeout=10,
        )
        if chat_id:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": f"处理：{act or '按钮'}"},
                timeout=10,
            )
        print(f"点击: {act}")
    except Exception as e:
        print(f"处理异常: {e}")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
