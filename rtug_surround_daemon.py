"""
RTUG COLOR SURROUND DAEMON — 7/24 Otonom Tarama + Telegram Bildirim
==================================================================
Her N dakikada bir tum piyasaları tarar, color surround pattern'lerini
tespit eder ve Telegram'a aninda bildirim gonderir.

KULLANIM:
    python rtug_surround_daemon.py                   # Varsayilan (15dk)
    python rtug_surround_daemon.py --interval 5       # Her 5 dk'da bir
    python rtug_surround_daemon.py --once             # Tek sefer calistir
    python rtug_surround_daemon.py --no-telegram      # Sadece konsola yaz

WINDOWS SERVICE (Task Scheduler):
    python rtug_surround_daemon.py --install          # Task Scheduler'a ekle
    python rtug_surround_daemon.py --uninstall        # Task Scheduler'dan sil
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from datetime import datetime
from typing import List, Optional
from pathlib import Path

import numpy as np

# RTUG engine
from rtug_scanner_core import RTUGSignalEngine, BreakoutType, SignalResult

# ─── LOGGING ─────────────────────────────────────────────
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "surround_daemon.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("rtug-daemon")

# ─── DURUM DOSYASI (daha once bildirilen pattern'leri kaydet) ──
STATUS_FILE = Path(__file__).parent / ".surround_status.json"

# ─── SEMBOL LISTELERI ────────────────────────────────────

BIST_SYMBOLS = [
    "AKBNK.IS", "ARCLK.IS", "ASELS.IS", "BIMAS.IS", "EKGYO.IS",
    "EREGL.IS", "FROTO.IS", "GARAN.IS", "GUBRF.IS", "HALKB.IS",
    "ISCTR.IS", "KCHOL.IS", "KRDMD.IS", "MAVI.IS", "MPARK.IS",
    "OYAKC.IS", "PETKM.IS", "PGSUS.IS", "SAHOL.IS", "SASA.IS",
    "SISE.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS", "TOASO.IS",
    "TUPRS.IS", "VAKBN.IS", "YKBNK.IS", "ALBRK.IS", "ALGYO.IS",
    "ALARK.IS", "AEFES.IS", "ANSGR.IS", "BERA.IS", "BRISA.IS",
    "CCOLA.IS", "CIMSA.IS", "DOHOL.IS", "ECZYT.IS", "ENJSA.IS",
    "ENKAI.IS", "GOLTS.IS", "GSDHO.IS", "HURGZ.IS", "ICBCT.IS",
    "ISGYO.IS", "KONTR.IS", "KRVGD.IS", "MGROS.IS", "ODINE.IS",
    "OTKAR.IS", "POLHO.IS", "SOKM.IS", "TABGD.IS", "TKFEN.IS",
    "TTKOM.IS", "TTRAK.IS", "ULKER.IS", "VESTL.IS", "ZOREN.IS",
]

US_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "JPM", "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD",
    "BAC", "DIS", "ADBE", "CRM", "NFLX", "PYPL", "INTC",
    "AMD", "QCOM", "CSCO", "IBM", "ORCL", "UBER", "COIN",
    "MSTR", "PLTR", "SNOW", "DASH", "HOOD",
]

CRYPTO_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT",
    "MATIC/USDT", "UNI/USDT", "SHIB/USDT", "LTC/USDT", "BCH/USDT",
    "ATOM/USDT", "ETC/USDT", "XLM/USDT", "NEAR/USDT", "APT/USDT",
    "ARB/USDT", "OP/USDT", "SUI/USDT", "PEPE/USDT", "INJ/USDT",
]

# ─── DURUM YONETIMI ─────────────────────────────────────

def load_status() -> dict:
    """Daha once bildirilen pattern'leri yukle."""
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"notified": {}, "last_scan": None}

def save_status(status: dict):
    """Durumu kaydet."""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def is_already_notified(status: dict, symbol: str, pattern: str) -> bool:
    """Bu sembol+pattern daha once bildirildi mi?"""
    key = f"{symbol}:{pattern}"
    return key in status.get("notified", {})

def mark_notified(status: dict, symbol: str, pattern: str, strength: int, price: float):
    """Bu sembol+pattern'i bildirildi olarak isaretle."""
    key = f"{symbol}:{pattern}"
    status["notified"][key] = {
        "time": datetime.now().isoformat(),
        "strength": strength,
        "price": price
    }
    # 24 saatten eski kayitlari temizle
    cutoff = datetime.now().timestamp() - 86400
    status["notified"] = {
        k: v for k, v in status["notified"].items()
        if datetime.fromisoformat(v["time"]).timestamp() > cutoff
    }

