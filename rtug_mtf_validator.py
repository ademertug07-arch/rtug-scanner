"""
RTUG MULTI-TIMEFRAME VALIDATOR
================================
Daily timeframe'da bulunan pattern eslesmelerini 4h ve 1h'de dogrular.
Yanlis sinyalleri (false positive) filtrelemek icin kullanilir.

KULLANIM:
    from rtug_mtf_validator import MTFValidator
    validator = MTFValidator()
    result = validator.validate("BTC/USDT", daily_signal, "crypto")
    if result.confidence >= 0.4:
        # Sinyal dogrulandi
        print(f"MTF onay: %{result.confidence:.0f}")
    else:
        print(f"MTF veto: %{result.confidence:.0f} — {result.reason}")
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import numpy as np

import pandas as pd
from rtug_scanner_core import RTUGSignalEngine, SignalResult

logger = logging.getLogger("rtug-mtf")

# Lower timeframe konfigurasyonlari
TF_CONFIG = {
    "h4": {"ccxt": "4h", "bars": 200, "weight": 0.6},
    "h1": {"ccxt": "1h", "bars": 200, "weight": 0.4},
}

@dataclass
class TFAlignment:
    """Tek bir timeframe icin alignment sonucu."""
    tf_name: str
    has_signal: bool = False
    divergence_count: int = 0
    div1_aligned: bool = False
    div2_aligned: bool = False
    div6_aligned: bool = False
    obv_aligned: bool = False
    volume_rising: bool = False
    score: float = 0.0

@dataclass
class MTFResult:
    """Multi-timeframe dogrulama sonucu."""
    confidence: float = 0.0
    is_validated: bool = False
    reason: str = ""
    alignments: Dict[str, TFAlignment] = field(default_factory=dict)
    details: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "confidence": round(self.confidence, 3),
            "is_validated": self.is_validated,
            "reason": self.reason,
            "details": self.details,
            "alignments": {
                k: {
                    "has_signal": v.has_signal,
                    "divergence_count": v.divergence_count,
                    "div1_aligned": v.div1_aligned,
                    "div2_aligned": v.div2_aligned,
                    "div6_aligned": v.div6_aligned,
                    "obv_aligned": v.obv_aligned,
                    "volume_rising": v.volume_rising,
                    "score": round(v.score, 3),
                }
                for k, v in alignments.items()
            } if hasattr(self, 'alignments') else {}
        }


class MTFValidator:
    """
    Multi-Timeframe Validator.
    
    Pattern sinyalinin daha dusuk timeframe'lerde teyit edilmesini saglar:
    - 4h: Orta vadeli trend uyumu (en onemli)
    - 1h: Kisa vadeli momentum teyidi
    
    Skorlama:
      0.7+  → Strong (tum TF'ler teyit ediyor)
      0.4+  → Medium (en az 1 TF teyit ediyor)
      <0.4  → Weak (teyit yok, FP riski yuksek)
    """
    
    def __init__(self):
        self.engine = RTUGSignalEngine()
        self._ccxt_cache: Dict[str, dict] = {}
    
    def validate(self, symbol: str, daily_signal: SignalResult,
                 market_type: str = "crypto") -> MTFResult:
        """
        Ana dogrulama metodu.
        
        Args:
            symbol: Sembol adi (BTC/USDT, AAPL, AKBNK.IS)
            daily_signal: Gunluk timeframe'daki sinyal
            market_type: "crypto", "bist", veya "us"
        
        Returns:
            MTFResult: Dogrulama sonucu
        """
        result = MTFResult()
        
        # Gunluk sinyalin divergence yonlerini al
        d1_dir = 1 if daily_signal.div1 > 0 else (-1 if daily_signal.div1 < 0 else 0)
        d2_dir = 1 if daily_signal.div2 > 0 else (-1 if daily_signal.div2 < 0 else 0)
        d6_dir = 1 if daily_signal.div6 > 0 else (-1 if daily_signal.div6 < 0 else 0)
        daily_bullish = daily_signal.bull_count > daily_signal.bear_count
        
        # Lower timeframe verilerini getir
        ltf_data = self._fetch_ltf(symbol, market_type)
        if not ltf_data:
            result.reason = "LTF verisi alinamadi, MTF atlaniyor"
            result.confidence = 0.5  # Notr — veri yoksa filtreleme
            return result
        
        # Her lower TF'de analiz yap
        aligned_count = 0
        total_weight = 0
        weighted_score = 0.0
        
        for tf_name, (close, volume) in ltf_data.items():
            if len(close) < 100:
                continue
            
            alignment = self._check_tf(tf_name, close, volume, d1_dir, d2_dir, d6_dir, daily_bullish)
            result.alignments[tf_name] = alignment
            result.details.extend(self._detail_lines(tf_name, alignment))
            
            weight = TF_CONFIG.get(tf_name, {}).get("weight", 0.5)
            total_weight += weight
            weighted_score += alignment.score * weight
            
            if alignment.score >= 0.5:
                aligned_count += 1
        
        if total_weight > 0:
            result.confidence = weighted_score / total_weight
        
        # Sonuc degerlendirme
        if result.confidence >= 0.7:
            result.is_validated = True
            result.reason = f"Guclu MTF dogrulama (conf: %{result.confidence:.0f}, {aligned_count}/{len(result.alignments)} TF)"
        elif result.confidence >= 0.4:
            result.is_validated = True
            result.reason = f"Orta MTF dogrulama (conf: %{result.confidence:.0f}, {aligned_count}/{len(result.alignments)} TF)"
        else:
            result.is_validated = False
            result.reason = f"MTF teyit YOK (conf: %{result.confidence:.0f}) — FP riski yuksek"
        
        return result
    
    def _check_tf(self, tf_name: str, close: np.ndarray, volume: np.ndarray,
                  d1_dir: int, d2_dir: int, d6_dir: int,
                  daily_bullish: bool) -> TFAlignment:
        """Tek bir lower timeframe'de alignment kontrol et."""
        alignment = TFAlignment(tf_name=tf_name)
        
        # Lower TF'de engine'i calistir
        ltf_signal = self.engine.analyze(close, volume)
        if not ltf_signal or not ltf_signal.breakout_type:
            alignment.score = 0.2
            return alignment
        
        alignment.has_signal = True
        alignment.divergence_count = ltf_signal.bull_count + ltf_signal.bear_count
        
        # Divergence yon uyumu
        lt_d1 = 1 if ltf_signal.div1 > 0 else (-1 if ltf_signal.div1 < 0 else 0)
        lt_d2 = 1 if ltf_signal.div2 > 0 else (-1 if ltf_signal.div2 < 0 else 0)
        lt_d6 = 1 if ltf_signal.div6 > 0 else (-1 if ltf_signal.div6 < 0 else 0)
        
        alignment.div1_aligned = d1_dir != 0 and lt_d1 == d1_dir
        alignment.div2_aligned = d2_dir != 0 and lt_d2 == d2_dir
        alignment.div6_aligned = d6_dir != 0 and lt_d6 == d6_dir
        
        # OBV yon uyumu (gunluk bullish ise LTF'de de OBV pozitif olmali)
        daily_obv_dir = 1 if daily_bullish else -1 if ltf_signal.obv_norm < 0 else 0
        lt_obv_dir = 1 if ltf_signal.obv_norm > 0 else (-1 if ltf_signal.obv_norm < 0 else 0)
        alignment.obv_aligned = daily_obv_dir != 0 and lt_obv_dir == daily_obv_dir
        
        # Volume trend (son 5 bar / onceki 15 bar)
        vol_ratio = float(np.mean(volume[-5:]) / (np.mean(volume[-20:-5]) + 1e-9))
        alignment.volume_rising = vol_ratio > 1.15
        
        # Skor hesapla
        key_div_alignments = sum([alignment.div1_aligned, alignment.div2_aligned, alignment.div6_aligned])
        score = key_div_alignments / 3 * 0.5  # 0-0.5 divergence uyumu
        
        if alignment.obv_aligned:
            score += 0.2  # +0.2 OBV uyumu
        
        if alignment.volume_rising:
            score += 0.15  # +0.15 volume destegi
        
        if alignment.has_signal and alignment.divergence_count >= 2:
            score += 0.15  # +0.15 lower TF'de de sinyal var
        
        alignment.score = min(1.0, score)
        return alignment
    
    def _detail_lines(self, tf_name: str, alignment: TFAlignment) -> List[str]:
        lines = []
        if alignment.score >= 0.6:
            prefix = "+"
        elif alignment.score >= 0.3:
            prefix = "~"
        else:
            prefix = "-"
        
        parts = []
        if alignment.div1_aligned: parts.append("D1")
        if alignment.div2_aligned: parts.append("D2")
        if alignment.div6_aligned: parts.append("D6")
        divs = "+".join(parts) if parts else "none"
        
        obv = "OBV+" if alignment.obv_aligned else "OBV-"
        vol = f"vol{x:.1f}" if alignment.volume_rising else "vol-" if alignment.volume_rising is not None else "vol?"
        
        lines.append(f"  {prefix} {tf_name}: {divs} | {obv} | {vol} (score:{alignment.score:.2f})")
        return lines
    
    def _fetch_ltf(self, symbol: str, market_type: str) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Lower timeframe verilerini getir."""
        result = {}
        
        if market_type == "crypto":
            result = self._fetch_ccxt_ltf(symbol)
        else:
            result = self._fetch_yahoo_ltf(symbol)
        
        return result
    
    def _fetch_ccxt_ltf(self, symbol: str) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Kripto icin ccxt'den 4h ve 1h veri cek."""
        import ccxt
        
        try:
            exchange = ccxt.binance({"enableRateLimit": True, "options": {"defaultType": "spot"}})
        except Exception:
            exchange = ccxt.binance()
        
        result = {}
        for tf_name, config in TF_CONFIG.items():
            tf = config["ccxt"]
            limit = config["bars"]
            cache_key = f"{symbol}:{tf}"
            
            if cache_key in self._ccxt_cache:
                data = self._ccxt_cache[cache_key]
                result[tf_name] = (data["close"], data["volume"])
                continue
            
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=limit)
                if len(ohlcv) >= 100:
                    close = np.array([c[4] for c in ohlcv], dtype=float)
                    volume = np.array([c[5] for c in ohlcv], dtype=float)
                    result[tf_name] = (close, volume)
                    self._ccxt_cache[cache_key] = {"close": close, "volume": volume, "ts": time.time()}
                time.sleep(0.15)
            except Exception as e:
                logger.debug(f"ccxt {symbol} {tf}: {e}")
                continue
        
        return result
    
    def _fetch_yahoo_ltf(self, symbol: str) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """BIST/US hisseleri icin Yahoo'dan 1h veri cek."""
        import yfinance as yf
        
        result = {}
        
        # Yahoo'da 4h yok, 1h var (son 1 ay)
        try:
            data = yf.download(symbol, period="1mo", interval="1h",
                              progress=False, auto_adjust=True, ignore_tz=True)
            if data is not None and not data.empty:
                close_col = ('Close', symbol) if isinstance(data.columns, type(data.columns)) and isinstance(data.columns.get_loc(('Close', symbol)), int) else 'Close'
                vol_col = ('Volume', symbol) if isinstance(data.columns, type(data.columns)) and isinstance(data.columns.get_loc(('Volume', symbol)), int) else 'Volume'
                
                # Fix for single-symbol download (no MultiIndex)
                if 'Close' in data.columns and isinstance(data.columns, pd.Index):
                    close = data['Close'].values.astype(float)
                    volume = data['Volume'].values.astype(float)
                else:
                    close = data[close_col].values.astype(float)
                    volume = data[vol_col].values.astype(float)
                
                mask = ~(np.isnan(close) | np.isnan(volume))
                close = close[mask]
                volume = volume[mask]
                
                if len(close) >= 100:
                    # 1h verisini kaydet
                    result["h1"] = (close, volume)
                    
                    # 4h'ye resample et (ortalama ~4 bar = 1 bar)
                    if len(close) >= 400:
                        n_4h = len(close) // 4
                        close_4h = close[-n_4h*4:].reshape(-1, 4).mean(axis=1)
                        volume_4h = volume[-n_4h*4:].reshape(-1, 4).sum(axis=1)
                        result["h4"] = (close_4h, volume_4h)
        except Exception as e:
            logger.debug(f"yahoo ltf {symbol}: {e}")
        
        return result
    
    def clear_cache(self):
        """LTF cache'ini temizle."""
        self._ccxt_cache.clear()
        logger.info("MTF cache temizlendi")


def add_mtf_to_alert(symbol: str, signal: SignalResult, market_type: str,
                     validator: Optional[MTFValidator] = None) -> str:
    """
    MTF dogrulama sonucunu Telegram mesajina eklemek icin kisa bir satir uretir.
    
    Ornek cikti:
      MTF: %72 dogrulandi (4h: D1+D2+D6, 1h: D1+D6)
      MTF: %23 VETO (1h teyit yok)
    """
    if validator is None:
        validator = MTFValidator()
    
    result = validator.validate(symbol, signal, market_type)
    
    if not result.is_validated:
        return f"MTF: %{result.confidence*100:.0f} VETO"
    
    # Basariliysa hangi TF'lerin onayladigini goster
    parts = []
    for tf_name, al in result.alignments.items():
        aligned = []
        if al.div1_aligned: aligned.append("D1")
        if al.div2_aligned: aligned.append("D2")
        if al.div6_aligned: aligned.append("D6")
        if aligned:
            parts.append(f"{tf_name}: {'+'.join(aligned)}")
    
    detail = ", ".join(parts[:2]) if parts else "onaylandi"
    return f"MTF: %{result.confidence*100:.0f} ({detail})"
