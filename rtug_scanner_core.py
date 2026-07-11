"""
RTUG BREAKOUT ALERT — Scanner Core Engine
==========================================
Pine Script'teki OBV divergence mantığının Python implementasyonu.
Tüm hisse senetlerini tarayıp breakout sinyali verenleri bulur.

Kullanım:
    from rtug_scanner_core import RTUGSignalEngine, BreakoutType
    
    engine = RTUGSignalEngine()
    result = engine.analyze(close_prices, volume_prices)
    print(result.breakout_type, result.bull_count)
"""

from typing import List, Optional, NamedTuple
import numpy as np
import pandas as pd


# ─── Sinyal Tipleri ──────────────────────────────────────
class BreakoutType:
    NONE           = ""
    BULLISH        = "BULLISH_BREAKOUT"
    BEARISH        = "BEARISH_BREAKOUT"
    SUPER_BULLISH  = "SUPER_BULLISH"
    SUPER_BEARISH  = "SUPER_BEARISH"
    CROSS_UP       = "DIV6_CROSS_UP"
    CROSS_DOWN     = "DIV6_CROSS_DOWN"
    MOMENTUM_BULL  = "MOMENTUM_BULL"
    MOMENTUM_BEAR  = "MOMENTUM_BEAR"
    # 🎯 Color Surround Pattern'leri
    BULL_SURROUND      = "BULLISH_SURROUND"       # Mor+Mavi Kırmızıyı sardı
    BEAR_SURROUND      = "BEARISH_SURROUND"       # Pembe+Kahve Kırmızıyı sardı
    STRONG_BULL_SUR    = "STRONG_BULLISH_SURROUND"  # Tam boğa sarma
    STRONG_BEAR_SUR    = "STRONG_BEARISH_SURROUND"  # Tam ayı sarma
    DEEP_BULL_SUR      = "DEEP_BULLISH_SURROUND"    # 4/5 bullish surround
    DEEP_BEAR_SUR      = "DEEP_BEARISH_SURROUND"    # 4/5 bearish surround
    REV_CIRCLE_BULL    = "REVERSE_CIRCLE_BULLISH"   # Reverse daireler boğa
    REV_CIRCLE_BEAR    = "REVERSE_CIRCLE_BEARISH"   # Reverse daireler ayı
    # 🔥 YENI: Triple Agreement (Uclu Uyum Pattern'leri)
    TRIPLE_BULL        = "TRIPLE_BULLISH"           # Div1+Div2+Div6 hepsi pozitif (Mor+Kirmizi+Mavi)
    TRIPLE_BEAR        = "TRIPLE_BEARISH"           # Div1+Div2+Div6 hepsi negatif (Pembe+Turuncu+Kahve)


class SignalResult(NamedTuple):
    """Bir sembol için sinyal analiz sonucu."""
    ticker: str
    breakout_type: str
    bull_count: int
    bear_count: int
    obv_norm: float
    div1: float
    div2: float
    div3: float
    div5: float
    div6: float
    score: float  # 0-100 conviction score
    price: float
    signal_name: str = ""
    # 🎯 Color Surround ek alanları
    surround_type: str = ""          # Hangi surround patterni
    surround_strength: int = 0       # 0-5 arası güç
    reverse_bull: int = 0            # Reverse divergance bullish count
    reverse_bear: int = 0            # Reverse divergance bearish count
    div_directions: int = 0          # Kaç divergence bullish (0-5)
    
    @property
    def has_signal(self) -> bool:
        return bool(self.breakout_type)
    
    @property
    def direction_icons(self) -> str:
        """Divergence yönlerini oklar olarak döndürür."""
        d = lambda v: "UP" if v > 0 else "DN"
        return f"D1:{d(self.div1)} D2:{d(self.div2)} D3:{d(self.div3)} D5:{d(self.div5)} D6:{d(self.div6)}"
    
    @property
    def surround_icons(self) -> str:
        """Surround patternini renk kodlu göster."""
        if not self.surround_type:
            return ""
        icons = {
            BreakoutType.BULL_SURROUND: "[Mor+Mavi Kirmiziyi Sardi]",
            BreakoutType.BEAR_SURROUND: "[Pembe+Kahve Kirmiziyi Sardi]",
            BreakoutType.STRONG_BULL_SUR: "[GUICLU] Mor+Mavi Kirmizi+Pembeyi Sardi",
            BreakoutType.STRONG_BEAR_SUR: "[GUICLU] Pembe+Kahve Kirmizi+Pembeyi Sardi",
            BreakoutType.DEEP_BULL_SUR: f"[Derin {self.div_directions}/5 bull]",
            BreakoutType.DEEP_BEAR_SUR: f"[Derin {5-self.div_directions}/5 bear]",
            BreakoutType.REV_CIRCLE_BULL: f"[Ters daire {self.reverse_bull}/5 bull]",
            BreakoutType.REV_CIRCLE_BEAR: f"[Ters daire {self.reverse_bear}/5 bear]",
        }
        return icons.get(self.surround_type, self.surround_type)
    
    @property
    def color_status(self) -> str:
        """Renk durumunu göster (mor/kirmizi/mavi vb)."""
        d1_c = "MOR UP" if self.div1 > 0 else "PEMBE DN"
        d2_c = "KIRMIZI UP" if self.div2 > 0 else "TURUNCU DN"
        d6_c = "MAVI UP" if self.div6 > 0 else "KAHVE DN"
        return f"D1:{d1_c} | D2:{d2_c} | D6:{d6_c}"


