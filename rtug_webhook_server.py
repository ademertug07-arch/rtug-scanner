"""
RTUG COLOR SURROUND — TradingView Webhook → Telegram Bridge
=============================================================
Real-time pattern bildirimleri: TradingView'de pattern oluşunca
anında Telegram'a düşer.

KULLANIM:
    # Lokal test (ngrok ile):
    python rtug_webhook_server.py
    # ngrok http 5000 → https://xxxx.ngrok.io/webhook

    # Render/Railway deploy:
    #   Start command: python rtug_webhook_server.py
    #   Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TRADINGVIEW AYARI:
    TradingView'de indicator'e sağ tık → Add alert
    Condition: "RTUG Color Surround"
    Webhook URL: https://SUNUCUNUZ/webhook
    Message: {içerik önemli değil, Pine Script JSON'u gönderir}

GEREKLİLİKLER:
    pip install flask requests python-dotenv
"""

import os, sys, json, logging
from datetime import datetime
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# ─── Config ───────────────────────────────────────────────
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_PORT       = int(os.getenv("WEBHOOK_PORT", "5000"))
DEBUG_MODE         = os.getenv("DEBUG", "false").lower() == "true"

# Logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("rtug-webhook")

app = Flask(__name__)


# ─── Pattern Bilgileri ────────────────────────────────────
PATTERN_INFO = {
    # 🎯 Color Surround
    "BULLISH_SURROUND":       ("🟣", "BOĞA SARMA",     "Mor+Mavi Kırmızıyı sardı (düşüş bitiyor)"),
    "BEARISH_SURROUND":       ("🔴", "AYI SARMA",      "Pembe+Kahve Kırmızıyı sardı (yükseliş bitiyor)"),
    "STRONG_BULLISH_SURROUND":("🟢", "GÜÇLÜ BOĞA SARMA","Tam boğa sarma (Div1+Div6, Div2+Div5'i sardı)"),
    "STRONG_BEARISH_SURROUND":("🟠", "GÜÇLÜ AYI SARMA", "Tam ayı sarma (Div1+Div6, Div2+Div5'i sardı)"),
    "DEEP_BULLISH_SURROUND":  ("🔮", "DERİN BOĞA",     "4/5 divergence bullish"),
    "DEEP_BEARISH_SURROUND":  ("🔮", "DERİN AYI",      "4/5 divergence bearish"),
    "OBV_CONFIRMED_BULLISH_SURROUND": ("✅", "OBV ONAYLI BOĞA", "Surround + OBV onaylı"),
    "OBV_CONFIRMED_BEARISH_SURROUND": ("❌", "OBV ONAYLI AYI",  "Surround + OBV onaylı"),

    # 🔵 Reverse Circle
    "REVERSE_CIRCLE_BULLISH": ("🔵", "TERS DAİRE BOĞA", "Reverse daireler bullish (yakında yükseliş)"),
    "REVERSE_CIRCLE_BEARISH": ("🟠", "TERS DAİRE AYI",  "Reverse daireler bearish (yakında düşüş)"),

    # 🔥 Triple
    "TRIPLE_BULLISH":         ("🔵", "ÜÇLÜ BOĞA",   "Div1+Div2+Div6 hepsi UP: Mor+Kırmızı+Mavi"),
    "TRIPLE_BEARISH":         ("🟠", "ÜÇLÜ AYI",    "Div1+Div2+Div6 hepsi DN: Pembe+Turuncu+Kahve"),

    # ⚡ Box Breakout
    "BOX_BREAKOUT_BULL":      ("⚡", "KUTU PATLAMASI BOĞA", "Konsolidasyon kutusu yukarı kırıldı"),
    "BOX_BREAKOUT_BEAR":      ("⚡", "KUTU PATLAMASI AYI",  "Konsolidasyon kutusu aşağı kırıldı"),

    # 🔄 Div2 Turn
    "DIV2_TURNING_BULLISH":   ("🔄", "DIV2 BOĞA DÖNÜŞ", "Turuncu→Kırmızı dönüş başladı"),
    "DIV2_TURNING_BEARISH":   ("🔄", "DIV2 AYI DÖNÜŞ",  "Kırmızı→Turuncu dönüş başladı"),
}

