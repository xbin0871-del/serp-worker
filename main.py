import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN", "9195362168:AAFE1zCNmbRqUu93850Re3urZd8ItHgYKRA")
WEBHOOK_URL = "https://serp-worker.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 纯同步处理，零异步坑
@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=["verify"])
def verify(msg):
    bot.send_message(msg.chat.id, "✅ 跑通了！")

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    # 启动时设置 Webhook
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
