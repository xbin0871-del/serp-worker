import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 跑通了！")

application.add_handler(CommandHandler("verify", verify))

# v20 必须用这个初始化，不能用 application.run_async / application.loop
@app.before_first_request
def init_app():
    asyncio.run(application.initialize())

@app.post("/")
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

@app.get("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
