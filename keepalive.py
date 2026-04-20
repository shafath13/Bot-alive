from flask import Flask, jsonify, render_template_string
from datetime import datetime
import threading
import requests
import os

app = Flask(__name__)

start_time = datetime.utcnow()

# ── HTML status page (served at "/") ─────────────────────────────────────────
PAGE = open(os.path.join(os.path.dirname(__file__), "index.html")).read()

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/ping")
def ping():
    uptime_seconds = int((datetime.utcnow() - start_time).total_seconds())
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return jsonify({
        "status": "alive",
        "uptime": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

# ── Self-ping loop (keeps the Replit/Render dyno awake) ─────────────────────
def self_ping():
    """
    Pings this server's /ping endpoint every 4 minutes.
    Replace SELF_URL with your deployed URL, e.g.:
        https://my-bot-keepalive.onrender.com
    or just leave the env-var approach below.
    """
    import time
    url = os.getenv("SELF_URL", "http://localhost:5000/ping")
    while True:
        time.sleep(240)          # 4 minutes
        try:
            r = requests.get(url, timeout=10)
            print(f"[keep-alive] self-ping → {r.status_code}")
        except Exception as e:
            print(f"[keep-alive] self-ping failed: {e}")

def run():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    """Call this from your bot's main file instead of running this script directly."""
    t = threading.Thread(target=run, daemon=True)
    t.start()
    ping_t = threading.Thread(target=self_ping, daemon=True)
    ping_t.start()

# ── Standalone entry-point ───────────────────────────────────────────────────
if __name__ == "__main__":
    ping_t = threading.Thread(target=self_ping, daemon=True)
    ping_t.start()
    run()