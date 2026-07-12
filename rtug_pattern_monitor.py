"""
RTUG PATTERN MONITOR v2 — AI Pattern Memory + 7/24 Canli Tarama + Telegram
==========================================================================
Pattern memory'deki ogrenilen pattern'leri kullanarak tum piyasalari
7/24 tarar, benzer durumlari tespit eder ve Telegram'a bildirim gonderir.

CALISMA MANTIGI:
1. Pattern memory'den egitilmis pattern'leri yukle
2. Scanner core ile tum sembolleri tara
3. Her sembolun anlik indicator state'ini pattern'lerle karsilastir
4. Eslesme bulursa (threshold >= %70) Telegram'a bildir
5. Ayni sembol+pattern kombinasyonunu 24 saatte bir bildir (spam onleme)

KULLANIM:
    python rtug_pattern_monitor.py                          # 7/24 calistir
    python rtug_pattern_monitor.py --interval 5              # Her 5 dk'da bir
    python rtug_pattern_monitor.py --once                    # Tek sefer
    python rtug_pattern_monitor.py --no-telegram             # Sadece konsol
    python rtug_pattern_monitor.py --threshold 0.80          # %80 eslesme threshold
    python rtug_pattern_monitor.py --list-patterns           # Pattern'leri listele
    python rtug_pattern_monitor.py --symbol BTC/USDT         # Tek sembol test
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

import numpy as np

# RTUG Engine
from rtug_scanner_core import RTUGSignalEngine, SignalResult

# RTUG Pattern Memory
from rtug_pattern_memory import PatternMemory, IndicatorState, MatchResult

# Logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "pattern_monitor.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("rtug-pattern-monitor")

# ─── Durum Dosyasi ───────────────────────────────────────
STATUS_FILE = Path(__file__).parent / ".pattern_monitor_status.json"

# ─── Sembol Listeleri ────────────────────────────────────
try:
    from rtug_symbols import BIST_SYMBOLS, SP500_SYMBOLS
except ImportError:
    logger.warning("rtug_symbols import edilemedi, manuel listeler kullanilacak")
    BIST_SYMBOLS = []
    SP500_SYMBOLS = []

# Kripto
try:
    from rtug_symbols import get_all_crypto_symbols as _fetch_crypto
    _crypto_list = _fetch_crypto()
    CRYPTO_SYMBOLS = _crypto_list if _crypto_list else None
except Exception:
    CRYPTO_SYMBOLS = None

if not CRYPTO_SYMBOLS:
    CRYPTO_SYMBOLS = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
        "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT",
        "MATIC/USDT", "UNI/USDT", "SHIB/USDT", "LTC/USDT", "BCH/USDT",
        "ATOM/USDT", "ETC/USDT", "XLM/USDT", "NEAR/USDT", "APT/USDT",
        "ARB/USDT", "OP/USDT", "SUI/USDT", "PEPE/USDT", "INJ/USDT",
        "TIA/USDT", "SEI/USDT", "FIL/USDT", "FTM/USDT", "ALGO/USDT",
    ]

logger.info(f"Sembol listeleri: BIST {len(BIST_SYMBOLS)}, US {len(SP500_SYMBOLS)}, Crypto {len(CRYPTO_SYMBOLS)}")


# ─── Data Provider ───────────────────────────────────────

class DataProvider:
    @staticmethod
    def from_yahoo(symbols, period="6mo"):
        import yfinance as yf
        results = {}
        batch_size = 30
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            try:
                data = yf.download(batch, period=period, interval="1d",
                                  progress=False, auto_adjust=True, ignore_tz=True)
                if data is not None and not data.empty:
                    for symbol in batch:
                        try:
                            close_col = ('Close', symbol)
                            vol_col = ('Volume', symbol)
                            if close_col not in data.columns:
                                continue
                            close = data[close_col].values.astype(float)
                            volume = data[vol_col].values.astype(float)
                            mask = ~(np.isnan(close) | np.isnan(volume))
                            close = close[mask]; volume = volume[mask]
                            if len(close) >= 120:
                                results[symbol] = (close, volume)
                        except:
                            continue
            except:
                continue
            time.sleep(0.3)
        return results
    
    @staticmethod
    def from_ccxt(symbols, limit=300):
        import ccxt
        exchange = ccxt.binance({"enableRateLimit": True, "options": {"defaultType": "spot"}})
        results = {}
        for symbol in symbols:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, "1d", limit=limit)
                if len(ohlcv) >= 100:
                    close = np.array([c[4] for c in ohlcv], dtype=float)
                    volume = np.array([c[5] for c in ohlcv], dtype=float)
                    results[symbol] = (close, volume)
                time.sleep(0.1)
            except:
                continue
        return results


# ─── Durum Yonetimi ──────────────────────────────────────

def load_status() -> dict:
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"notified": {}, "last_scan": None}

def save_status(status: dict):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def is_already_notified(status: dict, symbol: str, pattern: str) -> bool:
    key = f"{symbol}:{pattern}"
    entry = status.get("notified", {}).get(key)
    if not entry:
        return False
    # 24 saat kontrol
    notified_time = datetime.fromisoformat(entry["time"])
    if datetime.now() - notified_time > timedelta(hours=24):
        return False
    return True

def mark_notified(status: dict, symbol: str, pattern: str, similarity: float, price: float):
    key = f"{symbol}:{pattern}"
    status["notified"][key] = {
        "time": datetime.now().isoformat(),
        "similarity": similarity,
        "price": price,
        "count": status["notified"].get(key, {}).get("count", 0) + 1,
    }
    cutoff = datetime.now().timestamp() - 86400
    status["notified"] = {
        k: v for k, v in status["notified"].items()
        if datetime.fromisoformat(v["time"]).timestamp() > cutoff
    }


# ─── Telegram ────────────────────────────────────────────

def load_env():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "6988108865")
    if not token:
        try:
            from dotenv import load_dotenv
            env_path = Path(__file__).parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                token = os.getenv("TELEGRAM_BOT_TOKEN", "")
                chat_id = os.getenv("TELEGRAM_CHAT_ID", "6988108865")
        except:
            pass
    return token, chat_id

def send_telegram(message: str, no_telegram: bool = False):
    if no_telegram or not message:
        if message:
            print(message)
        return True
    token, chat_id = load_env()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN eksik")
        print(message)
        return True
    import requests
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": chat_id, "text": message,
            "parse_mode": "HTML", "disable_web_page_preview": True,
        }, timeout=10)
        if resp.status_code == 200:
            logger.info(f"Telegram: {len(message)} karakter")
            return True
        else:
            logger.error(f"Telegram hatasi: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"Telegram baglanti: {e}")
        return False


# ─── Pattern Karsilastirma ──────────────────────────────

def signal_to_indicator_state(signal: SignalResult, symbol: str = "") -> IndicatorState:
    """RTUGSignalEngine sonucundan IndicatorState olustur."""
    state = IndicatorState()
    state.symbol = symbol or signal.ticker
    state.div1 = signal.div1
    state.div2 = signal.div2
    state.div3 = signal.div3
    state.div5 = signal.div5
    state.div6 = signal.div6
    state.obv_norm = signal.obv_norm
    state.price = signal.price
    
    # Direction flags
    state.div1_dir = 1 if signal.div1 > 0 else (-1 if signal.div1 < 0 else 0)
    state.div2_dir = 1 if signal.div2 > 0 else (-1 if signal.div2 < 0 else 0)
    state.div3_dir = 1 if signal.div3 > 0 else (-1 if signal.div3 < 0 else 0)
    state.div5_dir = 1 if signal.div5 > 0 else (-1 if signal.div5 < 0 else 0)
    state.div6_dir = 1 if signal.div6 > 0 else (-1 if signal.div6 < 0 else 0)
    state.obv_dir = 1 if signal.obv_norm > 0 else (-1 if signal.obv_norm < 0 else 0)
    
    state.pattern_type = signal.signal_name
    return state


def format_pattern_alert(matches: List[tuple], market_name: str) -> str:
    """Pattern eslesmelerini Telegram mesajina donustur."""
    if not matches:
        return ""
    
    lines = [
        "<b>🧠 RTUG PATTERN ALERT — AI Eslesme Bulundu!</b>",
        f"Kaynak: {market_name}",
        f"Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Eslesme: {len(matches)} sembol",
        "─" * 20,
    ]
    
    for symbol, match, signal in matches[:10]:
        p = match.pattern
        s = match.matched_state
        
        # Pattern durumu
        dir_icons = ("D1:" + ("🟣" if s.div1_dir > 0 else "🩷" if s.div1_dir < 0 else "⚪") +
                    " D2:" + ("🔴" if s.div2_dir > 0 else "🟠" if s.div2_dir < 0 else "⚪") +
                    " D6:" + ("🔵" if s.div6_dir > 0 else "🟤" if s.div6_dir < 0 else "⚪"))
        
        lines.append(
            f"\n🎯 <b>{symbol}</b> | Benzerlik: %{match.similarity:.0f}"
        )
        lines.append(f"   Eslesti: {p.name}")
        lines.append(f"   {dir_icons}")
        lines.append(f"   Bull:{s.bull_count}/5 Bear:{s.bear_count}/5 | ${s.price:.4f}")
        lines.append(f"   Pattern: {signal.signal_name if hasattr(signal, 'signal_name') else signal.breakout_type}")
    
    if len(matches) > 10:
        lines.append(f"\n... ve {len(matches) - 10} sembol daha")
    
    lines.append("\n" + "─" * 20)
    lines.append("RTUG PATTERN MONITOR v2 (7/24 AI)")
    
    return "\n".join(lines)


# ─── Ana Tarama ──────────────────────────────────────────

def scan_and_match(engine: RTUGSignalEngine, memory: PatternMemory,
                   status: dict, data: dict, market_name: str,
                   min_similarity: float = 0.70,
                   no_telegram: bool = False) -> List[tuple]:
    """
    Bir piyasadaki tum sembolleri tara, pattern'lerle karsilastir,
    eslesme bulursa bildir.
    """
    new_matches = []
    
    for symbol, (close, volume) in data.items():
        try:
            # Scanner core ile analiz
            signal = engine.analyze(close, volume)
            if not signal or not signal.breakout_type:
                continue
            
            # IndicatorState'e cevir
            state = signal_to_indicator_state(signal, symbol)
            
            # Pattern memory'de ara
            match = memory.find_best_match(state, min_similarity=min_similarity)
            
            if match and match.is_match:
                # Daha once bildirildi mi?
                if is_already_notified(status, symbol, match.pattern.name):
                    continue
                
                new_matches.append((symbol, match, signal))
                
                # Bildirildi olarak isaretle
                mark_notified(status, symbol, match.pattern.name,
                            match.similarity, signal.price)
                
                # Pattern match sayisini artir
                memory.record_match(match.pattern.name, success=True)
                
                logger.info(f"🔴 PATTERN ESLESTI: {symbol} -> {match.pattern.name} "
                          f"(%{match.similarity:.0f})")
                
        except Exception as e:
            continue
    
    # Yeni eslesmeleri Telegram'a gonder
    if new_matches:
        msg = format_pattern_alert(new_matches, market_name)
        send_telegram(msg, no_telegram)
        logger.info(f"🔴 {len(new_matches)} yeni pattern eslesmesi bildirildi!")
    else:
        logger.info(f"Pattern eslesmesi yok: {market_name}")
    
    return new_matches


# ─── Ana Dongu ──────────────────────────────────────────

def run_scan(engine: RTUGSignalEngine, memory: PatternMemory, status: dict,
             min_similarity: float = 0.70, no_telegram: bool = False,
             scan_bist: bool = True, scan_us: bool = True, scan_crypto: bool = True):
    """Tum piyasalari tara."""
    total_matches = 0
    
    if scan_bist and BIST_SYMBOLS:
        try:
            logger.info(f"BIST taranıyor ({len(BIST_SYMBOLS)} sembol)...")
            data = DataProvider.from_yahoo(BIST_SYMBOLS)
            matches = scan_and_match(engine, memory, status, data, "BIST 100", min_similarity, no_telegram)
            total_matches += len(matches)
        except Exception as e:
            logger.error(f"BIST hatasi: {e}")
    
    if scan_us and SP500_SYMBOLS:
        try:
            logger.info(f"ABD taranıyor ({len(SP500_SYMBOLS)} sembol)...")
            data = DataProvider.from_yahoo(SP500_SYMBOLS)
            matches = scan_and_match(engine, memory, status, data, "US Stocks", min_similarity, no_telegram)
            total_matches += len(matches)
        except Exception as e:
            logger.error(f"US hatasi: {e}")
    
    if scan_crypto and CRYPTO_SYMBOLS:
        try:
            logger.info(f"Kripto taranıyor ({len(CRYPTO_SYMBOLS)} coin)...")
            data = DataProvider.from_ccxt(CRYPTO_SYMBOLS)
            matches = scan_and_match(engine, memory, status, data, "Crypto", min_similarity, no_telegram)
            total_matches += len(matches)
        except Exception as e:
            logger.error(f"Kripto hatasi: {e}")
    
    # Durumu kaydet
    status["last_scan"] = datetime.now().isoformat()
    save_status(status)
    
    if total_matches > 0:
        logger.info(f"✅ Toplam {total_matches} yeni pattern eslesmesi!")
    else:
        logger.info("Yeni pattern eslesmesi yok.")
    
    return total_matches


def run_daemon(interval_minutes: int, min_similarity: float = 0.70,
               no_telegram: bool = False,
               scan_bist: bool = True, scan_us: bool = True, scan_crypto: bool = True):
    """Sonsuz dongu ile 7/24 pattern tarama."""
    engine = RTUGSignalEngine()
    memory = PatternMemory()
    status = load_status()
    
    # Pattern kontrol
    pattern_count = len(memory.patterns)
    if pattern_count == 0:
        logger.warning("Henuz pattern memory'de pattern yok!")
        logger.warning("Once bir gorsel analiz edip pattern kaydedin:")
        logger.warning("  python vision_analyzer.py chart.png --train")
        send_telegram(
            "<b>⚠️ RTUG PATTERN MONITOR</b>\n"
            "Pattern memory bos! Once egitim yapmalisiniz:\n"
            "python vision_analyzer.py <gorsel> --train",
            no_telegram
        )
        return
    
    # Golden pattern var mi?
    goldens = memory.get_golden_patterns()
    golden_msg = f"{len(goldens)} golden" if goldens else "yok"
    
    logger.info(f"{'='*50}")
    logger.info(f"RTUG PATTERN MONITOR v2 BASLADI")
    logger.info(f"Pattern memory: {pattern_count} pattern ({golden_msg})")
    logger.info(f"Threshold: %{min_similarity:.0f}")
    logger.info(f"Interval: {interval_minutes} dk")
    logger.info(f"BIST: {scan_bist}, US: {scan_us}, Crypto: {scan_crypto}")
    logger.info(f"Telegram: {'AKTIF' if not no_telegram else 'PASIF'}")
    logger.info(f"{'='*50}")
    
    send_telegram(
        f"<b>🧠 RTUG PATTERN MONITOR v2 BASLADI</b>\n"
        f"Pattern: {pattern_count} | Golden: {len(goldens)}\n"
        f"Threshold: %{min_similarity:.0f}\n"
        f"BIST: {len(BIST_SYMBOLS)} hisse\n"
        f"US: {len(SP500_SYMBOLS)} hisse\n"
        f"Crypto: {len(CRYPTO_SYMBOLS)} coin\n"
        f"Interval: {interval_minutes} dk\n"
        f"Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        no_telegram
    )
    
    # Ilk taramayi hemen yap
    run_scan(engine, memory, status, min_similarity, no_telegram,
             scan_bist, scan_us, scan_crypto)
    
    # Dongu
    while True:
        try:
            next_scan = datetime.now() + timedelta(minutes=interval_minutes)
            logger.info(f"Sonraki tarama: {next_scan.strftime('%H:%M')}")
            time.sleep(interval_minutes * 60)
            
            logger.info(f"\n{'='*50}")
            logger.info(f"TARAMA: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            run_scan(engine, memory, status, min_similarity, no_telegram,
                     scan_bist, scan_us, scan_crypto)
            logger.info(f"BITTI: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
        except KeyboardInterrupt:
            logger.info("Monitor durduruldu.")
            send_telegram("<b>RTUG PATTERN MONITOR DURDURULDU</b>", no_telegram)
            break
        except Exception as e:
            logger.error(f"Hata: {e}, 5sn sonra yeniden...")
            time.sleep(5)
            continue


# ─── CLI ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RTUG PATTERN MONITOR v2 — AI Pattern Memory Scanner")
    parser.add_argument("--interval", type=int, default=15, help="Tarama araligi (dk)")
    parser.add_argument("--once", action="store_true", help="Tek sefer")
    parser.add_argument("--no-telegram", action="store_true", help="Sadece konsol")
    parser.add_argument("--threshold", type=float, default=0.70, 
                       help="Eslesme threshold (0.0-1.0, varsayilan: 0.70)")
    parser.add_argument("--no-bist", action="store_true")
    parser.add_argument("--no-us", action="store_true")
    parser.add_argument("--no-crypto", action="store_true")
    parser.add_argument("--list-patterns", action="store_true", help="Pattern'leri listele")
    parser.add_argument("--symbol", type=str, help="Tek sembol test")
    parser.add_argument("--stats", action="store_true", help="Memory istatistikleri")
    
    args = parser.parse_args()
    
    memory = PatternMemory()
    
    if args.list_patterns:
        patterns = memory.list_patterns()
        print(f"\n=== PATTERN MEMORY ({len(patterns)} pattern) ===")
        for p in patterns:
            tags = f" [{','.join(p['tags'])}]" if p.get('tags') else ""
            print(f"  {p['name']:30s} | Bull:{p['bull_count']}/{5-p['bear_count']} "
                  f"| {p['source']:8s} | %{p['success_rate']:.0f} | {p['match_count']} eslesme{tags}")
        return
    
    if args.stats:
        stats = memory.get_statistics()
        print("\n=== PATTERN MEMORY ISTATISTIK ===")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        return
    
    if args.symbol:
        # Tek sembol test
        engine = RTUGSignalEngine()
        symbol = args.symbol
        
        print(f"\n=== {symbol} PATTERN TESTI ===\n")
        
        # Crypto test
        is_crypto = "/" in symbol
        if is_crypto:
            data = DataProvider.from_ccxt([symbol])
        else:
            data = DataProvider.from_yahoo([symbol])
        
        if symbol in data:
            close, volume = data[symbol]
            signal = engine.analyze(close, volume)
            state = signal_to_indicator_state(signal, symbol)
            
            print(f"Scanner Sonucu:")
            print(f"  Breakout: {signal.breakout_type or 'YOK'}")
            print(f"  Bull: {signal.bull_count}/5 | Bear: {signal.bear_count}/5")
            print(f"  Div1: {signal.div1:.2f} | Div2: {signal.div2:.2f} | Div3: {signal.div3:.2f}")
            print(f"  Div5: {signal.div5:.2f} | Div6: {signal.div6:.2f}")
            print(f"  OBV: {signal.obv_norm:.4f}")
            print(f"  Fiyat: ${signal.price:.4f}")
            print(f"\nState vektoru: {state.direction_vector}")
            print(f"Bull: {state.bull_count}/5 Bear: {state.bear_count}/5")
            
            # Pattern esleme
            print(f"\nPattern esleme araniyor (threshold: %{args.threshold:.0f})...")
            matches = memory.find_all_matches(state, min_similarity=args.threshold)
            if matches:
                for m in matches:
                    print(f"  ✅ {m.pattern.name}: %{m.similarity:.1f}")
            else:
                print(f"  ❌ Eslesen pattern yok")
                print(f"  Bunu memory'e eklemek icin istersen kaydedebiliriz.")
        else:
            print(f"Veri alinamadi: {symbol}")
        
        return
    
    if args.once:
        engine = RTUGSignalEngine()
        status = load_status()
        run_scan(engine, memory, status, args.threshold, args.no_telegram,
                not args.no_bist, not args.no_us, not args.no_crypto)
    else:
        run_daemon(args.interval, args.threshold, args.no_telegram,
                  not args.no_bist, not args.no_us, not args.no_crypto)


if __name__ == "__main__":
    main()
