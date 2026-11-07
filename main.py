import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA")

app = Flask(__name__)
# 强制使用同步 HTTP 客户端，彻底避开所有事件循环坑
application = Application.builder().token(TOKEN).concurrent_updates(True).build()

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 跑通了！")

application.add_handler(CommandHandler("verify", verify))

# 纯同步路由
@app.route("/", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        # 使用 PTB 官方同步调度，无 asyncio.run
        application.update_queue.put_nowait(update)
        return "ok", 200
    except Exception as e:
        return str(e), 500

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

if __name__ == "__main__":
    # 预初始化
    application.initialize()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
