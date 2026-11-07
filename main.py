import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 建议跑通后换成 Render 环境变量，目前先用你现有的
TOKEN = os.environ.get("BOT_TOKEN", "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# /verify 逻辑
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 跑通了！")

application.add_handler(CommandHandler("verify", verify))

# v20 官方推荐写法：用 async with 自动处理 initialize/process/shutdown，无 before_request 依赖
@app.post("/")
async def webhook():
    if request.headers.get("Content-Type") == "application/json":
        async with application:
            update = Update.de_json(request.get_json(force=True), application.bot)
            await application.process_update(update)
        return "", 200
    return "Bad Request", 400

@app.get("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    # Render 会注入 PORT 环境变量，本地默认 10000
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
