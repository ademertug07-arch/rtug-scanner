"""
RTUG BREAKOUT ALERT — Multi-Symbol Scanner
============================================
Tüm hisse senetlerini/kriptoları tara, RTUG breakout sinyali verenleri
Telegram'a bildir.

KULLANIM:
    python rtug_multi_symbol_scanner.py          # Tüm kaynakları tara
    python rtug_multi_symbol_scanner.py --bist   # Sadece BIST
    python rtug_multi_symbol_scanner.py --us     # Sadece US
    python rtug_multi_symbol_scanner.py --crypto # Sadece kripto
    
n8n ENTEGRASYONU:
    n8n Schedule Trigger → Execute Command node → python rtug_multi_symbol_scanner.py
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

# RTUG engine
from rtug_scanner_core import RTUGSignalEngine, BreakoutType, SignalResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rtug-scanner")

# ─── Sembol Listeleri ────────────────────────────────────

# BIST 100 (Türkiye) — En likit hisseler
BIST_SYMBOLS = [
    "AKBNK.IS", "ARCLK.IS", "ASELS.IS", "BIMAS.IS", "EKGYO.IS",
    "EREGL.IS", "FROTO.IS", "GARAN.IS", "GUBRF.IS", "HALKB.IS",
    "ISCTR.IS", "KCHOL.IS", "KRDMD.IS",
    "MAVI.IS", "MPARK.IS", "OYAKC.IS", "PETKM.IS", "PGSUS.IS",
    "SAHOL.IS", "SASA.IS", "SISE.IS", "TAVHL.IS", "TCELL.IS",
    "THYAO.IS", "TOASO.IS", "TUPRS.IS", "VAKBN.IS", "YKBNK.IS",
    "ALBRK.IS", "ALGYO.IS", "ALARK.IS", "AEFES.IS", "ANSGR.IS",
    "BERA.IS", "BRISA.IS", "CCOLA.IS", "CIMSA.IS", "DOHOL.IS",
    "ECZYT.IS", "ENJSA.IS", "ENKAI.IS", "GOLTS.IS", "GSDHO.IS",
    "HURGZ.IS", "ICBCT.IS", "ISGYO.IS", "KONTR.IS",
    "KRVGD.IS", "MGROS.IS", "ODINE.IS", "OTKAR.IS", "POLHO.IS",
    "SOKM.IS", "TABGD.IS", "TKFEN.IS", "TTKOM.IS", "TTRAK.IS",
    "ULKER.IS", "VESTL.IS", "ZOREN.IS",
]

# ABD Hisse Senetleri (büyükler)
US_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "JPM", "V", "JNJ",
    "WMT", "PG", "MA", "UNH", "HD",
    "BAC", "DIS", "ADBE", "CRM", "NFLX",
    "PYPL", "INTC", "AMD", "QCOM", "CSCO",
    "IBM", "ORCL", "UBER", "COIN",
    "MSTR", "PLTR", "SNOW", "DASH", "HOOD",
]

# Kripto Paralar (Binance USDT)
CRYPTO_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT",
    "MATIC/USDT", "UNI/USDT", "SHIB/USDT", "LTC/USDT", "BCH/USDT",
    "ATOM/USDT", "ETC/USDT", "XLM/USDT", "NEAR/USDT", "APT/USDT",
    "ARB/USDT", "OP/USDT", "SUI/USDT", "PEPE/USDT", "INJ/USDT",
    "TIA/USDT", "SEI/USDT", "STRK/USDT", "FIL/USDT", "FTM/USDT",
]

# ─── Veri Sağlayıcıları ─────────────────────────────────

class DataProvider:
    """Hisse senedi/kripto verilerini indirir."""
    
    @staticmethod
    def from_yahoo(symbols: List[str], period: str = "6mo") -> dict:
        """Yahoo Finance'den hisse verilerini indir."""
        import yfinance as yf
        logger.info(f"📥 Yahoo Finance'den {len(symbols)} sembol indiriliyor...")
        
        results = {}
        try:
            # Tek seferde değil, 10'ar gruplar halinde indir (daha kararlı)
            batch_size = 10
            all_data = {}
            
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i+batch_size]
                try:
                    data = yf.download(
                        batch, 
                        period=period, 
                        interval="1d",
                        progress=False,
                        auto_adjust=True,
                        ignore_tz=True
                    )
                    
                    # yfinance 0.1.4+ MultiIndex columns döndürür: (Close, AAPL)
                    if data is not None and not data.empty:
                        for symbol in batch:
                            try:
                                if len(batch) == 1:
                                    # Tek sembollü download: sütunlar (Close, SYM) şeklinde MultiIndex
                                    close_col = ('Close', symbol)
                                    vol_col = ('Volume', symbol)
                                    if close_col in data.columns:
                                        close = data[close_col].values.astype(float)
                                        volume = data[vol_col].values.astype(float)
                                    else:
                                        # Fallback: ticker yoksa sembolü kullan
                                        continue
                                else:
                                    # Çok sembollü download
                                    close_col = ('Close', symbol)
                                    vol_col = ('Volume', symbol)
                                    if close_col not in data.columns:
                                        continue
                                    close = data[close_col].values.astype(float)
                                    volume = data[vol_col].values.astype(float)
                                
                                # NaN'leri temizle
                                mask = ~(np.isnan(close) | np.isnan(volume))
                                close = close[mask]
                                volume = volume[mask]
                                
                                if len(close) < 120:
                                    logger.debug(f"  ⏳ {symbol}: yetersiz veri ({len(close)} bar)")
                                    continue
                                    
                                results[symbol] = (close, volume)
                                logger.debug(f"  ✅ {symbol}: {len(close)} bar, son fiyat: {close[-1]:.2f}")
                                
                            except Exception as e:
                                logger.debug(f"  ⚠️ {symbol}: {e}")
                                continue
                
                except Exception as batch_e:
                    logger.warning(f"  ⚠️ Batch hatası ({i}-{i+batch_size}): {batch_e}")
                    continue
                    
                time.sleep(0.5)  # Rate limiting
                    
        except Exception as e:
            logger.error(f"❌ Yahoo Finance hatası: {e}")
            
        logger.info(f"  ✅ {len(results)}/{len(symbols)} sembol başarıyla indirildi")
        return results
    
    @staticmethod
    def from_ccxt(symbols: List[str], limit: int = 300) -> dict:
        """CCXT (Binance) üzerinden kripto verilerini indir."""
        import ccxt
        logger.info(f"📥 Binance'den {len(symbols)} sembol indiriliyor...")
        
        exchange = ccxt.binance({
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        })
        
        results = {}
        for symbol in symbols:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, "1d", limit=limit)
                if len(ohlcv) < 100:
                    continue
                    
                close = np.array([c[4] for c in ohlcv], dtype=float)
                volume = np.array([c[5] for c in ohlcv], dtype=float)
                
                results[symbol] = (close, volume)
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                logger.debug(f"  ⚠️ {symbol}: {e}")
                continue
        
        logger.info(f"  ✅ {len(results)} sembol başarıyla indirildi")
        return results


