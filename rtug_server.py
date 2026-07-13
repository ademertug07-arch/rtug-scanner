"""
RTUG SERVER — Consolidated Scanner + Telegram Bot + Webhook
==============================================================
Hetzner VPS'te 7/24 calismak uzere tasarlandi.
Monitor (pattern tarama) + Flask webhook (TradingView alerts) +
Telegram bildirim (sadece %70+ guven sinyalleri) tek bir surecte.

KULLANIM:
    python rtug_server.py                          # 7/24 calistir
    python rtug_server.py --once                   # Tek sefer tarama
    python rtug_server.py --interval 30            # Her 30 dk'da bir

systemd icin:
    [Service]
    ExecStart=/usr/bin/python3 /opt/rtug/rtug_server.py
    Restart=always
    User=rtug
"""

import os, sys, json, time, logging, threading
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)

from dotenv import load_dotenv
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_PORT       = int(os.getenv("WEBHOOK_PORT", "5000"))

log_dir = BASE_DIR / "logs"
log_dir.mkdir(exist_ok=True)

import logging as log_mod
log_mod.basicConfig(
    level=log_mod.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        log_mod.FileHandler(log_dir / "rtug_server.log", encoding="utf-8"),
        log_mod.StreamHandler()
    ]
)
logger = log_mod.getLogger("rtug-server")

# RTUG imports
from rtug_scanner_core import RTUGSignalEngine
from rtug_pattern_memory import PatternMemory
from rtug_pattern_monitor import (
    DataProvider, load_status, save_status, is_already_notified,
    mark_notified, signal_to_indicator_state, format_pattern_alert,
    MTFValidator, add_mtf_to_alert, AlertTracker,
    BIST_SYMBOLS, SP500_SYMBOLS, CRYPTO_SYMBOLS
)
from rtug_confidence_filter import ConfidenceFilter

# ─── Telegram ────────────────────────────────────────────

def send_telegram(message: str) -> bool:
    if not message:
        return True
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN eksik")
        return False
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID, "text": message,
            "parse_mode": "HTML", "disable_web_page_preview": True
        }, timeout=10)
        if resp.status_code == 200:
            return True
        else:
            logger.error("Telegram hata: %d %s" % (resp.status_code, resp.text[:200]))
            return False
    except Exception as e:
        logger.error("Telegram baglanti: %s" % e)
        return False

# ─── Confidence Filter Setup ────────────────────────────

gate = ConfidenceFilter()

# ─── Scanner ─────────────────────────────────────────────

def get_market_type(name):
    if "kripto" in name.lower() or "crypto" in name.lower():
        return "crypto"
    elif "bist" in name.lower():
        return "bist"
    return "us"

