import os, requests

TOKEN = os.getenv("TG_TOKEN")
GROUP_ID = os.getenv("TG_GROUP", "-1004466833723")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {"chat_id": GROUP_ID, "text": "报备文本测试"}
res = requests.post(url, data=data)
print("状态:", res.status_code)
print("返回:", res.text)