# ─── Ana Tarayıcı ─────────────────────────────────────────

class RTUGMultiScanner:
    """
    Tüm sembolleri tara, breakout sinyali verenleri raporla.
    """
    
    def __init__(self, min_bars: int = 100):
        self.engine = RTUGSignalEngine()
        self.min_bars = min_bars
    
    def scan_symbols(self, data: dict) -> Tuple[List[SignalResult], List[SignalResult]]:
        """
        Sembolleri tara, sinyali olanları ve olmayanları döndür.
        
        Returns:
            (signals, no_signals) — sinyal listesi ve sinyalsizler
        """
        signals = []
        no_signals = []
        
        for symbol, (close, volume) in data.items():
            try:
                if len(close) < self.min_bars:
                    continue
                    
                result = self.engine.analyze(close, volume)
                # Sembol adını ekle
                result = result._replace(ticker=symbol)
                
                if result.has_signal:
                    signals.append(result)
                else:
                    no_signals.append(result)
                    
            except Exception as e:
                logger.debug(f"  ⚠️ {symbol} analiz hatası: {e}")
                continue
        
        # Sinyalleri skora göre sırala (en güçlü önce)
        signals.sort(key=lambda r: r.score, reverse=True)
        
        return signals, no_signals
    
    def scan_parallel(self, data: dict, max_workers: int = 10) -> Tuple[List[SignalResult], List[SignalResult]]:
        """
        Çoklu iş parçacığı ile hızlı tarama.
        """
        all_signals = []
        all_no_signals = []
        
        # Sembolleri gruplara böl
        items = list(data.items())
        chunk_size = max(1, len(items) // max_workers)
        chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
        
        def scan_chunk(chunk):
            local_data = dict(chunk)
            # Her chunk için ayrı engine (thread-safe)
            local_engine = RTUGSignalEngine()
            sigs, nos = [], []
            for symbol, (close, volume) in local_data.items():
                try:
                    result = local_engine.analyze(close, volume)
                    result = result._replace(ticker=symbol)
                    if result.has_signal:
                        sigs.append(result)
                    else:
                        nos.append(result)
                except:
                    continue
            return sigs, nos
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(scan_chunk, chunk) for chunk in chunks]
            for future in as_completed(futures):
                sigs, nos = future.result()
                all_signals.extend(sigs)
                all_no_signals.extend(nos)
        
        all_signals.sort(key=lambda r: r.score, reverse=True)
        return all_signals, all_no_signals
    
    def format_telegram_message(self, signals: List[SignalResult], source_name: str) -> str:
        """Sinyalleri Telegram mesajına dönüştür."""
        if not signals:
            return ""
        
        icon_map = {
            BreakoutType.SUPER_BULLISH: "*",
            BreakoutType.SUPER_BEARISH: "v",
            BreakoutType.BULLISH: "+",
            BreakoutType.BEARISH: "-",
            BreakoutType.CROSS_UP: "x",
            BreakoutType.CROSS_DOWN: "x",
            # Surround pattern ikonları
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
            f"<b>RTUG TARAMA SONUCLARI</b>",
            f"Kaynak: {source_name}",
            f"Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            f"Sinyal: {len(signals)} sembol",
            f"----------------------------",
        ]
        
        for s in signals[:15]:  # En fazla 15 sonuç
            icon = icon_map.get(s.breakout_type, ">")
            
            # Surround pattern'i varsa detay ekle
            surround_detail = ""
            if s.surround_type:
                surround_detail = f"\n   [COLOR] {s.surround_icons}"
            
            lines.append(
                f"{icon} <b>{s.ticker}</b> | {s.signal_name}\n"
                f"   Bull:{s.bull_count}/5 Bear:{s.bear_count}/5 | Skor: {s.score:.0f}% | ${s.price:.2f}"
                f"{surround_detail}"
            )
        
        if len(signals) > 15:
            lines.append(f"\n... ve {len(signals) - 15} sembol daha")
        
        lines.append(f"\n----------------------------")
        lines.append(f"RTUG BREAKOUT SCANNER")
        
        return "\n".join(lines)
    
    def send_telegram(self, message: str):
        """Telegram'a mesaj gönder."""
        if not message:
            logger.info("ℹ️ Sinyal yok, mesaj gönderilmedi")
            return
        
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "6988108865")
        
        if not token:
            # .env dosyasından oku
            try:
                from dotenv import load_dotenv
                load_dotenv()
                token = os.getenv("TELEGRAM_BOT_TOKEN", "")
            except:
                pass
        
        if not token:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN eksik, sadece konsola yazdırılıyor")
            print(message)
            return
        
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
                logger.info(f"✅ Telegram bildirimi gönderildi ({len(message)} karakter)")
            else:
                logger.error(f"❌ Telegram hatası: {resp.status_code}")
        except Exception as e:
            logger.error(f"❌ Telegram bağlantı hatası: {e}")


