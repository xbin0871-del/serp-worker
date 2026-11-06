import os, requests

TOKEN = os.getenv("TG_TOKEN")
# 优先读密钥，如果没读到，强制用这个真实ID兜底
GROUP_ID = os.getenv("TG_GROUP", "-1004466833723")

print("准备发到:", GROUP_ID) # 日志里必须看到 -1004466833723

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {"chat_id": GROUP_ID, "text": "报备文本测试"}
res = requests.post(url, data=data)

print("状态:", res.status_code)
print("返回:", res.text)