DIV_EMOJIS = {
    "MOR_UP": "🟣", "PEMBE_DN": "🩷",
    "KIRMIZI_UP": "🔴", "TURUNCU_DN": "🟠",
    "MAVI_UP": "🔵", "KAHVE_DN": "🟤",
    "PEMBE_UP": "💗", "MOR_DN": "💜",
    "YESIL_UP": "🟢", "SARI_DN": "🟡",
}


# ─── Telegram Gönderme ────────────────────────────────────

def send_telegram(message: str) -> bool:
    """Telegram'a mesaj gönder."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("❌ TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID eksik!")
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
            logger.error(f"❌ Telegram hatası: {resp.status_code} - {resp.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram bağlantı hatası: {e}")
        return False


# ─── RTUG JSON Parse ve Formatlama ────────────────────────

def div_direction_str(direction: str) -> str:
    """Div yönünü okuyabilir hale getir."""
    emoji = DIV_EMOJIS.get(direction, "")
    label = direction.replace("_", " ").title()
    return f"{emoji} {label}" if emoji else label


def format_rtug_alert(data: dict) -> str:
    """
    Pine Script'ten gelen RTUG Color Surround JSON'u
    zengin Telegram mesajına dönüştürür.
    """
    pattern_type = data.get("type", "UNKNOWN")
    ticker = data.get("ticker", "N/A")
    exchange = data.get("exchange", "")
    price = data.get("close", "?")
    strength = data.get("strength", "0")

    # Pattern bilgisi
    p_emoji, p_name, p_desc = PATTERN_INFO.get(pattern_type, ("❓", pattern_type, ""))

    # Div yönleri
    div_lines = []
    for d in ["d1", "d2", "d3", "d5", "d6"]:
        val = data.get(d)
        dir_key = data.get(f"{d}d", "")
        if val is not None:
            val_str = f"{float(val):+.2f}" if val else val
            dir_str = div_direction_str(dir_key) if dir_key else ""
            names = {"d1": "Div1", "d2": "Div2", "d3": "Div3", "d5": "Div5", "d6": "Div6"}
            colors = {"d1": "#aa00ff" if float(val) > 0 else "#ff00aa",
                      "d2": "#ff4444" if float(val) > 0 else "#ff8800",
                      "d3": "#00ff88" if float(val) > 0 else "#bbff00",
                      "d5": "#ff00aa" if float(val) > 0 else "#aa00ff",
                      "d6": "#00cccc" if float(val) > 0 else "#cc6600"}
            clr = colors.get(d, "#888888")
            div_lines.append(f"<b>{names[d]}:</b> <code>{val_str}</code> {dir_str}")

    # Bull count
    bull_count = data.get("bull_count", "?")
    obv = data.get("obv", "")
    obv_str = f" | OBV: {obv}" if obv else ""

    # Satırları oluştur
    lines = [
        f"<b>{p_emoji} RTUG COLOR SURROUND</b>",
        f"━━━━━━━━━━━━━━━━━",
        f"<b>Sembol:</b> {ticker} ({exchange})" if exchange else f"<b>Sembol:</b> {ticker}",
        f"<b>Pattern:</b> {p_name}",
        f"<b>Fiyat:</b>  <code>{price}</code>",
        f"<b>Güç:</b>    {'⭐' * int(strength) if strength.isdigit() else strength}/5",
        f"<b>Durum:</b>  {bull_count}/5 Bullish{obv_str}",
        f"<b>Açıklama:</b> {p_desc}" if p_desc else "",
        f"",
        f"<b>Divergence Durumu:</b>",
    ]

    # Div satırlarını ekle
    lines.extend(div_lines[:6])

    # TradingView chart linki
    sym_clean = ticker.replace("/", "")
    chart_url = f"https://www.tradingview.com/chart/?symbol={ticker}"
    lines.extend([
        f"",
        f"📊 <a href='{chart_url}'>Chartı Aç</a>",
        f"⏱ {datetime.now().strftime('%H:%M:%S')}",
    ])

    return "\n".join(lines)


# ─── Endpoints ─────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    """TradingView alert webhook alıcısı (RTUG Color Surround + legacy)."""
    try:
        raw_data = request.get_data(as_text=True)
        logger.info(f"📩 Webhook geldi ({len(raw_data)} bytes)")

        # JSON parse
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            data = {"message": raw_data[:500], "raw": True}
            message = f"<b>🔔 RTUG ALERT (raw)</b>\n<code>{raw_data[:500]}</code>"
            send_telegram(message)
            return jsonify({"status": "ok", "parsed": False}), 200

        # RTUG Color Surround formatını tanı
        pattern_type = data.get("type", "")
        if pattern_type and pattern_type in PATTERN_INFO:
            message = format_rtug_alert(data)
        else:
            # Legacy format (rtug_telegram_bot.py mantığı)
            ticker = data.get("ticker", data.get("symbol", "N/A"))
            price = data.get("close", data.get("price", "?"))
            msg_text = data.get("message", str(data)[:200])
            
            if "BREAKOUT" in msg_text:
                message = f"<b>🔔 RTUG BREAKOUT ALERT</b>\n\n{msg_text}"
            else:
                message = (
                    f"<b>🔔 RTUG ALERT</b>\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"<b>Sembol:</b> {ticker}\n"
                    f"<b>Fiyat:</b>  {price}\n"
                    f"<b>Mesaj:</b>  {msg_text}"
                )

        send_telegram(message)
        return jsonify({"status": "ok", "sent": True}), 200

    except Exception as e:
        logger.error(f"❌ Webhook hatası: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Sağlık kontrolü."""
    return jsonify({
        "status": "healthy",
        "bot": "RTUG Color Surround Webhook",
        "version": "2.0",
        "telegram_configured": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        "patterns": list(PATTERN_INFO.keys())
    })


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "RTUG Color Surround Webhook",
        "endpoints": {
            "/webhook": "POST - TradingView alert alıcısı",
            "/health": "GET - Sağlık kontrolü"
        },
        "patterns": len(PATTERN_INFO)
    })


