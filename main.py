import os
import re
import telebot
from datetime import datetime, timezone, timedelta
from flask import Flask, request, abort

# ================= 基础配置 =================
TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://serp-worker.onrender.com")
GUARANTOR = "皇冠担保"
ADMIN_IDS = [8385371786]  # ✅ 已填入你的ID，别再改

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# 内存订单表（免费版重启会丢，先跑着）
ORDERS = {}

# ================= 工具 =================
def _name(u):
    return f"@{u.username}" if u.username else f"{u.first_name or '用户'}({u.id})"

def tz8():
    return timezone(timedelta(hours=8))

def now_str():
    return datetime.now(tz8()).strftime("%Y-%m-%d %H:%M:%S")

# ================= /verify（保留，跑通自检用） =================
@bot.message_handler(commands=["verify"])
def verify(msg):
    bot.reply_to(msg, f"✅ 跑通了！你的ID: {msg.from_user.id}")

# ================= /baobei 报备 =================
class IsAdmin(telebot.custom_filters.SimpleCustomFilter):  # ✅ 已修正笔误
    key = "is_chat_admin"
    @staticmethod
    def check(msg):
        if msg.chat.type not in ("group", "supergroup"):
            return False
        try:
            st = bot.get_chat_member(msg.chat.id, msg.from_user.id).status
            return st in ("creator", "administrator")
        except Exception:
            return False

bot.add_custom_filter(IsAdmin())

@bot.message_handler(commands=["baobei"], is_chat_admin=True)
def baobei(msg):
    target = msg.reply_to_message.from_user if msg.reply_to_message else None
    if not target:
        return bot.reply_to(msg, "⚠️ 请先【回复】要报备的那条消息，再输入 /baobei 金额")

    arg = (msg.text or "").split()
    amount = arg[1] if len(arg) > 1 else ""
    if amount and not re.fullmatch(r"[0-9,]+(?:\.[0-9]+)?", amount):
        return bot.reply_to(msg, "⚠️ 金额格式不对，例：/baobei 2325 或 /baobei 1,200.50")

    order_id = f"TD{int(datetime.now().timestamp())}"
    text = (
        f"📋 【交易报备】\n"
        f"🆔 订单号: {order_id}\n"
        f"👤 交易对象: {_name(target)}\n"
        f"💰 金额: {amount or '（待填）'} U\n"
        f"🛡️ 担保方式: {GUARANTOR}\n"
        f"👮 操作人: {_name(msg.from_user)}\n"
        f"🕒 报备时间: {now_str()}\n"
        f"⏳ 状态: 待双方确认"
    )
    ORDERS[order_id] = {
        "amount": amount, "target": target.id,
        "status": "pending", "chat_id": msg.chat.id,
    }

    mk = telebot.types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        telebot.types.InlineKeyboardButton("✅ 双方确认完成", callback_data=f"done_{order_id}"),
        telebot.types.InlineKeyboardButton("❌ 双方确认取消", callback_data=f"cancel_{order_id}"),
    )
    mk.add(telebot.types.InlineKeyboardButton("🛡️ 担保取消订单", callback_data=f"gcancel_{order_id}"))

    bot.send_message(msg.chat.id, text,
                     reply_markup=mk,
                     reply_to_message_id=msg.reply_to_message.message_id)

@bot.message_handler(commands=["baobei"])
def baobei_deny(msg):
    if msg.chat.type in ("group", "supergroup"):
        bot.reply_to(msg, "⛔ 只有群管理员可以发起报备")

# ================= 按钮回调 =================
@bot.callback_query_handler(func=lambda c: c.data.startswith(("done_", "cancel_", "gcancel_")))
def handle_btn(call):
    try:
        action, oid = call.data.split("_", 1)
    except ValueError:
        return bot.answer_callback_query(call.id, "数据异常")

    order = ORDERS.get(oid)
    if not order:
        return bot.answer_callback_query(call.id, "订单已失效或重启丢失，请重新报备")

    uid = call.from_user.id
    try:
        is_admin = bot.get_chat_member(call.message.chat.id, uid).status in ("creator", "administrator")
    except Exception:
        is_admin = False

    # 只允许：交易对象本人 / 群管理员 / 配置的超级管理员
    if uid != order["target"] and uid not in ADMIN_IDS and not is_admin:
        return bot.answer_callback_query(call.id, "⛔ 你没有权限操作这笔订单")

    old = call.message.text
    t = f"\n🕒 处理时间: {now_str()}"

    if action == "done":
        order["status"] = "completed"
        new = old.replace("⏳ 状态: 待双方确认", "✅ 状态: 双方已确认完成") + t
        bot.answer_callback_query(call.id, "已确认完成 ✅")
    elif action == "cancel":
        order["status"] = "cancelled"
        new = old.replace("⏳ 状态: 待双方确认", "❌ 状态: 双方确认取消") + t
        bot.answer_callback_query(call.id, "已取消 ❌")
    elif action == "gcancel":
        order["status"] = "g_cancelled"
        new = old.replace("⏳ 状态: 待双方确认", "🛡️ 状态: 担保方取消订单") + t
        bot.answer_callback_query(call.id, "担保方已取消 🛡️")
    else:
        return

    try:
        bot.edit_message_text(new, call.message.chat.id, call.message.message_id, reply_markup=None)
    except Exception:
        bot.answer_callback_query(call.id, "状态已更新（消息未能刷新，属正常）")

# ================= Webhook =================
@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        if request.headers.get("content-type") != "application/json":
            abort(403)
        bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode("utf-8"))])
        return "OK"
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
