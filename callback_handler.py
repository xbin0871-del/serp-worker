# callback_handler.py
import os
import json
import requests
from flask import Flask, request

TOKEN = "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA"

app = Flask(__name__)

# 按钮 data -> 回复文案
ANSWER = {
    "ok": "✅ 已确认，客服跟进中",
    "check": "🔍 已标记核查",
    "reject": "❌ 已驳回",
}

TG = f"https://api.telegram.org/bot{TOKEN}"


def send(chat_id, text, reply_to=None):
    """安全地给 Telegram 发消息，失败只记日志不炸。"""
    if not chat_id:
        return
    payload = {"chat_id": chat_id, "text": text}
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    try:
        requests.post(f"{TG}/sendMessage", json=payload, timeout=15)
    except Exception as e:
        print(f"发送消息失败: {e}")


def answer_cb(cb_id, text):
    """安全地响应按钮点击（让按钮上的转圈消失）。"""
    if not cb_id:
        return
    try:
        requests.post(
            f"{TG}/answerCallbackQuery",
            json={"callback_query_id": str(cb_id), "text": text, "show_alert": False},
            timeout=15,
        )
    except Exception as e:
        print(f"回应回调失败: {e}")


@app.get("/")
def health():
    return "🤖 bot is running", 200


@app.post(f"/{TOKEN}")
def webhook():
    # silent=True：请求体为空/非法 JSON 也不炸
    d = request.get_json(silent=True)
    if not isinstance(d, dict):
        return "ok", 200

    # ============ 1. 按钮回调 ============
    q = d.get("callback_query")
    if isinstance(q, dict):
        cb_id = q.get("id")                 # 用 .get，绝不会 KeyError
        act = q.get("data") or ""
        msg = q.get("message") or {}
        chat_id = (msg.get("chat") or {}).get("id")
        user = (q.get("from") or {}).get("username") or (q.get("from") or {}).get("id")

        print(f"点击: {act} | 用户: {user}")

        answer_cb(cb_id, ANSWER.get(act, "已收到"))

        if chat_id:
            send(chat_id, f"处理：{act or '按钮'}\n{ANSWER.get(act, '')}")
        return "ok", 200

    # ============ 2. 普通消息 ============
    msg = d.get("message")
    if isinstance(msg, dict):
        chat_id = (msg.get("chat") or {}).get("id")
        user = (msg.get("from") or {}).get("username") or (msg.get("from") or {}).get("id")
        text = (msg.get("text") or "").strip()

        print(f"消息: {text!r} | 用户: {user}")

        if text == "/start":
            send(
                chat_id,
                "👋 皇冠担保报备机器人已就绪\n"
                "/verify  验证连通性\n"
                "/report  提交报备\n"
                "/status  查看状态",
                reply_to=msg.get("message_id"),
            )
        elif text == "/verify":
            send(chat_id, "✅ 验证已收到，服务正常运行中", reply_to=msg.get("message_id"))
        elif text == "/report":
            send(chat_id, "📝 请按格式发送：订单号 + 金额 + 对方账号", reply_to=msg.get("message_id"))
        elif text == "/status":
            send(chat_id, "🟢 服务在线，Webhook 已连通", reply_to=msg.get("message_id"))
        # 其他消息一律静默，不报错
        return "ok", 200

    # ============ 3. 其他更新（编辑/加入群组等）一律忽略 ============
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