# ─── Ana Çalıştırma ─────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RTUG Multi-Symbol Scanner")
    parser.add_argument("--bist", action="store_true", help="Sadece BIST tara")
    parser.add_argument("--us", action="store_true", help="Sadece US tara")
    parser.add_argument("--crypto", action="store_true", help="Sadece kripto tara")
    parser.add_argument("--no-telegram", action="store_true", help="Telegram'a gönderme")
    parser.add_argument("--fast", action="store_true", help="Hızlı tarama (paralel)")
    args = parser.parse_args()
    
    # Hangi kaynaklar taranacak?
    scan_bist = args.bist or not (args.us or args.crypto)
    scan_us = args.us or not (args.bist or args.crypto)
    scan_crypto = args.crypto or not (args.bist or args.us)
    
    scanner = RTUGMultiScanner()
    all_signals = []
    
    print("\n" + "="*60)
    print("  RTUG BREAKOUT + COLOR SURROUND SCANNER")
    print("="*60)
    
    # 1. BIST tara
    if scan_bist:
        print(f"\n📊 BIST 100 taranıyor ({len(BIST_SYMBOLS)} sembol)...")
        data = DataProvider.from_yahoo(BIST_SYMBOLS)
        
        if args.fast:
            signals, _ = scanner.scan_parallel(data)
        else:
            signals, _ = scanner.scan_symbols(data)
        
        if signals:
            msg = scanner.format_telegram_message(signals, "BIST 100")
            if not args.no_telegram:
                scanner.send_telegram(msg)
            all_signals.extend(signals)
            print(f"\n✅ BIST'te {len(signals)} sinyal bulundu!")
        else:
            print("ℹ️ BIST'te sinyal bulunamadı.")
    
    # 2. US tara
    if scan_us:
        print(f"\n📊 US hisseleri taranıyor ({len(US_SYMBOLS)} sembol)...")
        data = DataProvider.from_yahoo(US_SYMBOLS)
        
        if args.fast:
            signals, _ = scanner.scan_parallel(data)
        else:
            signals, _ = scanner.scan_symbols(data)
        
        if signals:
            msg = scanner.format_telegram_message(signals, "US Stocks")
            if not args.no_telegram:
                scanner.send_telegram(msg)
            all_signals.extend(signals)
            print(f"\n✅ US'te {len(signals)} sinyal bulundu!")
        else:
            print("ℹ️ US'te sinyal bulunamadı.")
    
    # 3. Kripto tara
    if scan_crypto:
        print(f"\n📊 Kripto taranıyor ({len(CRYPTO_SYMBOLS)} sembol)...")
        data = DataProvider.from_ccxt(CRYPTO_SYMBOLS)
        
        if args.fast:
            signals, _ = scanner.scan_parallel(data)
        else:
            signals, _ = scanner.scan_symbols(data)
        
        if signals:
            msg = scanner.format_telegram_message(signals, "Kripto (Binance)")
            if not args.no_telegram:
                scanner.send_telegram(msg)
            all_signals.extend(signals)
            print(f"\n✅ Kriptoda {len(signals)} sinyal bulundu!")
        else:
            print("ℹ️ Kriptoda sinyal bulunamadı.")
    
    # Özet
    print("\n" + "="*60)
    print(f"  📊 TARAMA ÖZETİ")
    print(f"  Toplam sinyal: {len(all_signals)}")
    if all_signals:
        print(f"\n  En güçlü sinyaller:")
        for s in all_signals[:5]:
            print(f"    {s.signal_name} {s.ticker} (Skor: {s.score:.0f}%)")
    print("="*60)
    
    return all_signals


if __name__ == "__main__":
    main()
