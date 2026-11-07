import os
import asyncio
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA"

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 机器人已跑通！")

application.add_handler(CommandHandler("verify", verify))

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
    return Response("ok", status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
