import requests
import os

# 读取刚刚配置的 Token
BOT_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = "-1004466833723"  # 你的群ID

# 1U 消息内容
text = "1U 测试推送 ✅"

# 三按钮配置
reply_markup = {
    "inline_keyboard": [[
        {"text": "按钮1", "callback_data": "btn1"},
        {"text": "按钮2", "callback_data": "btn2"},
        {"text": "按钮3", "callback_data": "btn3"}
    ]]
}

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID,
    "text": text,
    "reply_markup": reply_markup
}

resp = requests.post(url, json=data)
print("状态码:", resp.status_code)
print("返回:", resp.json())

if resp.status_code == 200:
    print("推送成功 ✅")
else:
    print("推送失败 ❌")
