import os
import requests
import json
import datetime

TOKEN = os.getenv("TG_TOKEN")
GROUP_ID = os.getenv("TG_GROUP", "-1004466833723")

# 业务数据（后续接真实表格/API）
order = {
    "group":   "公群H组 1111",
    "side":    "供押",
    "amount":  "1111111U",
    "counter": "HX支付集团（供方老板）",
    "no":      f"HB{datetime.datetime.now().strftime('%Y%m%d-%H%M')}",
    "time":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
}

lines = [
    "📋 **新报备待确认**",
    f"单号：`{order['no']}`",
    f"组别：{order['group']}",
    f"方向：{order['side']}  {order['amount']}",
    f"对手：{order['counter']}",
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

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
res = requests.post(url, json={
    "chat_id":      GROUP_ID,
    "text":         text,
    "parse_mode":   "Markdown",
    "reply_markup": json.dumps(keyboard, ensure_ascii=False),
})

print("准备发到:", GROUP_ID)
print("状态:", res.status_code, "| ok:", res.json().get("ok"))
