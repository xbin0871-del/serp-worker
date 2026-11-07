import os, asyncio
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)
application = Application.builder().token("9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA").build()

async def verify(update, context):
    await update.message.reply_text("✅ 跑通了")

application.add_handler(CommandHandler("verify", verify))

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
    return Response("ok", status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
