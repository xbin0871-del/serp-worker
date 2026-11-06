import os, requests
from flask import Flask, request

TOKEN    = os.getenv("TG_TOKEN")
GROUP_ID = os.getenv("TG_GROUP", "-1004466833723")
PORT     = int(os.getenv("PORT", 9000))
app = Flask(__name__)

ANSWER = {
    "ok":     "✅ 已确认，客服跟进中",
    "check":  "❓ 已标记疑问，请补充说明确",
    "reject": "❌ 已驳回，本单作废",
}

@app.get("/")
def ping():
    return "ok", 200

@app.post(f"/{TOKEN}")
def cb():
    d = request.get_json(force=True)
    q   = d.get("callback_query", {})
    act, no = (q.get("callback_data", "").split("::") + [""])[:2]
    user   = q.get("from", {}).get("first_name", "未知")
    print(f"点击: {act} | 单号: {no} | 人: {user}")

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
        json={"callback_query_id": q["id"], "text": ANSWER.get(act, "已收到")},
        timeout=5,
    )
    if act in ANSWER:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": GROUP_ID,
                  "text": f"单号 `{no}`\n处理：{ANSWER[act]}\n操作人：{user}",
                  "parse_mode": "Markdown"},
            timeout=8,
        )
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