def scan_market(engine, memory, status, data, market_name,
                min_sim=0.70, mtf_min=0.40, alert_tracker=None):
    """Tek piyasayi tara, high-confidence sinyalleri Telegram'a gonder."""
    mtf_val = MTFValidator()
    market_t = get_market_type(market_name)
    new_matches = []

    for symbol, (close, volume) in data.items():
        try:
            signal = engine.analyze(close, volume)
            if not signal or not signal.breakout_type:
                continue

            state = signal_to_indicator_state(signal, symbol)
            match = memory.find_best_match(state, min_similarity=min_sim)
            if not match or not match.is_match:
                continue

            # MTF
            mtf_conf = 0.5
            mtf_line = ""
            try:
                mtf_r = mtf_val.validate(symbol, signal, market_t)
                mtf_conf = mtf_r.confidence
                mtf_line = add_mtf_to_alert(symbol, signal, market_t, mtf_val)
            except:
                pass

            if mtf_conf < mtf_min:
                continue

            # Confidence Gate (sadece %70+)
            vol_ratio = float(np.mean(volume[-5:]) / (np.mean(volume[-10:-5]) + 1e-9))
            g = gate.evaluate(symbol, match.pattern.name, match.similarity, mtf_conf, vol_ratio)
            if not g.passed:
                continue

            # Spam onleme (24h)
            if is_already_notified(status, symbol, match.pattern.name):
                continue

            new_matches.append((symbol, match, signal, mtf_conf, mtf_line, g))
            mark_notified(status, symbol, match.pattern.name, match.similarity, signal.price)
            memory.record_match(match.pattern.name, success=True)

            if alert_tracker:
                alert_tracker.track_alert(symbol, signal.price, match.pattern.name,
                    match.similarity, market_t, signal.breakout_type, mtf_conf)

            logger.info("SINYAL: %s -> %s (%%%d gate:%%%d)" % (
                symbol, match.pattern.name, match.similarity*100, g.final_score*100))

        except:
            continue

    mtf_val.clear_cache()

    if new_matches:
        lines = [
            "<b>RTUG PATTERN ALERT</b>",
            "Zaman: %s" % datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Kaynak: %s" % market_name,
            "Eslesme: %d sembol" % len(new_matches),
            "-" * 20,
        ]
        for item in new_matches[:10]:
            symbol, match, signal, mtf_conf, mtf_line, g = item
            s = match.matched_state
            d = ("D1:%s D2:%s D6:%s" % (
                "+" if s.div1_dir>0 else "-" if s.div1_dir<0 else "0",
                "+" if s.div2_dir>0 else "-" if s.div2_dir<0 else "0",
                "+" if s.div6_dir>0 else "-" if s.div6_dir<0 else "0"))
            lines.append("\n%s | %%%d eslesme\n   %s\n   Gate: %%%d | MTF: %%%d" % (
                symbol, match.similarity*100, d, g.final_score*100, mtf_conf*100))
        if len(new_matches) > 10:
            lines.append("\n... ve %d sembol daha" % (len(new_matches) - 10))
        lines.append("\n" + "-" * 20)
        lines.append("RTUG v2 (High-Confidence Gate: %70+)")

        msg = "\n".join(lines)
        send_telegram(msg)
        logger.info("%d yuksek guven sinyali gonderildi!" % len(new_matches))

    return new_matches

def run_all_scans(engine, memory, status, interval_min=15,
                  min_sim=0.70, mtf_min=0.40, alert_tracker=None):
    """Tum piyasalari tara."""
    total = 0
    if BIST_SYMBOLS:
        try:
            data = DataProvider.from_yahoo(BIST_SYMBOLS)
            total += len(scan_market(engine, memory, status, data, "BIST 100",
                                     min_sim, mtf_min, alert_tracker))
        except Exception as e:
            logger.error("BIST: %s" % e)
    if SP500_SYMBOLS:
        try:
            data = DataProvider.from_yahoo(SP500_SYMBOLS)
            total += len(scan_market(engine, memory, status, data, "US Stocks",
                                     min_sim, mtf_min, alert_tracker))
        except Exception as e:
            logger.error("US: %s" % e)
    if CRYPTO_SYMBOLS:
        try:
            data = DataProvider.from_ccxt(CRYPTO_SYMBOLS)
            total += len(scan_market(engine, memory, status, data, "Crypto",
                                     min_sim, mtf_min, alert_tracker))
        except Exception as e:
            logger.error("Crypto: %s" % e)
    status["last_scan"] = datetime.now().isoformat()
    save_status(status)

    if alert_tracker:
        val, tp = alert_tracker.validate_pending()
        if val > 0:
            logger.info("Alert validation: %d TP / %d total" % (tp, val))

    return total

# ─── Monitor Thread ───────────────────────────────────────

