import os, requests
from flask import Flask, request, jsonify

TOKEN = os.environ.get("TOKEN")
TG = "https://api.telegram.org/bot" + TOKEN
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 10000))

@app.route("/", methods=["GET"])
def health():
    return "OK"

@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    u = request.get_json(silent=True) or {}
    m = u.get("message") or {}
    c = m.get("chat", {})
    cid = c.get("id")
    txt = (m.get("text") or "").strip()
    if cid and txt == "/verify":
        requests.post(TG + "/sendMessage", json={"chat_id": cid, "text": "✅ 活了"})
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
