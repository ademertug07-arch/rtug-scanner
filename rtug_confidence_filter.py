"""
RTUG CONFIDENCE FILTER v1 — High-Confidence Signal Gate
=========================================================
Pattern eslesmesi + MTF dogrulama + gecmis precision verilerini
birlestirerek sadece yuksek guvenilirlikli sinyallerin (%70+)
Telegram'a gecmesini saglar.

AKIS:
  pattern_match (0-1) * 0.40
  + mtf_confidence (0-1) * 0.35
  + historical_precision (0-1) * 0.15
  + volume_boost (0-0.10)
  + mtf_strong_boost (+0.05 if MTF >= 0.60)
  = final_score

  final_score >= 0.70 -> GECER
  final_score < 0.70  -> ENGELLENIR

KULLANIM:
    from rtug_confidence_filter import ConfidenceFilter
    gate = ConfidenceFilter()
    result = gate.evaluate(pattern_name, pattern_sim, mtf_conf, volume_ratio)
    if result.passed:
        send_telegram(result.build_alert(...))
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger("rtug-confidence")

BACKTEST_REPORT = Path(__file__).parent / ".rtug-backtest" / "aggregate_report.json"
ALERT_METRICS = Path(__file__).parent / ".rtug-alerts" / "metrics.json"

@dataclass
class GateResult:
    pattern_name: str
    symbol: str
    pattern_similarity: float
    mtf_confidence: float
    historical_precision: float
    volume_ratio: float
    final_score: float
    passed: bool
    reasons: List[str] = field(default_factory=list)

    def build_alert_line(self) -> str:
        """Telegram mesajina eklenecek kisa skor satiri."""
        status = "GECTI" if self.passed else "ENGELLENDI"
        return (
            f"[Gate: %{self.final_score*100:.0f} {status}] "
            f"(p:%{self.pattern_similarity*100:.0f} "
            f"m:%{self.mtf_confidence*100:.0f} "
            f"h:%{self.historical_precision*100:.0f})"
        )

    def soft_reject_line(self) -> str:
        return (
            f"RED: {self.symbol} -> {self.pattern_name}\n"
            f"  Score: %{self.final_score*100:.0f} (< %70)\n"
            f"  Pattern: %{self.pattern_similarity*100:.0f} | "
            f"MTF: %{self.mtf_confidence*100:.0f} | "
            f"Hist: %{self.historical_precision*100:.0f}\n"
            f"  Neden: {' | '.join(self.reasons)}"
        )


class ConfidenceFilter:
    """
    Sinyal kalite gecidi. Sadece %70+ guven skoru olan sinyaller gecer.
    """

    def __init__(self):
        self._precision_cache: dict = {}
        self._load_precision_data()

    def _load_precision_data(self):
        """Backtest + AlertTracker'dan pattern precision verilerini yukle."""
        # Backtest verisi
        if BACKTEST_REPORT.exists():
            try:
                with open(BACKTEST_REPORT, "r", encoding="utf-8") as f:
                    bt = json.load(f)
                for pname, pdata in bt.get("pattern_breakdown", {}).items():
                    total = pdata.get("total_signals", 0)
                    tp = pdata.get("true_positives", 0)
                    self._precision_cache[pname] = {
                        "precision": tp / total if total > 0 else 0.0,
                        "signals": total,
                        "source": "backtest"
                    }
            except Exception as e:
                logger.debug(f"Backtest yukleme: {e}")

        # Canli alert metrikleri
        if ALERT_METRICS.exists():
            try:
                with open(ALERT_METRICS, "r", encoding="utf-8") as f:
                    am = json.load(f)
                for pname, pdata in am.get("pattern_breakdown", {}).items():
                    total = pdata.get("signals", 0)
                    tp = pdata.get("tp", 0)
                    precision = tp / total if total > 0 else 0.0
                    if pname in self._precision_cache:
                        old = self._precision_cache[pname]
                        agg_total = old["signals"] + total
                        agg_tp = int(old["precision"] * old["signals"]) + tp
                        self._precision_cache[pname] = {
                            "precision": agg_tp / agg_total if agg_total > 0 else 0.0,
                            "signals": agg_total,
                            "source": "combined"
                        }
                    else:
                        self._precision_cache[pname] = {
                            "precision": precision,
                            "signals": total,
                            "source": "live"
                        }
            except Exception as e:
                logger.debug(f"Alert metrics yukleme: {e}")

    def get_pattern_precision(self, pattern_name: str) -> float:
        """Bir pattern'in gecmis precision'ini getir. Veri yoksa 0.50 notr."""
        data = self._precision_cache.get(pattern_name)
        if data and data["signals"] >= 3:
            return data["precision"]
        return 0.50

    def evaluate(self, symbol: str, pattern_name: str,
                 pattern_similarity: float, mtf_confidence: float,
                 volume_ratio: float = 1.0) -> GateResult:
        """
        Sinyal kalitesini degerlendir.

        Args:
            symbol: Sembol adi
            pattern_name: Pattern adi
            pattern_similarity: Pattern eslesme yuzdesi (0-1)
            mtf_confidence: MTF guven skoru (0-1)
            volume_ratio: Son hacim / ortalama hacim orani

        Returns:
            GateResult: Gecis/engel karari
        """
        reasons = []

        # 1. Historik precision
        hist_precision = self.get_pattern_precision(pattern_name)

        # 2. Volume boost
        volume_boost = 0.0
        if volume_ratio > 1.3:
            volume_boost = 0.05
            reasons.append(f"hacim %{(volume_ratio-1)*100:.0f} artti")
        elif volume_ratio < 0.7:
            volume_boost = -0.05
            reasons.append(f"hacim %{(1-volume_ratio)*100:.0f} dustu")

        # 3. MTF boost: eger MTF >= 0.60 ise ekstra +0.05
        mtf_boost = 0.05 if mtf_confidence >= 0.60 else 0.0
        if mtf_boost > 0:
            reasons.append("MTF guclu")

        # 4. Final skor
        final_score = (
            pattern_similarity * 0.40
            + mtf_confidence * 0.35
            + hist_precision * 0.15
            + volume_boost
            + mtf_boost
        )
        final_score = max(0.0, min(1.0, final_score))

        # 4. Gecis karari
        passed = final_score >= 0.70

        if not passed:
            if pattern_similarity < 0.70:
                reasons.append("pattern eslesmesi dusuk")
            if mtf_confidence < 0.40:
                reasons.append("MTF teyit yetersiz")
            if hist_precision < 0.30:
                reasons.append("gecmis basari orani dusuk")

        return GateResult(
            pattern_name=pattern_name,
            symbol=symbol,
            pattern_similarity=pattern_similarity,
            mtf_confidence=mtf_confidence,
            historical_precision=hist_precision,
            volume_ratio=volume_ratio,
            final_score=round(final_score, 3),
            passed=passed,
            reasons=reasons or ["filtre gecti"],
        )
