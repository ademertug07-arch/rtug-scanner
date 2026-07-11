"""
RTUG BREAKOUT ALERT — Telegram Bildirim Botu
==============================================
TradingView → Webhook → Telegram

KULLANIM:
1. Bu script'i bir sunucuda çalıştır (veya localhost + ngrok)
2. Telegram'da @BotFather ile bot oluştur, token al
3. .env dosyasına TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID yaz
4. TradingView'de alert → Webhook URL olarak http://SUNUCU:5000/webhook ayarla
5. Botu çalıştır: python rtug_telegram_bot.py

GEREKLİLİKLER:
pip install flask requests python-dotenv
"""

import os
import json
import logging
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

# ─── Config ───────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_PORT       = int(os.getenv("WEBHOOK_PORT", "5000"))
DEBUG_MODE         = os.getenv("DEBUG", "false").lower() == "true"

# Logging
logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rtug-bot")

app = Flask(__name__)

# ─── Telegram Gönderme ────────────────────────────────────
def send_telegram(message: str) -> bool:
    """Telegram'a mesaj gönder."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("❌ TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID eksik! .env dosyasını kontrol et.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info("✅ Telegram mesajı gönderildi.")
            return True
        else:
            logger.error(f"❌ Telegram hatası: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram bağlantı hatası: {e}")
        return False


def format_tradingview_alert(data: dict) -> str:
    """
    TradingView'den gelen webhook verisini Telegram mesajına dönüştür.
    TradingView alert message formatını otomatik algılar.
    """
    # Eğer data string olarak geldiyse parse et
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            pass

    # TradingView alerts usually have 'ticker' or come as raw text
    ticker = data.get("ticker", data.get("symbol", "N/A"))
    price  = data.get("close", data.get("price", "N/A"))
    time   = data.get("time", data.get("timestamp", "N/A"))
    message_text = data.get("message", str(data))

    # RTUG formatını tanı
    if "RTUG BREAKOUT ALERT" in message_text:
        # Zaten formatlı gelmiş, olduğu gibi gönder
        return f"<b>🔔 RTUG BREAKOUT ALERT</b>\n\n{message_text}"

    # Ham veriden zengin mesaj oluştur
    lines = [
        f"<b>🔔 RTUG BREAKOUT ALERT</b>",
        f"━━━━━━━━━━━━━━━━━",
        f"<b>Sembol:</b> {ticker}",
        f"<b>Fiyat:</b>  {price}",
    ]

    if time and time != "N/A":
        lines.append(f"<b>Zaman:</b>  {time}")

    # Ekstra alanlar varsa ekle
    for key in ["type", "direction", "strength", "divergences", "bull_count", "bear_count"]:
        val = data.get(key)
        if val is not None:
            label = key.replace("_", " ").title()
            lines.append(f"<b>{label}:</b> {val}")

    lines.append(f"\n📊 <a href='https://tr.tradingview.com/chart/WfKlLjel/'>Chartı Aç</a>")
    lines.append(f"#{ticker.replace('/', '')}")

    return "\n".join(lines)


# ─── Webhook Endpoint ─────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    """TradingView alert webhook alıcısı."""
    try:
        # Gelen veriyi al
        raw_data = request.get_data(as_text=True)

        # JSON veya text olabilir
        try:
            data = json.loads(raw_data)
        except:
            data = {"message": raw_data, "raw": True}

        logger.info(f"📩 Gelen webhook: {json.dumps(data, indent=2)[:500]}")

        # Telegram'a gönder
        message = format_tradingview_alert(data)
        send_telegram(message)

        return jsonify({"status": "ok", "sent": True}), 200

    except Exception as e:
        logger.error(f"❌ Webhook işleme hatası: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Sağlık kontrolü."""
    return jsonify({
        "status": "healthy",
        "bot": "RTUG BREAKOUT ALERT",
        "telegram_configured": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    })


# ─── Ana Çalıştırma ──────────────────────────────────────
if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("""
╔════════════════════════════════════════════════════╗
║   RTUG BREAKOUT ALERT — Telegram Bot             ║
╠════════════════════════════════════════════════════╣
║  ❌ .env dosyası eksik!                          ║
║                                                  ║
║  .env dosyası oluştur:                           ║
║  ─────────────────────                            ║
║  TELEGRAM_BOT_TOKEN=123456:ABC-DEF               ║
║  TELEGRAM_CHAT_ID=-1001234567890                 ║
║  WEBHOOK_PORT=5000                               ║
║  DEBUG=true                                      ║
║                                                  ║
║  Chat ID almak için @userinfobot kullan.         ║
╚════════════════════════════════════════════════════╝
        """)

    print(f"""
╔════════════════════════════════════════════════════╗
║   🚀 RTUG BREAKOUT ALERT — Telegram Bot          ║
║   📡 Webhook: http://0.0.0.0:{WEBHOOK_PORT}/webhook    ║
║   ❤️  Health:  http://0.0.0.0:{WEBHOOK_PORT}/health    ║
║   📋 Bot: {'✅ Configured' if TELEGRAM_BOT_TOKEN else '❌ Missing Token'}          ║
╚════════════════════════════════════════════════════╝
    """)

    app.run(host="0.0.0.0", port=WEBHOOK_PORT, debug=DEBUG_MODE)
