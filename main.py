import os, requests

TOKEN = os.getenv("TG_TOKEN")
GROUP_ID = os.getenv("TG_GROUP")

# 如果TG_GROUP没设，再用你之前的ID（换成你真实的，带-100）
if not GROUP_ID:
    GROUP_ID = "-100你的真实群ID"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {"chat_id": GROUP_ID, "text": "报备文本测试"}
res = requests.post(url, data=data)
print("状态:", res.status_code)
print("返回:", res.text)
