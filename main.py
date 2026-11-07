import os, asyncio, threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 跑通了！")

application.add_handler(CommandHandler("verify", verify))

# 启动时在后台线程里跑一次 initialize，避开 before_first_request
def _init():
    asyncio.run(application.initialize())
threading.Thread(target=_init, daemon=True).start()

# 同步路由，彻底不碰 Flask 的 async 支持
@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
