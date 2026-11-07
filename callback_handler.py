# callback_handler.py
import os
import re
import json
import requests
from flask import Flask, request

TOKEN = "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA"
ADMIN_ID = 8385371786  # 只有你（8385371786）能发起报备

REPORTS = {}   # 报备单存储（内存，Render 休眠会清空，够测试用）
PENDING = {}   # 管理员发起后，下一条消息当作"对方用户名"

TG = f"https://api.telegram.org/bot{TOKEN}"

# 校验 @用户名：@ 开头，后面 5 位以上，只允许字母数字下划线
USERNAME_RE = re.compile(r"^@[\w]{5,}$")


def _post(method, **kw):
    try:
        r = requests.post(f"{TG}/{method}", json=kw, timeout=15)
        if not r.ok:
            print(f"[TG {method} {r.status_code}] {r.text[:200]}")
        return r
    except Exception as e:
        print(f"[TG {method} 异常] {e}")
        return None


def send(chat_id, text, markup=None, reply_to=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if markup: data["reply_markup"] = json.dumps(markup)
    if reply_to: data["reply_to_message_id"] = reply_to
    return _post("sendMessage", **data)


def answer_cb(cb_id, text="", alert=False):
    if not cb_id:
        return
    _post("answerCallbackQuery",
          callback_query_id=str(cb_id), text=str(text)[:200],
          show_alert=bool(alert), cache_time=1)


def is_admin(user):
    return user and str(user.get("id")) == str(ADMIN_ID)


app = Flask(__name__)


@app.get("/")
def health():
    return "🤖 bot running", 200


@app.post(f"/{TOKEN}")
def webhook():
    d = request.get_json(silent=True)
    if not isinstance(d, dict):
        return "ok", 200

    # ================= 1. 按钮回调 =================
    q = d.get("callback_query")
    if isinstance(q, dict):
        cb_id = q.get("id")
        msg = q.get("message") or {}
        chat_id = (msg.get("chat") or {}).get("id")
        user = q.get("from") or {}
        who = f"@{user.get('username')}" if user.get("username") else user.get("first_name") or user.get("id")

        act = q.get("data") or ""
        # 格式：rep_{ok|reject}@{对方用户名}
        if act.startswith("rep_"):
            try:
                _, decision, target = act.split("@", 2)
            except ValueError:
                answer_cb(cb_id, "数据异常")
                return "ok", 200

            key = f"report:{chat_id}:{target.lower()}"
            REPORTS[key] = {"status": decision, "who": who, "target": target}

            if decision == "ok":
                text = f"✅ <b>已确认报备</b>\n对象：{target}\n确认人：{who}"
                answer_cb(cb_id, "已确认，谢谢！", alert=True)
            else:
                text = f"❌ <b>已拒绝报备</b>\n对象：{target}\n拒绝人：{who}"
                answer_cb(cb_id, "已拒绝", alert=True)

            _post("editMessageText", chat_id=chat_id,
                  message_id=msg.get("message_id"), text=text, parse_mode="HTML")
            return "ok", 200

        answer_cb(cb_id, "已收到")
        return "ok", 200

    # ================= 2. 普通消息 =================
    msg = d.get("message")
    if not isinstance(msg, dict):
        return "ok", 200

    chat_id = (msg.get("chat") or {}).get("id")
    user = msg.get("from") or {}
    text = (msg.get("text") or "").strip()
    msg_id = msg.get("message_id")

    # ---- 管理员正在"等待输入对方用户名" ----
    if is_admin(user) and str(user.get("id")) in PENDING:
        if not USERNAME_RE.match(text):
            send(chat_id,
                 "⚠️ 格式不对，请输入对方的 <b>@用户名</b>，例如 <code>@xiaoming_88</code>\n"
                 "（不要带空格，只要一个 @用户名）", reply_to=msg_id)
            return "ok", 200

        target = text.strip()          # 例如 @xiaoming_88
        PENDING.pop(str(user.get("id")), None)

        markup = {"inline_keyboard": [[
            {"text": "✅ 确认报备", "callback_data": f"rep_ok@{target}"},
            {"text": "❌ 拒绝", "callback_data": f"rep_reject@{target}"},
        ]]}

        send(chat_id,
             f"📢 <b>公群担保报备</b>\n"
             f"发起人：@{ADMIN_USER if ADMIN_ID else '管理员'}\n"
             f"对象：<a href='https://t.me/{target[1:]}'>{target}</a>\n\n"
             f"{target} 请核对信息后点击下方按钮确认。",
             markup=markup, reply_to=msg_id)
        return "ok", 200

    # ---- 指令 / 菜单 ----
    if text == "/start":
        send(chat_id,
             "👋 <b>皇冠担保报备机器人</b>\n\n"
             "▸ 点菜单「公群报备」或发 /report 发起\n"
             "▸ 仅管理员可发起\n"
             "▸ 本群查询 /status　我的报备 /my", reply_to=msg_id)

    elif text in ("/verify", "/status"):
        send(chat_id, "✅ 服务正常 · Webhook 已连通", reply_to=msg_id)

    elif text in ("/report", "公群报备"):
        if not is_admin(user):
            send(chat_id, "⚠️ 只有管理员能发起报备，你没权限哦。", reply_to=msg_id)
        else:
            PENDING[str(user.get("id"))] = {"chat_id": chat_id}
            send(chat_id,
                 "📝 请直接回复这一条，输入<b>对方的 @用户名</b>（例如 <code>@xiaoming_88</code>）：",
                 reply_to=msg_id)

    elif text in ("/query", "本群查询"):
        if not is_admin(user):
            send(chat_id, "⚠️ 仅管理员", reply_to=msg_id); return "ok", 200
        n = sum(1 for k in REPORTS if k.startswith(f"report:{chat_id}:"))
        send(chat_id, f"📊 本群已处理报备：<b>{n}</b> 单", reply_to=msg_id)

    elif text in ("/my", "我的报备"):
        n = sum(1 for v in REPORTS.values() if v.get("target", "").lower()
                in [f"@{user.get('username')}"] if user.get("username"))
        send(chat_id, f"📁 涉及你的报备记录：<b>{n}</b> 单", reply_to=msg_id)

    # 其他闲聊一律静默，不报错
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
