import os
import requests
import json
import datetime

TOKEN = os.getenv("TG_TOKEN")
GROUP_ID = os.getenv("TG_GROUP", "-1004466833723")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# 1. 调用 SerpApi 获取真实数据（示例：搜索 Google）
search_query = "USDT 承兑 报备"
params = {
    "q": search_query,
    "api_key": SERPAPI_KEY,
    "engine": "google"
}
try:
    resp = requests.get("https://serpapi.com/search", params=params)
    data = resp.json()
    # 取第一个自然结果作为演示（实际按你的业务解析）
    top_result = data.get("organic_results", [{}])[0]
    snippet = top_result.get("snippet", "无摘要")[:50]
except Exception as e:
    snippet = f"数据获取失败: {e}"

# 2. 组装业务卡片
order = {
    "group":   "公群H组",
    "side":    "供押",
    "amount":  "1111111U",
    "counter": "HX支付集团",
    "no":      f"HB{datetime.datetime.now().strftime('%Y%m%d%H%M')}",
    "time":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "data":    snippet
}

lines = [
    "📋 **新报备待确认** (含SerpApi数据)",
    f"单号：`{order['no']}`",
    f"组别：{order['group']}",
    f"方向：{order['side']}  {order['amount']}",
    f"对手：{order['counter']}",
    f"搜索参考：{order['data']}",
    f"时间：{order['time']}",
    "",
    "请下方操作 👇",
]
text = "\n".join(lines)

keyboard = {
    "inline_keyboard": [
        [
            {"text": "✅ 确认",  "callback_data": f"ok::{order['no']}"},
            {"text": "❓ 有疑问", "callback_data": f"check::{order['no']}"},
            {"text": "❌ 驳回",  "callback_data": f"reject::{order['no']}"},
        ]
    ]
}

# 3. 发送 Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
res = requests.post(url, json={
    "chat_id":      GROUP_ID,
    "text":         text,
    "parse_mode":   "Markdown",
    "reply_markup": json.dumps(keyboard, ensure_ascii=False),
})

print("状态:", res.status_code, "| ok:", res.json().get("ok"))
