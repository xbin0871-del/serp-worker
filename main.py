import os
from flask import Flask, request, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TG_TOKEN")
PORT = int(os.getenv("PORT", 10000))

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("✅ 确认", callback_data="confirm"),
            InlineKeyboardButton("❓ 有疑问", callback_data="question"),
            InlineKeyboardButton("❌ 驳回", callback_data="reject"),
        ]
    ]
    text = (
        "📋 新报备待确认\n"
        "单号:HB20261107-0307\n"
        "组别:公群H组 1111\n"
        "方向:供押 11111111U\n"
        "对手:HX支付集团(供方老板)\n"
        "时间:2026-11-07 03:07\n\n"
        "请下方操作 👇"
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    mapping = {"confirm": "已确认 ✅", "question": "已标记有疑问 ❓", "reject": "已驳回 ❌"}
    await q.edit_message_text(mapping.get(q.data, "已处理"))

application.add_handler(CommandHandler("verify", verify))
application.add_handler(CallbackQueryHandler(on_button))

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.run_async(application.process_update(update))
        return Response("ok", 200)
    return Response("Bot is running", 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
