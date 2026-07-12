"""
RTUG BACKTEST ENGINE v1 — Pattern Dogrulama + Strateji Olusturma
================================================================
Walk-forward backtest ile pattern'lerin gerçek breakout öncesi mi
sonrasi mi oldugunu tespit eder, CVD/order-flow analizi ekler,
precision/recall hesaplar.

KULLANIM:
    python rtug_backtest.py --symbols 10 --pattern CANONICAL_FULL_BULL_BREAKOUT
    python rtug_backtest.py --all --breach 0.05   --lookahead 10
    python rtug_backtest.py --report
"""

import os, sys, json, time, math, copy
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from collections import defaultdict

import numpy as np
import pandas as pd

from rtug_scanner_core import RTUGSignalEngine, SignalResult, BreakoutType
from rtug_pattern_memory import PatternMemory, IndicatorState, MatchResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "logs" / "backtest.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("rtug-backtest")

BT_DIR = Path(__file__).parent / ".rtug-backtest"
BT_DIR.mkdir(exist_ok=True)

# ─── Volume Analysis (CVD + Order Flow) ───────────────────

class VolumeAnalyzer:
    """Extended volume analysis beyond OBV."""

    @staticmethod
    def cvd(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Cumulative Volume Delta — tick-based volume direction."""
        chg = np.diff(close, prepend=close[0])
        direction = np.sign(chg)
        cvd_series = np.cumsum(direction * volume)
        return cvd_series

    @staticmethod
    def cvd_divergence(cvd: np.ndarray, close: np.ndarray, period: int = 20) -> float:
        """CVD vs price divergence: positive = bullish divergence."""
        if len(cvd) < period:
            return 0.0
        cvd_slope = (cvd[-1] - cvd[-period]) / max(abs(cvd[-period]), 1)
        price_slope = (close[-1] - close[-period]) / max(close[-period], 0.01)
        if price_slope > 0 and cvd_slope <= 0:
            return -abs(cvd_slope)
        elif price_slope <= 0 and cvd_slope > 0:
            return abs(cvd_slope)
        return 0.0

    @staticmethod
    def volume_profile(close: np.ndarray, volume: np.ndarray, bins: int = 10):
        """Volume profile — VAH, VAL, POC."""
        lo, hi = min(close), max(close)
        bin_edges = np.linspace(lo, hi, bins + 1)
        vol_by_price = np.zeros(bins)
        for i in range(len(close)):
            idx = min(bins - 1, max(0, int((close[i] - lo) / (hi - lo + 1e-9) * bins)))
            vol_by_price[idx] += volume[i]
        poc_idx = np.argmax(vol_by_price)
        val_idx = min(bins - 1, max(0, poc_idx - 1))
        vah_idx = min(bins - 1, poc_idx + 1)
        return {
            "poc": bin_edges[poc_idx],
            "val": bin_edges[val_idx],
            "vah": bin_edges[vah_idx],
            "volume_distribution": vol_by_price.tolist()
        }

    @staticmethod
    def order_flow_imbalance(close: np.ndarray, volume: np.ndarray, period: int = 5) -> float:
        """Order flow imbalance proxy: (buy_vol - sell_vol) / total_vol"""
        chg = np.diff(close[-period-1:], prepend=close[-period-1])
        vol = volume[-period-1:]
        buy_vol = sum(v for c, v in zip(chg, vol) if c > 0)
        sell_vol = sum(v for c, v in zip(chg, vol) if c < 0)
        total = buy_vol + sell_vol
        if total == 0:
            return 0.0
        return (buy_vol - sell_vol) / total

    @staticmethod
    def volume_expansion(volume: np.ndarray, short: int = 5, long: int = 20) -> float:
        """Volume expansion ratio: recent avg / longer avg."""
        if len(volume) < long:
            return 1.0
        recent = np.mean(volume[-short:])
        prior = np.mean(volume[-long:-short]) if len(volume) > long + short else np.mean(volume[:-short])
        if prior == 0:
            return 1.0
        return recent / prior

    @staticmethod
    def price_volume_divergence(close: np.ndarray, volume: np.ndarray, period: int = 10) -> str:
        """Price-volume divergence detection."""
        if len(close) < period:
            return "neutral"
        price_trend = close[-1] - close[-period]
        vol_trend = np.mean(volume[-period:]) - np.mean(volume[-period*2:-period])
        if price_trend > 0 and vol_trend <= 0:
            return "bearish_divergence"
        elif price_trend <= 0 and vol_trend > 0:
            return "bullish_divergence"
        return "neutral"

    @staticmethod
    def analyze_all(close: np.ndarray, volume: np.ndarray) -> dict:
        """Run all volume analysis and return structured results."""
        cvd_series = VolumeAnalyzer.cvd(close, volume)
        vp = VolumeAnalyzer.volume_profile(close, volume)
        return {
            "obv_norm": float(np.nan_to_num(
                (close[-1] - close.min()) / (close.max() - close.min() + 1e-9) * 2 - 1, 0)),
            "cvd": float(cvd_series[-1]) if len(cvd_series) > 0 else 0.0,
            "cvd_divergence": VolumeAnalyzer.cvd_divergence(cvd_series, close),
            "order_flow_imbalance": VolumeAnalyzer.order_flow_imbalance(close, volume),
            "volume_expansion": VolumeAnalyzer.volume_expansion(volume),
            "price_volume_divergence": VolumeAnalyzer.price_volume_divergence(close, volume),
            "volume_profile_poc": vp["poc"],
            "volume_profile_val": vp["val"],
            "volume_profile_vah": vp["vah"],
        }


# ─── Walk-Forward Backtest ────────────────────────────────

class BacktestResult:
    """Single backtest result for one symbol + pattern combination."""

    def __init__(self, symbol: str, pattern_name: str):
        self.symbol = symbol
        self.pattern_name = pattern_name
        self.total_signals = 0
        self.true_positives = 0
        self.false_positives = 0
        self.pattern_before_breakout = 0  # Signal came BEFORE price move
        self.pattern_after_breakout = 0   # Signal came AFTER price move started
        self.avg_lead_bars = 0.0          # Avg bars signal was early
        self.lead_bars_list: List[int] = []
        self.false_positives_list: List[dict] = []
        self.true_positives_list: List[dict] = []
        self.pattern_type_counts: Dict[str, int] = defaultdict(int)
        self.volume_analysis_list: List[dict] = []
        self.final_price = 0.0
        self.start_price = 0.0

    @property
    def precision(self) -> float:
        if self.total_signals == 0:
            return 0.0
        return self.true_positives / self.total_signals

    @property
    def timing_score(self) -> float:
        """0.0 = always after breakout, 1.0 = always before breakout."""
        if self.true_positives == 0:
            return 0.0
        return self.pattern_before_breakout / self.true_positives

    @property
    def avg_return_per_signal(self) -> float:
        if not self.true_positives_list:
            return 0.0
        returns = [t.get("return_pct", 0) for t in self.true_positives_list]
        return sum(returns) / len(returns)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "pattern": self.pattern_name,
            "total_signals": self.total_signals,
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "precision": round(self.precision, 4),
            "pattern_before_breakout": self.pattern_before_breakout,
            "pattern_after_breakout": self.pattern_after_breakout,
            "timing_score": round(self.timing_score, 4),
            "avg_lead_bars": round(self.avg_lead_bars, 1),
            "avg_return_per_signal": round(self.avg_return_per_signal, 4),
            "pattern_types": dict(self.pattern_type_counts),
        }


class BacktestEngine:
    """
    Walk-forward backtest engine.
    
    For each symbol:
      1. Walk through historical data bar by bar
      2. At each bar, compute scanner signal + pattern match
      3. Look ahead N bars for price breakout
      4. Classify as TP/FP
      5. Track timing (before/after breakout)
    """

    def __init__(self, memory: PatternMemory, engine: RTUGSignalEngine = None):
        self.memory = memory
        self.engine = engine or RTUGSignalEngine()
        self.min_bars = 150
        self.results: Dict[str, BacktestResult] = {}
        
        # Default thresholds
        self.pattern_threshold = 0.70
        self.breach_pct = 0.05      # 5% price move = breakout
        self.lookahead_bars = 10    # Look 10 bars ahead for breakout
        self.entry_window = 5       # Pattern must form within 5 bars of breakout
        
    def classify_breakout(self, close: np.ndarray, signal_idx: int, 
                          lookahead: int, breach_pct: float) -> Tuple[bool, int, float]:
        """
        Check if a breakout happened within lookahead bars after signal_idx.
        
        Returns:
            (is_breakout, lead_bars, max_return_pct)
        """
        if signal_idx + lookahead >= len(close):
            return False, 0, 0.0
        
        entry_price = close[signal_idx]
        if entry_price <= 0:
            return False, 0, 0.0
        
        max_future = max(close[signal_idx:signal_idx + lookahead + 1])
        max_return = (max_future - entry_price) / entry_price
        
        for offset in range(1, lookahead + 1):
            bar_return = (close[signal_idx + offset] - entry_price) / entry_price
            if bar_return >= breach_pct:
                return True, offset, max_return
        
        return False, 0, max_return

    def run_symbol(self, symbol: str, close: np.ndarray, volume: np.ndarray,
                   breach_pct: float = None, lookahead: int = None) -> Optional[BacktestResult]:
        """Run walk-forward backtest on one symbol."""
        if breach_pct is None:
            breach_pct = self.breach_pct
        if lookahead is None:
            lookahead = self.lookahead_bars
        
        if len(close) < self.min_bars or len(volume) < self.min_bars:
            return None
        
        result = BacktestResult(symbol, "all_patterns")
        result.start_price = float(close[-lookahead])
        result.final_price = float(close[-1])
        
        # Walk through each bar (start at min_bars to have enough data)
        # Step by 3 bars to keep computation reasonable
        step = max(1, len(close) // 200)
        
        for i in range(self.min_bars, len(close) - lookahead - 1, step):
            try:
                window_close = close[:i + 1]
                window_vol = volume[:i + 1]
                
                signal = self.engine.analyze(window_close, window_vol)
                if not signal or not signal.breakout_type:
                    continue
                
                state = IndicatorState()
                state.div1 = signal.div1; state.div2 = signal.div2
                state.div3 = signal.div3; state.div5 = signal.div5
                state.div6 = signal.div6; state.obv_norm = signal.obv_norm
                state.div1_dir = 1 if signal.div1 > 0 else (-1 if signal.div1 < 0 else 0)
                state.div2_dir = 1 if signal.div2 > 0 else (-1 if signal.div2 < 0 else 0)
                state.div3_dir = 1 if signal.div3 > 0 else (-1 if signal.div3 < 0 else 0)
                state.div5_dir = 1 if signal.div5 > 0 else (-1 if signal.div5 < 0 else 0)
                state.div6_dir = 1 if signal.div6 > 0 else (-1 if signal.div6 < 0 else 0)
                state.obv_dir = 1 if signal.obv_norm > 0 else (-1 if signal.obv_norm < 0 else 0)
                
                # Check pattern match
                match = self.memory.find_best_match(state, min_similarity=self.pattern_threshold)
                if not match or not match.is_match:
                    continue
                
                result.total_signals += 1
                result.pattern_type_counts[match.pattern.name] += 1
                
                # Look ahead for breakout
                is_breakout, lead_bars, max_ret = self.classify_breakout(
                    close, i, lookahead, breach_pct)
                
                # Volume analysis
                vol_analysis = VolumeAnalyzer.analyze_all(window_close, window_vol)
                
                if is_breakout:
                    result.true_positives += 1
                    result.lead_bars_list.append(lead_bars)
                    
                    entry = {"bar": i, "lead_bars": lead_bars, "return_pct": round(max_ret, 4)}
                    
                    if lead_bars <= self.entry_window:
                        result.pattern_before_breakout += 1
                        entry["timing"] = "before_breakout"
                    else:
                        result.pattern_after_breakout += 1
                        entry["timing"] = "after_breakout_started"
                    
                    result.true_positives_list.append(entry)
                    result.volume_analysis_list.append(vol_analysis)
                    
                else:
                    result.false_positives += 1
                    result.false_positives_list.append({
                        "bar": i, "max_return_pct": round(max_ret, 4),
                    })
                    
            except Exception as e:
                continue
        
        if result.total_signals > 0:
            result.avg_lead_bars = (
                sum(result.lead_bars_list) / len(result.lead_bars_list)
            ) if result.lead_bars_list else 0.0
            
            self.results[f"{symbol}:{result.pattern_name}"] = result
        
        return result if result.total_signals > 0 else None

    def run_batch(self, data: Dict[str, Tuple[np.ndarray, np.ndarray]],
                  market_name: str, max_symbols: int = 0) -> List[BacktestResult]:
        """Run backtest on multiple symbols."""
        results = []
        symbols = list(data.keys())
        if max_symbols > 0:
            symbols = symbols[:max_symbols]
        
        for sym in symbols:
            close, volume = data[sym]
            r = self.run_symbol(sym, close, volume)
            if r:
                results.append(r)
        
        self._save_results(results, market_name)
        return results

    def _save_results(self, results: List[BacktestResult], market_name: str):
        """Save backtest results to file."""
        data = {
            "market": market_name,
            "timestamp": datetime.now().isoformat(),
            "total_symbols": len(results),
            "results": [r.to_dict() for r in results]
        }
        with open(BT_DIR / f"bt_{market_name.lower().replace(' ','_')}.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def aggregate_report(self) -> dict:
        """Generate aggregate report across all symbols."""
        if not self.results:
            return {"error": "No results to report"}
        
        results = list(self.results.values())
        
        total_signals = sum(r.total_signals for r in results)
        total_tp = sum(r.true_positives for r in results)
        total_fp = sum(r.false_positives for r in results)
        
        symbols_with_matches = sum(1 for r in results if r.total_signals > 0)
        
        # Per-pattern breakdown
        pattern_stats = defaultdict(lambda: {"signals": 0, "tp": 0, "fp": 0, "before": 0, "after": 0})
        for r in results:
            for pname, count in r.pattern_type_counts.items():
                ps = pattern_stats[pname]
                ps["signals"] += count
                ps["tp"] += r.true_positives
                ps["fp"] += r.false_positives
                ps["before"] += r.pattern_before_breakout
                ps["after"] += r.pattern_after_breakout
        
        patterns = {}
        for pname, ps in pattern_stats.items():
            patterns[pname] = {
                "precision": round(ps["tp"] / ps["signals"], 4) if ps["signals"] > 0 else 0,
                "timing_score": round(ps["before"] / ps["tp"], 4) if ps["tp"] > 0 else 0,
                "total_signals": ps["signals"],
                "true_positives": ps["tp"],
                "false_positives": ps["fp"],
            }
        
        overall_precision = total_tp / total_signals if total_signals > 0 else 0
        avg_lead = np.mean([r.avg_lead_bars for r in results if r.lead_bars_list])
        
        # Volume analysis
        all_vol = []
        for r in results:
            all_vol.extend(r.volume_analysis_list)
        
        vol_summary = {}
        if all_vol:
            ofi_vals = [v.get("order_flow_imbalance", 0) for v in all_vol]
            ve_vals = [v.get("volume_expansion", 1) for v in all_vol]
            vol_summary = {
                "avg_order_flow_imbalance": round(np.mean(ofi_vals), 4) if ofi_vals else 0,
                "avg_volume_expansion": round(np.mean(ve_vals), 2) if ve_vals else 1.0,
                "ofi_std": round(np.std(ofi_vals), 4) if len(ofi_vals) > 1 else 0,
            }
        
        # Top symbols
        top_by_tp = sorted(results, key=lambda r: r.true_positives, reverse=True)[:10]
        
        # Candlestick-style stats
        tp_bars = []
        for r in results:
            tp_bars.extend(r.lead_bars_list)
        
        return {
            "summary": {
                "total_symbols_analyzed": len(results),
                "symbols_with_matches": symbols_with_matches,
                "total_signals": total_signals,
                "total_true_positives": total_tp,
                "total_false_positives": total_fp,
                "overall_precision": round(overall_precision, 4),
                "avg_lead_bars": round(avg_lead, 1),
                "avg_return_per_signal": round(
                    np.mean([r.avg_return_per_signal for r in results if r.true_positives > 0]), 4),
            },
            "pattern_breakdown": patterns,
            "volume_analysis": vol_summary,
            "lead_bar_distribution": {
                "mean": float(np.mean(tp_bars)) if tp_bars else 0,
                "median": float(np.median(tp_bars)) if tp_bars else 0,
                "min": int(min(tp_bars)) if tp_bars else 0,
                "max": int(max(tp_bars)) if tp_bars else 0,
            } if tp_bars else {},
            "top_symbols": [
                {"symbol": r.symbol, "tp": r.true_positives, "fp": r.false_positives,
                 "precision": round(r.precision, 4), "timing": round(r.timing_score, 4)}
                for r in top_by_tp
            ],
        }


# ─── Strateji Generator ───────────────────────────────────

def generate_strategy(aggregate: dict, memory: PatternMemory) -> dict:
    """Generate trading strategy based on backtest results."""
    
    patterns = aggregate.get("pattern_breakdown", {})
    summary = aggregate.get("summary", {})
    
    best_patterns = sorted(
        patterns.items(),
        key=lambda x: x[1]["precision"] * 0.6 + x[1].get("timing_score", 0) * 0.4,
        reverse=True
    )
    
    entries = []
    for pname, pstats in best_patterns:
        confidence = "HIGH" if pstats["precision"] > 0.7 else \
                     "MEDIUM" if pstats["precision"] > 0.5 else "LOW"
        
        timing_label = "EARLY" if pstats["timing_score"] > 0.6 else \
                       "ON_TIME" if pstats["timing_score"] > 0.3 else "LATE"
        
        entries.append({
            "pattern": pname,
            "precision": pstats["precision"],
            "timing_score": pstats["timing_score"],
            "confidence": confidence,
            "timing_label": timing_label,
            "signals": pstats["total_signals"],
        })
    
    vol = aggregate.get("volume_analysis", {})
    lead_dist = aggregate.get("lead_bar_distribution", {})
    
    strategy = {
        "generated": datetime.now().isoformat(),
        "pattern_count": len(patterns),
        "overall_precision": summary.get("overall_precision", 0),
        "avg_lead_bars": summary.get("avg_lead_bars", 0),
        "avg_return": summary.get("avg_return_per_signal", 0),
        "entries": entries,
        "recommendations": [],
        "volume_filter": {},
        "entry_exit_rules": {},
    }
    
    # Generate recommendations
    recs = []
    
    best_p = entries[0] if entries else None
    if best_p and best_p["precision"] > 0.6:
        recs.append(f"En iyi pattern: {best_p['pattern']} "
                    f"(precision %{best_p['precision']:.0f}, timing: {best_p['timing_label']})")
    
    if summary.get("overall_precision", 0) > 0.6:
        recs.append("Pattern'ler genel olarak guvenilir — canli ticarete uygun")
    elif summary.get("overall_precision", 0) > 0.4:
        recs.append("Orta guvenilirlik — volume filtresi ile iyilestirilebilir")
    else:
        recs.append("Dusuk guvenilirlik — daha fazla pattern egitimi gerekli")
    
    if vol.get("avg_order_flow_imbalance", 0) > 0.2:
        strategy["volume_filter"] = {
            "use_order_flow_imbalance": True,
            "min_ofi": 0.15,
            "reason": "OFI pattern'lerde yuksenk"
        }
        recs.append(f"Order flow imbalance filtresi ekle (min %{vol.get('avg_order_flow_imbalance', 0)*100:.0f})")
    
    if vol.get("avg_volume_expansion", 1) > 1.3:
        strategy["volume_filter"]["use_volume_expansion"] = True
        strategy["volume_filter"]["min_expansion"] = 1.2
        recs.append("Volume expansion filtresi ekle (min 1.2x)")
    
    median_lead = lead_dist.get("median", 0)
    if median_lead > 0:
        strategy["entry_exit_rules"] = {
            "max_hold_bars": int(median_lead * 2),
            "take_profit_pct": summary.get("avg_return", 0) * 100,
            "stop_loss_pct": max(2.0, summary.get("avg_return", 0) * 50),
        }
        recs.append(f"Optimal hold: {int(median_lead)} bar, TP: %{strategy['entry_exit_rules']['take_profit_pct']:.1f}")
    
    strategy["recommendations"] = recs
    return strategy


# ─── Main CLI ────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="RTUG Backtest Engine")
    parser.add_argument("--symbols", type=int, default=0, help="Max symbol sayisi (0=hepsi)")
    parser.add_argument("--breach", type=float, default=0.05, help="Breakout esigi (%%5)")
    parser.add_argument("--lookahead", type=int, default=10, help="Lookahead bar sayisi")
    parser.add_argument("--threshold", type=float, default=0.70, help="Pattern eslesme threshold")
    parser.add_argument("--bist", action="store_true", help="Sadece BIST")
    parser.add_argument("--us", action="store_true", help="Sadece US")
    parser.add_argument("--crypto", action="store_true", help="Sadece Crypto")
    parser.add_argument("--all", action="store_true", help="Tum piyasalar")
    parser.add_argument("--report", action="store_true", help="Son raporu goster")
    parser.add_argument("--single", type=str, help="Tek sembol test")
    parser.add_argument("--generate-strategy", action="store_true", help="Strateji olustur")
    
    args = parser.parse_args()
    
    memory = PatternMemory()
    engine = RTUGSignalEngine()
    
    if args.report:
        return show_report(memory)
    
    if args.single:
        return run_single(memory, engine, args.single, args.breach, args.lookahead)
    
    if args.generate_strategy:
        return generate_and_save(memory)
    
    # Run backtest
    run_backtest(memory, engine, args)


def run_single(memory: PatternMemory, engine: RTUGSignalEngine,
               symbol: str, breach: float, lookahead: int):
    """Run backtest on a single symbol."""
    from rtug_pattern_monitor import DataProvider
    
    bt = BacktestEngine(memory, engine)
    bt.breach_pct = breach
    bt.lookahead_bars = lookahead
    
    is_crypto = "/" in symbol
    if is_crypto:
        data = DataProvider.from_ccxt([symbol])
    else:
        data = DataProvider.from_yahoo([symbol])
    
    if symbol not in data:
        print(f"Veri alinamadi: {symbol}")
        return
    
    close, volume = data[symbol]
    result = bt.run_symbol(symbol.replace("/USDT", "").replace("/USD", ""), close, volume)
    
    if not result:
        print(f"Hiç pattern eslesmesi bulunamadi: {symbol}")
        return
    
    print(f"\n{'='*60}")
    print(f"BACKTEST: {symbol}")
    print(f"{'='*60}")
    print(f"Toplam sinyal:  {result.total_signals}")
    print(f"True Positive:  {result.true_positives}")
    print(f"False Positive: {result.false_positives}")
    print(f"Precision:      %{result.precision*100:.1f}")
    print(f"Pattern once:   {result.pattern_before_breakout}")
    print(f"Pattern sonra:  {result.pattern_after_breakout}")
    print(f"Timing score:   %{result.timing_score*100:.1f}")
    print(f"Ort lead:       {result.avg_lead_bars:.1f} bar")
    print(f"Ort getiri:     %{result.avg_return_per_signal*100:.2f}")
    print(f"\nPattern tipleri:")
    for pname, count in sorted(result.pattern_type_counts.items(), key=lambda x: -x[1]):
        print(f"  {pname}: {count}")


def run_backtest(memory: PatternMemory, engine: RTUGSignalEngine, args):
    """Run full multi-market backtest."""
    from rtug_pattern_monitor import DataProvider
    
    bt = BacktestEngine(memory, engine)
    bt.breach_pct = args.breach
    bt.lookahead_bars = args.lookahead
    bt.pattern_threshold = args.threshold
    
    all_results = []
    
    markets_to_scan = []
    
    # Hangi piyasalar taranacak?
    scan_all = args.all or not (args.bist or args.us or args.crypto)
    
    if scan_all or args.crypto:
        try:
            from rtug_symbols import get_all_crypto_symbols
            crypto_list = get_all_crypto_symbols() or []
        except:
            crypto_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
        markets_to_scan.append(("Crypto", crypto_list, "ccxt"))
    
    if scan_all or args.bist:
        try:
            from rtug_symbols import BIST_SYMBOLS
        except:
            BIST_SYMBOLS = []
        if BIST_SYMBOLS:
            markets_to_scan.append(("BIST", BIST_SYMBOLS, "yahoo"))
    
    if scan_all or args.us:
        try:
            from rtug_symbols import SP500_SYMBOLS
        except:
            SP500_SYMBOLS = []
        if SP500_SYMBOLS:
            markets_to_scan.append(("US", SP500_SYMBOLS, "yahoo"))
    
    for market_name, symbols, provider_type in markets_to_scan:
        if args.symbols > 0:
            symbols = symbols[:args.symbols]
        
        print(f"\n{'='*60}")
        print(f"TARANIYOR: {market_name} ({len(symbols)} sembol)")
        print(f"{'='*60}")
        
        if provider_type == "ccxt":
            data = DataProvider.from_ccxt(symbols)
        else:
            data = DataProvider.from_yahoo(symbols)
        
        if not data:
            print(f"  Veri alinamadi: {market_name}")
            continue
        
        results = bt.run_batch(data, market_name)
        all_results.extend(results)
        print(f"  {len(results)} sembolde pattern eslesmesi bulundu")
    
    # Aggregate report
    report = bt.aggregate_report()
    
    # Save report
    report_file = BT_DIR / "aggregate_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print("AGREGATE RAPOR")
    print(f"{'='*60}")
    s = report.get("summary", {})
    print(f"Toplam sembol:    {s.get('total_symbols_analyzed', 0)}")
    print(f"Eslesen sembol:   {s.get('symbols_with_matches', 0)}")
    print(f"Toplam sinyal:    {s.get('total_signals', 0)}")
    print(f"True Positive:    {s.get('total_true_positives', 0)}")
    print(f"False Positive:   {s.get('total_false_positives', 0)}")
    print(f"PRECISION:        %{s.get('overall_precision', 0)*100:.1f}")
    print(f"Ort lead:         {s.get('avg_lead_bars', 0):.1f} bar")
    print(f"Ort getiri:       %{s.get('avg_return_per_signal', 0)*100:.2f}")
    
    print(f"\nPattern breakdown:")
    for pname, pstats in report.get("pattern_breakdown", {}).items():
        print(f"  {pname:40s} | TP:{pstats['true_positives']:4d} FP:{pstats['false_positives']:4d} "
              f"| P:%{pstats['precision']*100:.0f} | T:%{pstats['timing_score']*100:.0f}")
    
    v = report.get("volume_analysis", {})
    if v:
        print(f"\nVolume analizi:")
        print(f"  OFI: {v.get('avg_order_flow_imbalance', 0):+.4f}")
        print(f"  Vol Expansion: {v.get('avg_volume_expansion', 1):.2f}x")
    
    ld = report.get("lead_bar_distribution", {})
    if ld:
        print(f"\nLead bar dagilimi:")
        print(f"  Medyan: {ld.get('median', 0):.0f} bar | Min: {ld.get('min', 0)} | Max: {ld.get('max', 0)}")
    
    print(f"\nRapor kaydedildi: {report_file}")
    
    # Auto-generate strategy
    if all_results:
        print(f"\nStrateji olusturuluyor...")
        strategy = generate_strategy(report, memory)
        strategy_file = BT_DIR / "strategy.json"
        with open(strategy_file, "w", encoding="utf-8") as f:
            json.dump(strategy, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print("OLUSTURULAN STRATEJI")
        print(f"{'='*60}")
        for rec in strategy.get("recommendations", []):
            print(f"  → {rec}")
        
        if strategy.get("entry_exit_rules"):
            eer = strategy["entry_exit_rules"]
            print(f"\nGiris/Cikis Kurallari:")
            print(f"  Max hold: {eer.get('max_hold_bars', '?')} bar")
            print(f"  Take profit: %{eer.get('take_profit_pct', 0):.1f}")
            print(f"  Stop loss: %{eer.get('stop_loss_pct', 0):.1f}")
        
        print(f"\nStrateji kaydedildi: {strategy_file}")


def show_report(memory: PatternMemory):
    """Show the latest backtest report."""
    report_file = BT_DIR / "aggregate_report.json"
    if not report_file.exists():
        print("Henuz backtest raporu yok. Once calistirin:")
        print("  python rtug_backtest.py --all")
        return
    
    with open(report_file, "r") as f:
        report = json.load(f)
    
    print(f"\n{'='*60}")
    print("RTUG BACKTEST RAPORU")
    print(f"{'='*60}")
    s = report.get("summary", {})
    print(f"Toplam sembol:    {s.get('total_symbols_analyzed', 0)}")
    print(f"Eslesen sembol:   {s.get('symbols_with_matches', 0)}")
    print(f"Toplam sinyal:    {s.get('total_signals', 0)}")
    print(f"TP/FP:            {s.get('total_true_positives', 0)}/{s.get('total_false_positives', 0)}")
    print(f"PRECISION:        %{s.get('overall_precision', 0)*100:.1f}")
    print(f"Ort lead:         {s.get('avg_lead_bars', 0):.1f} bar")
    print(f"Ort getiri:       %{s.get('avg_return_per_signal', 0)*100:.2f}")
    
    print(f"\nPattern breakdown:")
    for pname, pstats in report.get("pattern_breakdown", {}).items():
        print(f"  {pname:40s} | P:%{pstats['precision']*100:.0f} | T:%{pstats['timing_score']*100:.0f}")


def generate_and_save(memory: PatternMemory):
    """Generate strategy from existing report."""
    report_file = BT_DIR / "aggregate_report.json"
    if not report_file.exists():
        print("Henuz backtest raporu yok.")
        return
    
    with open(report_file, "r") as f:
        report = json.load(f)
    
    strategy = generate_strategy(report, memory)
    strategy_file = BT_DIR / "strategy.json"
    with open(strategy_file, "w", encoding="utf-8") as f:
        json.dump(strategy, f, indent=2, ensure_ascii=False)
    
    print(f"Strateji olusturuldu: {strategy_file}")
    print(f"\nTavsiyeler:")
    for rec in strategy.get("recommendations", []):
        print(f"  → {rec}")


if __name__ == "__main__":
    main()