def monitor_loop(interval_min=15, min_sim=0.70, mtf_min=0.40):
    """Sonsuz dongu: pattern tarama + Telegram gonderimi."""
    engine = RTUGSignalEngine()
    memory = PatternMemory()
    status = load_status()
    tracker = AlertTracker()

    pattern_count = len(memory.patterns)
    if pattern_count == 0:
        logger.warning("Pattern memory bos! Once egitim yapin.")
        send_telegram("<b>RTUG SERVER</b>\nPattern memory bos! Egitim gerekli.")
        return

    goldens = memory.get_golden_patterns()
    send_telegram(
        "<b>RTUG SERVER BASLADI</b>\n"
        "7/24 yuksek guven sinyal taramasi aktif.\n"
        "Pattern: %d | Golden: %d\n"
        "BIST: %d | US: %d | Crypto: %d\n"
        "Confidence Gate: %%70+ | MTF: %%%.0f+\n"
        "Interval: %d dk" % (
            pattern_count, len(goldens),
            len(BIST_SYMBOLS), len(SP500_SYMBOLS), len(CRYPTO_SYMBOLS),
            mtf_min*100, interval_min
        )
    )

    # Ilk tarama
    run_all_scans(engine, memory, status, interval_min, min_sim, mtf_min, tracker)

    while True:
        try:
            next_t = datetime.now() + timedelta(minutes=interval_min)
            logger.info("Sonraki tarama: %s" % next_t.strftime("%H:%M"))
            time.sleep(interval_min * 60)
            logger.info("TARAMA: %s" % datetime.now().strftime("%d.%m.%Y %H:%M"))
            run_all_scans(engine, memory, status, interval_min, min_sim, mtf_min, tracker)
            logger.info("BITTI: %s" % datetime.now().strftime("%d.%m.%Y %H:%M"))
        except KeyboardInterrupt:
            send_telegram("<b>RTUG SERVER DURDURULDU</b>")
            break
        except Exception as e:
            logger.error("Dongu hatasi: %s, 5sn sonra..." % e)
            time.sleep(5)

# ─── Flask Webhook ──────────────────────────────────────

def start_webhook():
    """Flask webhook sunucusu (TradingView alert alici)."""
    from flask import Flask, request, jsonify
    import requests

    app = Flask(__name__)
    bot_token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID

    @app.route("/webhook", methods=["POST"])
    def webhook():
        try:
            data = request.get_json(force=True, silent=True) or {"raw": request.get_data(as_text=True)}
            tv_msg = json.dumps(data, indent=2)[:300]
            logger.info("TV webhook: %s" % tv_msg)

            ticker = data.get("ticker", data.get("symbol", "N/A"))
            price = data.get("close", data.get("price", "N/A"))
            msg = (
                "<b>TV BREAKOUT ALERT</b>\n"
                "Sembol: %s\nFiyat: %s\nZaman: %s" % (
                    ticker, price, datetime.now().strftime("%H:%M"))
            )

            if bot_token and chat_id:
                requests.post("https://api.telegram.org/bot%s/sendMessage" % bot_token,
                    json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}, timeout=10)

            return jsonify({"status": "ok"}), 200
        except Exception as e:
            logger.error("Webhook: %s" % e)
            return jsonify({"status": "error"}), 500

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "service": "RTUG SERVER",
            "confidence_gate": "%70+",
            "mtf_threshold": "%%%.0f+" % (float(os.getenv("MTF_MIN", "40")))
        })

    logger.info("Webhook basliyor: http://0.0.0.0:%d/webhook" % WEBHOOK_PORT)
    app.run(host="0.0.0.0", port=WEBHOOK_PORT, threaded=True)

# ─── Main ─────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RTUG SERVER — 7/24 Scanner + Webhook")
    parser.add_argument("--once", action="store_true", help="Tek sefer tarama")
    parser.add_argument("--interval", type=int, default=15, help="Tarama araligi (dk)")
    parser.add_argument("--threshold", type=float, default=0.70, help="Pattern eslesme threshold")
    parser.add_argument("--mtf-threshold", type=float, default=0.40, help="Min MTF confidence")
    parser.add_argument("--no-webhook", action="store_true", help="Webhook sunucusunu baslatma")

    args = parser.parse_args()

    print("""
╔════════════════════════════════════════════════════╗
║   RTUG SERVER — High-Confidence Pattern Scanner   ║
║   Confidence Gate: %%70+ | MTF: %%%.0f+              ║
║   Interval: %d dk                                 ║
╚════════════════════════════════════════════════════╝
    """ % (args.mtf_threshold*100, args.interval))

    if args.once:
        engine = RTUGSignalEngine()
        memory = PatternMemory()
        status = load_status()
        tracker = AlertTracker()
        found = run_all_scans(engine, memory, status, args.interval,
                              args.threshold, args.mtf_threshold, tracker)
        print("Tarama tamam. %d sinyal." % found)
    else:
        # Monitor thread
        t = threading.Thread(target=monitor_loop, args=(
            args.interval, args.threshold, args.mtf_threshold), daemon=True)
        t.start()

        # Webhook (TradingView alerts)
        if not args.no_webhook:
            start_webhook()
        else:
            # Monitor thread'ini canli tut
            try:
                while t.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
