import re
import requests
from flask import Flask, request

# ================= 配置 =================
# ⚠️ 强烈建议：旧 Token 已暴露，请去 @BotFather /revoke 换新后填这里或设环境变量
TOKEN = "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA" 
ADMIN_ID = 8385371786
ADMIN_USER = "xbin0871"

REPORTS = {}
PENDING = {}
USERNAME_RE = re.compile(r"^@[a-zA-Z0-9_]+")

TG = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)

# ================= 工具函数 =================
def send(chat_id, text, reply_markup=None):
    """纯发消息函数，不再混入回调判断"""
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

# ================= Webhook 路由 =================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    u = request.json
    if not u:
        return "ok"

    # 1. 处理普通消息指令（/verify, /report 等）
    if "message" in u:
        msg = u["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"].get("id")
        username = msg["from"].get("username", "")
        text = msg.get("text", "").strip()

        if text == "/start":
            send(chat_id, "皇冠担保报备机器人已就绪\n/verify 验证服务\n/report 提交报备")
        
        elif text == "/verify":
            send(chat_id, "✅ 服务正常，Webhook 已跑通")
        
        elif text == "/report":
            if user_id == ADMIN_ID or username == ADMIN_USER:
                send(chat_id, "📝 管理员报备：请发送 @用户名 金额")
            else:
                send(chat_id, "⚠️ 仅管理员可提交报备")
        
        # 简单演示：匹配 @用户名 进入待处理
        if USERNAME_RE.match(text):
            PENDING[text] = chat_id
            markup = {
                "inline_keyboard": [[
                    {"text": "✅ 确认收到", "callback_data": f"confirm_{text}"},
                    {"text": "❌ 拒绝", "callback_data": f"reject_{text}"}
                ]]
            }
            send(chat_id, f"收到报备：{text}\n请管理员确认", reply_markup=markup)

    # 2. 处理回调按钮（精准防御 KeyError，对应你原第29行报错）
    if "callback_query" in u:
        q = u.get("callback_query", {})
        q_id = q.get("id")  # 用 .get 替代 q["id"]，彻底避免 KeyError
        if q_id:
            answer_cb(q_id)
            data = q.get("data", "")
            chat_id = q.get("message", {}).get("chat", {}).get("id")
            if "confirm" in data:
                send(chat_id, f"✅ 报备已确认：{data}")
            elif "reject" in data:
                send(chat_id, f"❌ 报备已拒绝：{data}")

    return "ok"

# 根路径唤醒（解决 Render 冷启动）
@app.route("/")
def root():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