# ─── Ana Çalıştırma ──────────────────────────────────────

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        print("""
╔══════════════════════════════════════════════════════════╗
║   RTUG COLOR SURROUND — Webhook → Telegram Bridge      ║
╠══════════════════════════════════════════════════════════╣
║  ❌ .env dosyası eksik!                                ║
║                                                        ║
║  .env dosyası oluştur:                                 ║
║  ─────────────────────                                  ║
║  TELEGRAM_BOT_TOKEN=123456:ABC-DEF                      ║
║  TELEGRAM_CHAT_ID=6988108865                            ║
║  WEBHOOK_PORT=5000                                      ║
║  DEBUG=true                                             ║
╚══════════════════════════════════════════════════════════╝
        """)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║  🚀 RTUG COLOR SURROUND — WEBHOOK SERVER               ║
╠══════════════════════════════════════════════════════════╣
║  📡 Webhook:  http://0.0.0.0:{WEBHOOK_PORT}/webhook         ║
║  ❤️  Health:   http://0.0.0.0:{WEBHOOK_PORT}/health         ║
║  📋 Bot:      {'✅ Configured' if TELEGRAM_BOT_TOKEN else '❌ Missing Token'}     ║
║  📊 Patterns: {len(PATTERN_INFO)} adet                      ║
╚══════════════════════════════════════════════════════════╝
    """)

    if TELEGRAM_BOT_TOKEN:
        # Test mesajı
        send_telegram(
            f"<b>🚀 RTUG WEBHOOK SERVER BAŞLADI</b>\n"
            f"📡 Webhook hazır — TradingView alertleri bekleniyor...\n"
            f"📊 {len(PATTERN_INFO)} pattern tipi destekleniyor\n"
            f"⏱ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

    app.run(host="0.0.0.0", port=WEBHOOK_PORT, debug=DEBUG_MODE)