# ─── TELEGRAM ────────────────────────────────────────────

def load_env():
    """.env dosyasindan Telegram bilgilerini oku."""
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
    """Telegram'a mesaj gonder."""
    if no_telegram or not message:
        if message:
            print(message)
        return True
    
    token, chat_id = load_env()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN eksik, sadece konsola yaziliyor")
        print(message)
        return True
    
    import requests
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=10)
        
        if resp.status_code == 200:
            logger.info(f"Telegram bildirimi gonderildi ({len(message)} karakter)")
            return True
        else:
            logger.error(f"Telegram hatasi: {resp.status_code} - {resp.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"Telegram baglanti hatasi: {e}")
        return False

# ─── DATA PROVIDER ───────────────────────────────────────

class DataProvider:
    """Hisse senedi/kripto verilerini indirir."""
    
    @staticmethod
    def from_yahoo(symbols: List[str], period: str = "6mo") -> dict:
        """Yahoo Finance'den hisse verilerini indir."""
        import yfinance as yf
        results = {}
        batch_size = 10
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            try:
                data = yf.download(
                    batch, period=period, interval="1d",
                    progress=False, auto_adjust=True, ignore_tz=True
                )
                
                if data is not None and not data.empty:
                    for symbol in batch:
                        try:
                            if len(batch) == 1:
                                close_col = ('Close', symbol)
                                vol_col = ('Volume', symbol)
                            else:
                                close_col = ('Close', symbol)
                                vol_col = ('Volume', symbol)
                            
                            if close_col not in data.columns:
                                continue
                            
                            close = data[close_col].values.astype(float)
                            volume = data[vol_col].values.astype(float)
                            
                            mask = ~(np.isnan(close) | np.isnan(volume))
                            close = close[mask]
                            volume = volume[mask]
                            
                            if len(close) >= 120:
                                results[symbol] = (close, volume)
                        except:
                            continue
            except:
                continue
            time.sleep(0.3)
        
        return results
    
    @staticmethod
    def from_ccxt(symbols: List[str], limit: int = 300) -> dict:
        """CCXT (Binance) uzerinden kripto verilerini indir."""
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

# ─── TARAMA MOTORU ───────────────────────────────────────

def scan_market(data: dict, engine: RTUGSignalEngine, market_name: str) -> List[SignalResult]:
    """Bir piyasadaki tum sembolleri tara, surround pattern'lerini bul."""
    signals = []
    
    for symbol, (close, volume) in data.items():
        try:
            result = engine.analyze(close, volume)
            result = result._replace(ticker=symbol)
            
            if result.has_signal and result.surround_type:
                signals.append(result)
        except:
            continue
    
    signals.sort(key=lambda r: r.score, reverse=True)
    logger.info(f"{market_name}: {len(signals)} surround sinyali bulundu")
    return signals

def format_alert_message(signals: List[SignalResult], market_name: str) -> str:
    """Surround sinyallerini Telegram mesajina donustur."""
    if not signals:
        return ""
    
    surround_icons = {
        BreakoutType.BULL_SURROUND: "P>",
        BreakoutType.BEAR_SURROUND: "R<",
        BreakoutType.STRONG_BULL_SUR: "PS",
        BreakoutType.STRONG_BEAR_SUR: "RS",
        BreakoutType.DEEP_BULL_SUR: "DB",
        BreakoutType.DEEP_BEAR_SUR: "DR",
        BreakoutType.REV_CIRCLE_BULL: "CB",
        BreakoutType.REV_CIRCLE_BEAR: "CR",
    }
    
    lines = [
        "<b>RTUG COLOR SURROUND ALERT</b>",
        f"Kaynak: {market_name}",
        f"Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Sinyal: {len(signals)} sembol",
        f"----------------------------",
    ]
    
    for s in signals[:10]:
        icon = surround_icons.get(s.breakout_type, "??")
        lines.append(
            f"{icon} <b>{s.ticker}</b> | {s.signal_name}\n"
            f"   Skor: {s.score:.0f}% | {s.color_status}\n"
            f"   Bull:{s.bull_count}/5 Bear:{s.bear_count}/5 | ${s.price:.2f}"
        )
    
    if len(signals) > 10:
        lines.append(f"... ve {len(signals) - 10} sembol daha")
    
    lines.append(f"----------------------------")
    lines.append(f"RTUG SURROUND DAEMON (7/24)")
    
    return "\n".join(lines)

# ─── ANA DONGU ───────────────────────────────────────────

def run_scan(engine: RTUGSignalEngine, status: dict, no_telegram: bool = False,
             scan_bist: bool = True, scan_us: bool = True, scan_crypto: bool = True):
    """Tek bir tarama calistir."""
    new_signals = []
    
    # BIST
    if scan_bist:
        try:
            logger.info(f"BIST taranıyor ({len(BIST_SYMBOLS)} sembol)...")
            data = DataProvider.from_yahoo(BIST_SYMBOLS)
            signals = scan_market(data, engine, "BIST 100")
            for s in signals:
                key = f"{s.ticker}:{s.surround_type}"
                if not is_already_notified(status, s.ticker, s.surround_type):
                    new_signals.append(("BIST 100", s))
                    mark_notified(status, s.ticker, s.surround_type, s.surround_strength, s.price)
        except Exception as e:
            logger.error(f"BIST tarama hatasi: {e}")
    
    # US Stocks
    if scan_us:
        try:
            logger.info(f"ABD hisseleri taranıyor ({len(US_SYMBOLS)} sembol)...")
            data = DataProvider.from_yahoo(US_SYMBOLS)
            signals = scan_market(data, engine, "US Stocks")
            for s in signals:
                key = f"{s.ticker}:{s.surround_type}"
                if not is_already_notified(status, s.ticker, s.surround_type):
                    new_signals.append(("US Stocks", s))
                    mark_notified(status, s.ticker, s.surround_type, s.surround_strength, s.price)
        except Exception as e:
            logger.error(f"US tarama hatasi: {e}")
    
    # Crypto
    if scan_crypto:
        try:
            logger.info(f"Kripto taranıyor ({len(CRYPTO_SYMBOLS)} sembol)...")
            data = DataProvider.from_ccxt(CRYPTO_SYMBOLS)
            signals = scan_market(data, engine, "Crypto")
            for s in signals:
                key = f"{s.ticker}:{s.surround_type}"
                if not is_already_notified(status, s.ticker, s.surround_type):
                    new_signals.append(("Crypto", s))
                    mark_notified(status, s.ticker, s.surround_type, s.surround_strength, s.price)
        except Exception as e:
            logger.error(f"Kripto tarama hatasi: {e}")
    
    # Durumu kaydet
    status["last_scan"] = datetime.now().isoformat()
    save_status(status)
    
    # Yeni sinyalleri Telegram'a gonder
    if new_signals:
        # Her piyasa icin ayri mesaj
        markets = {}
        for mkt, sig in new_signals:
            if mkt not in markets:
                markets[mkt] = []
            markets[mkt].append(sig)
        
        for mkt, sigs in markets.items():
            msg = format_alert_message(sigs, mkt)
            send_telegram(msg, no_telegram)
        
        logger.info(f"YENI: {len(new_signals)} yeni surround sinyali bulundu!")
    else:
        logger.info("Yeni surround sinyali yok.")
    
    return new_signals

# ─── DAEMON ──────────────────────────────────────────────

def run_daemon(interval_minutes: int, no_telegram: bool = False,
               scan_bist: bool = True, scan_us: bool = True, scan_crypto: bool = True):
    """Sonsuz dongu ile 7/24 tarama."""
    engine = RTUGSignalEngine()
    status = load_status()
    
    logger.info(f"{'='*50}")
    logger.info(f"RTUG SURROUND DAEMON BASLADI")
    logger.info(f"Interval: {interval_minutes} dk")
    logger.info(f"BIST: {scan_bist}, US: {scan_us}, Crypto: {scan_crypto}")
    logger.info(f"Telegram: {'AKTIF' if not no_telegram else 'PASIF'}")
    logger.info(f"{'='*50}")
    
    # Ilk taramayi hemen yap
    send_telegram(
        f"<b>RTUG SURROUND DAEMON BASLADI</b>\n"
        f"Interval: {interval_minutes} dk\n"
        f"BIST: {len(BIST_SYMBOLS)} hisse\n"
        f"US: {len(US_SYMBOLS)} hisse\n"
        f"Crypto: {len(CRYPTO_SYMBOLS)} coin\n"
        f"Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        no_telegram
    )
    
    run_scan(engine, status, no_telegram, scan_bist, scan_us, scan_crypto)
    
    # Dongu
    while True:
        try:
            logger.info(f"\n--- {interval_minutes} dk bekleniyor... ---")
            time.sleep(interval_minutes * 60)
            
            logger.info(f"\n{'='*50}")
            logger.info(f"TARAMA BASLADI: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            run_scan(engine, status, no_telegram, scan_bist, scan_us, scan_crypto)
            logger.info(f"TARAMA BITTI: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
        except KeyboardInterrupt:
            logger.info("Daemon kullanici tarafindan durduruldu.")
            send_telegram("<b>RTUG SURROUND DAEMON DURDURULDU</b>", no_telegram)
            break
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            logger.info("5 saniye sonra yeniden baslaniliyor...")
            time.sleep(5)
            continue

# ─── WINDOWS TASK SCHEDULER ──────────────────────────────

def install_task(interval_minutes: int):
    """Windows Task Scheduler'a gorev ekle (her acilista baslasin)."""
    script_path = Path(__file__).resolve()
    python_path = sys.executable
    
    task_name = "RTUGSurroundDaemon"
    task_desc = "RTUG Color Surround 7/24 Tarama Daemon"
    
    cmd = f'"{python_path}" "{script_path}" --interval {interval_minutes}'
    
    try:
        # Gorevi olustur
        ps_cmd = f'''
        $action = New-ScheduledTaskAction -Execute "{python_path}" -Argument '"{script_path}" --interval {interval_minutes}'
        $trigger = New-ScheduledTaskTrigger -AtStartup -RandomDelay 00:01:00
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "{task_desc}" -Force
        '''
        
        subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True, timeout=30)
        logger.info(f"Task Scheduler gorevi eklendi: {task_name}")
        logger.info(f"Komut: {cmd}")
        print(f"\n[OK] Task Scheduler gorevi eklendi: '{task_name}'")
        print(f"    Her acilista otomatik baslayacak (interval: {interval_minutes} dk)")
        
        # Ayrica bir de baslangic kisa yolu
        startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        vbs_path = startup_dir / "RTUG_Surround_Daemon.vbs"
        if startup_dir.exists():
            vbs_content = f'''CreateObject("WScript.Shell").Run "{cmd}", 0, False
'''
            with open(vbs_path, "w", encoding="utf-8") as f:
                f.write(vbs_content)
            logger.info(f"Startup kisa yolu eklendi: {vbs_path}")
            print(f"    Startup kisa yolu: {vbs_path}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Task Scheduler hatasi: {e.stderr.decode() if e.stderr else 'Bilinmeyen hata'}")
        print(f"\n[HATA] Task Scheduler gorevi eklenemedi.")
        print(f"    Manuel: python \"{script_path}\" --interval {interval_minutes}")
        print(f"    Bunu Startup klasorune .bat olarak kaydedin.")
        
        # Fallback: startup klasorune .bat ekle
        try:
            startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            if startup_dir.exists():
                bat_path = startup_dir / "RTUG_Surround_Daemon.bat"
                bat_content = f'@echo off\nstart "" "{python_path}" "{script_path}" --interval {interval_minutes}\n'
                with open(bat_path, "w") as f:
                    f.write(bat_content)
                print(f"    Startup .bat dosyasi: {bat_path}")
        except:
            pass

def uninstall_task():
    """Task Scheduler gorevini kaldir."""
    task_name = "RTUGSurroundDaemon"
    try:
        ps_cmd = f'Unregister-ScheduledTask -TaskName "{task_name}" -Confirm:$false'
        subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True, timeout=15)
        logger.info(f"Task Scheduler gorevi kaldirildi: {task_name}")
        print(f"\n[OK] Task Scheduler gorevi kaldirildi.")
    except:
        logger.warning(f"Task Scheduler gorevi bulunamadi veya kaldirilamadi: {task_name}")
        print(f"\n[-] Task Scheduler gorevi bulunamadi.")

# ─── ANA ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RTUG Color Surround Daemon (7/24)")
    parser.add_argument("--interval", type=int, default=15, help="Tarama araligi (dakika, varsayilan: 15)")
    parser.add_argument("--once", action="store_true", help="Tek sefer calistir, donguye girme")
    parser.add_argument("--no-telegram", action="store_true", help="Telegram'a gonderme, sadece konsol")
    parser.add_argument("--no-bist", action="store_true", help="BIST'i tarama")
    parser.add_argument("--no-us", action="store_true", help="ABD hisselerini tarama")
    parser.add_argument("--no-crypto", action="store_true", help="Kriptoyu tarama")
    parser.add_argument("--install", action="store_true", help="Windows Task Scheduler'a ekle")
    parser.add_argument("--uninstall", action="store_true", help="Task Scheduler'dan kaldir")
    
    args = parser.parse_args()
    
    if args.install:
        install_task(args.interval)
        return
    
    if args.uninstall:
        uninstall_task()
        return
    
    engine = RTUGSignalEngine()
    status = load_status()
    
    if args.once:
        logger.info("Tek seferlik tarama...")
        run_scan(engine, status, args.no_telegram,
                 not args.no_bist, not args.no_us, not args.no_crypto)
    else:
        run_daemon(args.interval, args.no_telegram,
                   not args.no_bist, not args.no_us, not args.no_crypto)

if __name__ == "__main__":
    main()
