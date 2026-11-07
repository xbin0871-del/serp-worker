# callback_handler.py
import os
import json
import re
import requests
from flask import Flask, request

TOKEN = "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA"
ADMIN_ID = 8385371786          # 只有这个 ID 能发起报备
ADMIN_USER = "xbin0871"        # 替换为你的 @用户名（可选）

REPORTS = {}
PENDING = {}
USERNAME_RE = re.compile(r"^@[a-zA-Z0-9_]{5,}$")

TG = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)

def _post(method, **kw):
    try:
        r = requests.post(f"{TG}/{method}", json=kw, timeout=15)
        return r
    except Exception as e:
        print(f"[TG {method} 异常] {e}")
        return None

def send(chat_id, text, reply_markup=None, reply_to=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: data["reply_markup"] = json.dumps(reply_markup)
    if reply_to: data["reply_to_message_id"] = reply_to
    return _post("sendMessage", **data)

def answer_cb(cb_id, text=""):
    if not cb_id: return
    _post("answerCallbackQuery", callback_query_id=str(cb_id), text=str(text)[:200], cache_time=1)

def is_admin(user):
    return user.get("id") == ADMIN_ID

@app.route(f"/{TOKEN}", methods=["POST"])
def cb():
    u = request.get_json(silent=True) or {}
    msg = u.get("message") or {}
    cb_q = u.get("callback_query") or {}
    
    # 处理回调按钮（安全取值，防止 KeyError）
    if cb_q:
        qid = cb_q.get("id")
        data = cb_q.get("data", "")
        user = cb_q.get("from") or {}
        msg = cb_q.get("message") or {}
        chat_id = msg.get("chat", {}).get("id")
        
        if data.startswith("rep_ok@"):
            target = data.split("@", 1)[1]
            answer_cb(qid, "已确认")
            send(chat_id, f"✅ <b>报备成功</b>\n对象：@{target}\n发起人：@{ADMIN_USER}")
            return "ok", 200
        elif data.startswith("rep_reject@"):
            target = data.split("@", 1)[1]
            answer_cb(qid, "已拒绝")
            send(chat_id, f"❌ <b>报备已拒绝</b>\n对象：@{target}")
            return "ok", 200
        else:
            answer_cb(qid, "已收到")
            return "ok", 200

    # 处理普通消息/指令
    text = msg.get("text", "")
    user = msg.get("from") or {}
    chat_id = msg.get("chat", {}).get("id")
    msg_id = msg.get("message_id")
    
    if not text: return "ok", 200

    # 等待输入对方 @用户名
    if str(user.get("id")) in PENDING:
        if not USERNAME_RE.match(text.strip()):
            send(chat_id, "⚠️ 格式不对，请输入对方的 <b>@用户名</b>，例如 <code>@xiaoming_88</code>", reply_to=msg_id)
            return "ok", 200
        
        target = text.strip()
        PENDING.pop(str(user.get("id")), None)
        markup = {"inline_keyboard": [[
            {"text": "✅ 确认报备", "callback_data": f"rep_ok@{target[1:]}"},
            {"text": "❌ 拒绝", "callback_data": f"rep_reject@{target[1:]}"},
        ]]}
        send(chat_id,
             f"📢 <b>公群担保报备</b>\n发起人：@{ADMIN_USER}\n对象：<a href='https://t.me/{target[1:]}'>{target}</a>\n\n请核对后点击按钮。",
             markup=markup, reply_to=msg_id)
        return "ok", 200

    if text == "/start":
        send(chat_id, "👋 <b>皇冠担保报备机器人</b>\n\n▸ /report 发起报备（仅管理员）\n▸ /status 本群查询\n▸ /my 我的报备", reply_to=msg_id)
    elif text in ("/verify", "/status"):
        send(chat_id, "✅ 服务正常 · Webhook 已连通", reply_to=msg_id)
    elif text in ("/report", "公群报备"):
        if not is_admin(user):
            send(chat_id, "⚠️ 只有管理员能发起报备。", reply_to=msg_id)
        else:
            PENDING[str(user.get("id"))] = {"chat_id": chat_id}
            send(chat_id, "📝 请回复本条，输入<b>对方的 @用户名</b>（如 <code>@xiaoming_88</code>）：", reply_to=msg_id)
    elif text == "/my":
        send(chat_id, "📁 我的报备记录查询（演示）", reply_to=msg_id)
        
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