# ─── OBV Divergence Engine ───────────────────────────────
class RTUGSignalEngine:
    """
    Pine Script'teki RTUG BREAKOUT ALERT mantığının Python versiyonu.
    
    OBV (On-Balance Volume) hesaplar, RMA (Wilder's Moving Average) 
    ile fast/slow divergence'ları çıkarır, breakout sinyali üretir.
    """
    
    def __init__(self):
        # Varsayılan parametreler (Pine Script input() değerleri)
        self.main_period = 20
        self.obv_norm_len = 200
        self.bo_threshold = 4  # Min divergence count for breakout
        
        # Divergence periodları
        self.div_periods = {
            'div1': (100, 20),
            'div2': (70, 15),
            'div3': (50, 20),
            'div5': (15, 5),
            'div6': (8, 3),
        }
        
        # Reverse periodları
        self.rev_periods = {
            'div1': (20, 100),
            'div2': (15, 70),
            'div3': (20, 50),
            'div5': (5, 15),
            'div6': (3, 8),
        }
        
        # 🎯 Color Surround eşikleri
        self.surround_min_div_count = 2  # En az bu kadar divergence surround olmalı
    
    def _rma(self, series: np.ndarray, length: int) -> np.ndarray:
        """Wilder's Moving Average (RMA) — Pine Script ta.rma() ile aynı."""
        alpha = 1.0 / length
        rma = np.zeros_like(series)
        rma[:length] = np.nan
        if len(series) > length:
            rma[length] = np.mean(series[:length])
            for i in range(length + 1, len(series)):
                rma[i] = alpha * series[i] + (1 - alpha) * rma[i-1]
        return rma
    
    def _cum_obv(self, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """OBV (On-Balance Volume) hesaplama — Pine Script ta.cum() ile aynı."""
        chg = np.diff(close, prepend=close[0])
        signs = np.sign(chg)  # +1 up, -1 down, 0 no change
        obv = np.cumsum(signs * volume)
        return obv
    
    def _obv_norm_pine(self, obv_raw: np.ndarray, length: int) -> np.ndarray:
        """
        OBV'yi normalize et — Pine Script'teki ile aynı:
        obv_n = (obv1 - ta.lowest(obv1, len_main)) / 
                (ta.highest(obv1, len_main) - ta.lowest(obv1, len_main) + 1e-9) * 2 - 1
        """
        import pandas as pd
        s = pd.Series(obv_raw)
        lo = s.rolling(length, min_periods=1).min().values
        hi = s.rolling(length, min_periods=1).max().values
        result = (obv_raw - lo) / (hi - lo + 1e-9) * 2 - 1
        return result
    
    def _divergence(self, obv: np.ndarray, fast: int, slow: int) -> np.ndarray:
        """Divergence = RMA(fast) - RMA(slow) — Pine Script'teki ile aynı."""
        fast_rma = self._rma(obv, fast)
        slow_rma = self._rma(obv, slow)
        return fast_rma - slow_rma
    
    def analyze(self, close: np.ndarray, volume: np.ndarray) -> SignalResult:
        """
        Ana analiz fonksiyonu — Pine Script ile birebir aynı mantık.
        
        Args:
            close: Kapanış fiyatları (numpy array, en az 200 bar)
            volume: Hacim verileri (numpy array)
            
        Returns:
            SignalResult: Sinyal analiz sonucu
        """
        # OBV hesapla (tek sefer, tüm divergence'lar aynı OBV'yi kullanır)
        obv = self._cum_obv(close, volume)
        
        # OBV normalize (Pine Script'teki gibi)
        obv_norm_full = self._obv_norm_pine(obv, self.main_period)
        obv_norm_last = obv_norm_full[-1] if not np.isnan(obv_norm_full[-1]) else 0
        obv_norm_prev = obv_norm_full[-2] if len(obv_norm_full) > 1 and not np.isnan(obv_norm_full[-2]) else 0
        
        # Divergence'ları hesapla (hepsi aynı OBV'yi kullanır)
        div1_full = self._divergence(obv, self.div_periods['div1'][0], self.div_periods['div1'][1])
        div2_full = self._divergence(obv, self.div_periods['div2'][0], self.div_periods['div2'][1])
        div3_full = self._divergence(obv, self.div_periods['div3'][0], self.div_periods['div3'][1])
        div5_full = self._divergence(obv, self.div_periods['div5'][0], self.div_periods['div5'][1])
        div6_full = self._divergence(obv, self.div_periods['div6'][0], self.div_periods['div6'][1])
        
        # Son değerler
        d1 = float(div1_full[-1]) if not np.isnan(div1_full[-1]) else 0
        d2 = float(div2_full[-1]) if not np.isnan(div2_full[-1]) else 0
        d3 = float(div3_full[-1]) if not np.isnan(div3_full[-1]) else 0
        d5 = float(div5_full[-1]) if not np.isnan(div5_full[-1]) else 0
        d6 = float(div6_full[-1]) if not np.isnan(div6_full[-1]) else 0
        
        # ─── Reverse Divergences (daireler) ───
        div1r_full = self._divergence(obv, self.rev_periods['div1'][0], self.rev_periods['div1'][1])
        div2r_full = self._divergence(obv, self.rev_periods['div2'][0], self.rev_periods['div2'][1])
        div3r_full = self._divergence(obv, self.rev_periods['div3'][0], self.rev_periods['div3'][1])
        div5r_full = self._divergence(obv, self.rev_periods['div5'][0], self.rev_periods['div5'][1])
        div6r_full = self._divergence(obv, self.rev_periods['div6'][0], self.rev_periods['div6'][1])
        
        d1r = float(div1r_full[-1]) if not np.isnan(div1r_full[-1]) else 0
        d2r = float(div2r_full[-1]) if not np.isnan(div2r_full[-1]) else 0
        d3r = float(div3r_full[-1]) if not np.isnan(div3r_full[-1]) else 0
        d5r = float(div5r_full[-1]) if not np.isnan(div5r_full[-1]) else 0
        d6r = float(div6r_full[-1]) if not np.isnan(div6r_full[-1]) else 0
        
        # Önceki değerler (momentum/mav cross için)
        d1_prev = float(div1_full[-2]) if len(div1_full) > 1 and not np.isnan(div1_full[-2]) else 0
        d6_prev = float(div6_full[-2]) if len(div6_full) > 1 and not np.isnan(div6_full[-2]) else 0
        
        # Divergence pozisyonları (Pine Script'teki gibi: > 0 pozitif, < 0 negatif)
        divs = [d1, d2, d3, d5, d6]
        bull_count = sum(1 for v in divs if v > 0)
        bear_count = sum(1 for v in divs if v < 0)
        
        # Divergence momentum (Pine Script'teki div*_bull = div* > 0 and div* > div*[1])
        d1_bull = d1 > 0 and d1 > d1_prev
        d6_bull = d6 > 0 and d6 > d6_prev
        
        # OBV momentum (Pine Script: obv_bull = obv_norm > obv_norm[1])
        obv_bull = obv_norm_last > obv_norm_prev
        obv_strong = abs(obv_norm_last) > 0.3
        
        # Breakout tespiti
        breakout = BreakoutType.NONE
        
        if bull_count == 5 and obv_strong and obv_norm_last > 0:
            breakout = BreakoutType.SUPER_BULLISH
        elif bear_count == 5 and obv_strong and obv_norm_last < 0:
            breakout = BreakoutType.SUPER_BEARISH
        elif bull_count >= self.bo_threshold and obv_bull:
            breakout = BreakoutType.BULLISH
        elif bear_count >= self.bo_threshold and not obv_bull:
            breakout = BreakoutType.BEARISH
        
        # SADECE ana breakout yoksa div6 cross kontrol et
        # (cross, breakout'u ezmemeli)
        if breakout == BreakoutType.NONE:
            div6_cross_up = d6 > 0 and d6_prev <= 0 and d6_prev != 0
            div6_cross_dn = d6 < 0 and d6_prev >= 0 and d6_prev != 0
            
            if div6_cross_up:
                breakout = BreakoutType.CROSS_UP
            elif div6_cross_dn:
                breakout = BreakoutType.CROSS_DOWN
        
        # ═════════════════════════════════════════════════════
        # 🎯 COLOR SURROUND PATTERN DETECTION
        # ═════════════════════════════════════════════════════
        
        # Renk Yönleri:
        # Div1: Purple(>0) / Pink(<0) — Uzun trend
        # Div2: Red(>0) / Orange(<0) — Orta trend
        # Div6: Blue(>0) / Brown(<0) — Kısa trend
        d1_bull = d1 > 0;  d1_bear = d1 < 0
        d2_bull = d2 > 0;  d2_bear = d2 < 0
        d6_bull = d6 > 0;  d6_bear = d6 < 0
        d5_bull = d5 > 0;  d5_bear = d5 < 0
        
        # Kaç divergence bullish?
        div_directions = sum([d1_bull, d2_bull, d3 > 0, d5_bull, d6_bull])
        
        # Reverse divergence yönleri
        rev_bull_count = sum([d1r > 0, d2r > 0, d3r > 0, d5r > 0, d6r > 0])
        rev_bear_count = 5 - rev_bull_count
        
        surround_type = ""
        surround_strength = 0
        has_surround = False
        
        # --- PATTERN 1: Bullish Surround (Mor+Mavi Kırmızıyı Sardı) ---
        # Div1(Purple)>0 ve Div6(Blue)>0 ama Div2(Red)<0
        bull_surround_1 = d1_bull and d6_bull and d2_bear
        bull_surround_3 = d1_bull and d6_bull and d2_bear and d5_bear  # Tam sarma
        bull_surround_4 = d1_bull and d6_bull and obv_bull             # OBV onaylı
        
        if bull_surround_3:
            surround_type = BreakoutType.STRONG_BULL_SUR
            surround_strength = 4
            has_surround = True
        elif bull_surround_1:
            surround_type = BreakoutType.BULL_SURROUND
            surround_strength = 2
            has_surround = True
        
        # --- PATTERN 2: Bearish Surround (Pembe+Kahve Kırmızıyı Sardı) ---
        bear_surround_1 = d1_bear and d6_bear and d2_bull
        bear_surround_3 = d1_bear and d6_bear and d2_bull and d5_bull
        bear_surround_4 = d1_bear and d6_bear and not obv_bull
        
        if bear_surround_3:
            surround_type = BreakoutType.STRONG_BEAR_SUR
            surround_strength = 4
            has_surround = True
        elif bear_surround_1:
            surround_type = BreakoutType.BEAR_SURROUND
            surround_strength = 2
            has_surround = True
        
        # --- PATTERN 3: Deep Surround (4/5 consensus) ---
        if not has_surround:
            if div_directions >= 4 and (d2_bear or d5_bear):
                surround_type = BreakoutType.DEEP_BULL_SUR
                surround_strength = 3
                has_surround = True
            elif div_directions <= 1 and (d2_bull or d5_bull):
                surround_type = BreakoutType.DEEP_BEAR_SUR
                surround_strength = 3
                has_surround = True
        
        # --- PATTERN 4: Triple Agreement (Uclu Uyum) ---
        # Div1+Div2+Div6 hepsi ayni yonde (kisa/orta/uzun trend uyumu)
        # NOT: Bu, Reverse Circle'dan ONCE kontrol edilir cunku daha spesifik
        if not has_surround:
            if d1_bull and d2_bull and d6_bull:  # Mor+Kirmizi+Mavi hepsi UP
                surround_type = BreakoutType.TRIPLE_BULL
                surround_strength = 3
                has_surround = True
            elif d1_bear and d2_bear and d6_bear:  # Pembe+Turuncu+Kahve hepsi DN
                surround_type = BreakoutType.TRIPLE_BEAR
                surround_strength = 3
                has_surround = True
        
        # --- PATTERN 5: Reverse Circle Surround ---
        if not has_surround:
            rev_diff = rev_bull_count - bull_count
            if rev_diff >= 3:  # Reverse daireler çizgilerden çok daha boğa
                surround_type = BreakoutType.REV_CIRCLE_BULL
                surround_strength = rev_diff
                has_surround = True
            elif rev_diff <= -3:  # Reverse daireler çizgilerden çok daha ayı
                surround_type = BreakoutType.REV_CIRCLE_BEAR
                surround_strength = abs(rev_diff)
                has_surround = True
        
        # Eğer surround patterni bulunduysa, breakout'u ez
        if has_surround and breakout == BreakoutType.NONE:
            breakout = surround_type
        elif has_surround and breakout != BreakoutType.NONE:
            # Her iki sinyal de varsa, daha güçlü olanı kullan
            if surround_strength >= 3:
                breakout = surround_type
        
        # Conviction score (0-100) — Pine Script'teki Ultimate Scanner mantığı
        score = 50.0
        score += bull_count * 8
        score -= bear_count * 5
        if obv_bull: score += 10
        if obv_strong and bull_count >= 4: score += 10
        if d6_bull: score += 8
        if has_surround: score += surround_strength * 5  # Surround bonusu
        score = max(0, min(100, score))
        
        # Sinyal adı
        signal_names = {
            BreakoutType.SUPER_BULLISH: "SÜPER BOĞA",
            BreakoutType.SUPER_BEARISH: "SÜPER AYI",
            BreakoutType.BULLISH: "BOĞA KIRILIMI",
            BreakoutType.BEARISH: "AYI KIRILIMI",
            BreakoutType.CROSS_UP: "HIZLI YUKARI KESİŞ",
            BreakoutType.CROSS_DOWN: "HIZLI AŞAĞI KESİŞ",
            BreakoutType.MOMENTUM_BULL: "MOMENTUM BOĞA",
            BreakoutType.MOMENTUM_BEAR: "MOMENTUM AYI",
            # 🎯 Surround pattern adları
            BreakoutType.BULL_SURROUND: "BOGA SARMA [Purple+Blue>Red]",
            BreakoutType.BEAR_SURROUND: "AYI SARMA [Pink+Brown>Red]",
            BreakoutType.STRONG_BULL_SUR: "GUCLU BOGA SARMA",
            BreakoutType.STRONG_BEAR_SUR: "GUCLU AYI SARMA",
            BreakoutType.DEEP_BULL_SUR: "DERIN BOGA",
            BreakoutType.DEEP_BEAR_SUR: "DERIN AYI",
            BreakoutType.REV_CIRCLE_BULL: "TERS DAIRE BOGA",
            BreakoutType.REV_CIRCLE_BEAR: "TERS DAIRE AYI",
            # 🔥 Triple Agreement
            BreakoutType.TRIPLE_BULL: "UCLU BOGA [Mor+Kirmizi+Mavi UP]",
            BreakoutType.TRIPLE_BEAR: "UCLU AYI [Pembe+Turuncu+Kahve DN]",
        }
        
        return SignalResult(
            ticker="",
            breakout_type=breakout,
            bull_count=bull_count,
            bear_count=bear_count,
            obv_norm=round(obv_norm_last, 4),
            div1=round(d1, 2),
            div2=round(d2, 2),
            div3=round(d3, 2),
            div5=round(d5, 2),
            div6=round(d6, 2),
            score=round(score, 1),
            price=float(close[-1]),
            signal_name=signal_names.get(breakout, ""),
            surround_type=surround_type,
            surround_strength=surround_strength,
            reverse_bull=rev_bull_count,
            reverse_bear=rev_bear_count,
            div_directions=div_directions
        )
    
    def get_conviction(self, close: np.ndarray, volume: np.ndarray) -> float:
        """Sadece conviction skoru döndürür (hızlı tarama için)."""
        result = self.analyze(close, volume)
        return result.score


# ─── Test ─────────────────────────────────────────────────
if __name__ == "__main__":
    # Test: rastgele veri üret
    import numpy as np
    
    np.random.seed(42)
    bars = 300
    close = 100 + np.cumsum(np.random.randn(bars) * 0.5)
    volume = np.random.randint(100000, 10000000, bars)
    
    engine = RTUGSignalEngine()
    result = engine.analyze(close, volume)
    
    print("=== RTUG Scanner Core Test ===")
    print(f"Breakout: {result.breakout_type or 'YOK'}")
    print(f"Bull: {result.bull_count}/5 | Bear: {result.bear_count}/5")
    print(f"OBV: {result.obv_norm}")
    print(f"Div1: {result.div1} | Div2: {result.div2} | Div3: {result.div3} | Div5: {result.div5} | Div6: {result.div6}")
    print(f"Score: {result.score}/100")
    print(f"Price: {result.price:.2f}")
    print(f"Directions: {result.direction_icons}")
    # SURROUND test
    if result.surround_type:
        print(f"[SURROUND] {result.surround_icons}")
        print(f"   Strength: {result.surround_strength}/5")
        print(f"   Colors: {result.color_status}")
        print(f"   Reverse Bull: {result.reverse_bull}/5 | Bear: {result.reverse_bear}/5")
    print("[OK] Core engine OK")
