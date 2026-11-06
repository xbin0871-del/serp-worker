import os, requests
GROUP_ID = "-100你的真实群ID"
TOKEN = os.getenv("TG_TOKEN")
requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": GROUP_ID, "text": "报备文本测试"})
