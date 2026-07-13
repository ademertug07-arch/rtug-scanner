"""
RTUG PATTERN EVOLVER v1 — Adaptif Pattern Evrimi
===================================================
Canli backtest + alert tracker verilerini kullanarak pattern memory'ini
otomatik olarak iyilestirir.

YAPILANLAR:
  1. Her pattern'in precision'ini backtest + canli veriden hesapla
  2. Basarisiz pattern'lerin ortak divergence profilini cikar (FP profili)
  3. Pattern agirliklarini otomatik guncelle
  4. Dusuk performansli pattern'leri prune et
  5. Yeni pattern onerileri uret

KULLANIM:
    from rtug_pattern_evolver import PatternEvolver
    evolver = PatternEvolver(memory)
    report = evolver.evolve()
    print(report["summary"])
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from rtug_pattern_memory import PatternMemory

logger = logging.getLogger("rtug-evolver")

# Minimum veri gereksinimleri
MIN_SIGNALS_FOR_EVAL = 3
MIN_PRECISION_TO_KEEP = 0.30
FP_PROFILE_MIN_SAMPLES = 5

# Dosya yollari
BACKTEST_REPORT = Path(__file__).parent / ".rtug-backtest" / "aggregate_report.json"
ALERT_METRICS = Path(__file__).parent / ".rtug-alerts" / "metrics.json"
ALERTS_FILE = Path(__file__).parent / ".rtug-alerts" / "alerts.json"
EVOLUTION_LOG = Path(__file__).parent / ".rtug-memory" / "evolution_log.json"


def load_backtest_data() -> dict:
    """Backtest aggregate raporunu yukle."""
    if not BACKTEST_REPORT.exists():
        return {}
    try:
        with open(BACKTEST_REPORT, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Backtest data yukleme: {e}")
        return {}


def load_alert_data() -> dict:
    """Alert tracker verilerini yukle."""
    data = {"metrics": {}, "alerts": []}
    
    if ALERT_METRICS.exists():
        try:
            with open(ALERT_METRICS, "r", encoding="utf-8") as f:
                data["metrics"] = json.load(f)
        except Exception:
            pass
    
    if ALERTS_FILE.exists():
        try:
            with open(ALERTS_FILE, "r", encoding="utf-8") as f:
                data["alerts"] = list(json.load(f).values())
        except Exception:
            pass
    
    return data


class PatternEvolver:
    """
    Pattern memory'ini canli veriyle iyilestir.
    
    Ornek:
        evolver = PatternEvolver(memory)
        result = evolver.evolve()
        
        # Raporu gormek icin:
        print(result["summary"])
        
        # Degisiklikleri uygulamak icin:
        if result["changes_applied"]:
            memory.save()
    """
    
    def __init__(self, memory: Optional[PatternMemory] = None):
        self.memory = memory or PatternMemory()
        self.backtest = load_backtest_data()
        self.alerts = load_alert_data()
    
    def evolve(self, dry_run: bool = True) -> dict:
        """
        Ana evrim fonksiyonu.
        
        Args:
            dry_run: True ise sadece rapor ver, degisiklik yapma
        
        Returns:
            dict: Evrim raporu
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "backtest_data": bool(self.backtest),
            "alert_data": bool(self.alerts.get("alerts")),
            "dry_run": dry_run,
            "changes_applied": False,
            "summary": "",
            "pattern_performance": [],
            "fp_profile": {},
            "pruned_patterns": [],
            "recommendations": [],
        }
        
        # 1. Pattern performans degerlendirmesi
        perf = self._evaluate_patterns()
        report["pattern_performance"] = perf
        
        # 2. FP profil analizi
        fp_profile = self._analyze_fp_profile()
        report["fp_profile"] = fp_profile
        
        # 3. Prune kararlari
        pruned = self._prune_decisions(perf, dry_run)
        report["pruned_patterns"] = pruned
        
        # 4. Oneriler
        recommendations = self._generate_recommendations(perf, fp_profile)
        report["recommendations"] = recommendations
        
        # 5. Agirlik guncelleme
        weight_changes = self._update_weights(perf, dry_run)
        report["weight_changes"] = weight_changes
        
        # Ozet
        report["summary"] = self._format_summary(report)
        report["changes_applied"] = not dry_run and (len(pruned) > 0 or len(weight_changes) > 0)
        
        # Evolution log
        self._log_evolution(report)
        
        return report
    
    def _evaluate_patterns(self) -> List[dict]:
        """Her pattern'in backtest + canli precision'ini hesapla."""
        pattern_data = defaultdict(lambda: {
            "backtest_signals": 0, "backtest_tp": 0,
            "live_signals": 0, "live_tp": 0, "live_fp": 0,
            "total_similarity": 0.0, "match_count": 0,
        })
        
        # Backtest verisi
        backtest_patterns = self.backtest.get("pattern_breakdown", {})
        for pname, pdata in backtest_patterns.items():
            pd = pattern_data[pname]
            pd["backtest_signals"] = pdata.get("total_signals", 0)
            pd["backtest_tp"] = pdata.get("true_positives", 0)
        
        # Canli alert verisi
        for alert in self.alerts.get("alerts", []):
            pname = alert.get("pattern_name", "unknown")
            if alert.get("validated"):
                pd = pattern_data[pname]
                pd["live_signals"] += 1
                if alert.get("is_tp"):
                    pd["live_tp"] += 1
                else:
                    pd["live_fp"] += 1
        
        # Memory'den match counts
        memory_patterns = self.memory.get_statistics().get("patterns", {})
        for pname, pstats in memory_patterns.items():
            if pname in pattern_data:
                pattern_data[pname]["match_count"] = pstats.get("match_count", 0)
        
        # Birlestirilmis skor
        results = []
        for pname, pd in pattern_data.items():
            total_signals = pd["backtest_signals"] + pd["live_signals"]
            total_tp = pd["backtest_tp"] + pd["live_tp"]
            combined_precision = total_tp / total_signals if total_signals > 0 else 0.0
            
            # Weighted: canli veri daha agirlikli
            if pd["live_signals"] >= MIN_SIGNALS_FOR_EVAL and pd["backtest_signals"] > 0:
                weighted_precision = (
                    pd["backtest_tp"] / pd["backtest_signals"] * 0.3 +
                    pd["live_tp"] / pd["live_signals"] * 0.7
                ) if pd["live_signals"] > 0 else 0.0
            else:
                weighted_precision = combined_precision
            
            results.append({
                "name": pname,
                "backtest_signals": pd["backtest_signals"],
                "backtest_tp": pd["backtest_tp"],
                "backtest_precision": round(pd["backtest_tp"] / pd["backtest_signals"], 4) if pd["backtest_signals"] > 0 else 0.0,
                "live_signals": pd["live_signals"],
                "live_tp": pd["live_tp"],
                "live_precision": round(pd["live_tp"] / pd["live_signals"], 4) if pd["live_signals"] > 0 else 0.0,
                "combined_signals": total_signals,
                "combined_precision": round(combined_precision, 4),
                "weighted_precision": round(weighted_precision, 4),
                "match_count": pd["match_count"],
                "status": self._classify_pattern(weighted_precision, total_signals),
            })
        
        return sorted(results, key=lambda x: -x["weighted_precision"])
    
    def _classify_pattern(self, precision: float, signals: int) -> str:
        """Pattern durumunu siniflandir."""
        if signals < MIN_SIGNALS_FOR_EVAL:
            return "insufficient_data"
        if precision >= 0.60:
            return "high_performer"
        elif precision >= MIN_PRECISION_TO_KEEP:
            return "moderate"
        else:
            return "underperformer"
    
    def _analyze_fp_profile(self) -> dict:
        """False positive profili cikar: Hangi divergence kosullari FP uretiyor?"""
        # Backtest'ten FP bar profillerini analiz et
        fp_profile = {
            "common_fp_patterns": [],
            "volume_conditions": {"low_vol_fp": 0, "high_vol_fp": 0, "total_fp": 0},
            "divergence_patterns": defaultdict(int),
            "suggestions": [],
        }
        
        # Alert tracker'dan FP analizi
        for alert in self.alerts.get("alerts", []):
            if alert.get("validated") and not alert.get("is_tp"):
                fp_profile["volume_conditions"]["total_fp"] += 1
                # Basit volume karsilastirmasi
                ret = abs(alert.get("max_return_pct", 0))
                if ret < 0.02:
                    fp_profile["volume_conditions"]["low_vol_fp"] += 1
                else:
                    fp_profile["volume_conditions"]["high_vol_fp"] += 1
        
        # Backtest FP istatistikleri
        total_fp = fp_profile["volume_conditions"]["total_fp"]
        low_vol = fp_profile["volume_conditions"]["low_vol_fp"]
        high_vol = fp_profile["volume_conditions"]["high_vol_fp"]
        
        if total_fp >= FP_PROFILE_MIN_SAMPLES:
            if low_vol / total_fp > 0.6:
                fp_profile["suggestions"].append(
                    "FP'lerin cogu dusuk getirili (%2 alti). Volume filter + OBV alignment eklenebilir."
                )
            if high_vol / total_fp > 0.6:
                fp_profile["suggestions"].append(
                    "FP'ler yuksek getirili. Pattern yonunun tersine hareket ediyor olabilir. Reverse check ekle."
                )
        
        return dict(fp_profile)
    
    def _prune_decisions(self, perf: List[dict], dry_run: bool) -> List[dict]:
        """Dusuk performansli pattern'lari prune et."""
        pruned = []
        
        for p in perf:
            if p["status"] != "underperformer":
                continue
            if p["combined_signals"] < MIN_SIGNALS_FOR_EVAL:
                continue
            
            pattern = self.memory.get_pattern(p["name"])
            if pattern and not dry_run:
                self.memory.remove_pattern(p["name"])
                logger.info(f"Pruned: {p['name']} (precision: %{p['weighted_precision']*100:.0f})")
            
            pruned.append({
                "name": p["name"],
                "precision": p["weighted_precision"],
                "signals": p["combined_signals"],
                "removed": not dry_run,
            })
        
        return pruned
    
    def _update_weights(self, perf: List[dict], dry_run: bool) -> List[dict]:
        """Pattern agirliklarini performansa gore guncelle."""
        changes = []
        
        for p in perf:
            if p["combined_signals"] < MIN_SIGNALS_FOR_EVAL:
                continue
            
            pattern = self.memory.get_pattern(p["name"])
            if not pattern:
                continue
            
            old_weight = pattern.success_rate
            new_weight = p["weighted_precision"]
            
            # Agirlik guncelleme: EMA benzeri (70% yeni, 30% eski)
            if old_weight > 0:
                new_weight = old_weight * 0.3 + new_weight * 0.7
            
            if abs(new_weight - old_weight) > 0.05 and not dry_run:
                pattern.success_rate = new_weight
                changes.append({
                    "name": p["name"],
                    "old_weight": round(old_weight, 3),
                    "new_weight": round(new_weight, 3),
                    "delta": round(new_weight - old_weight, 3),
                })
                logger.info(f"Weight update: {p['name']} {old_weight:.2f} -> {new_weight:.2f}")
        
        return changes
    
    def _generate_recommendations(self, perf: List[dict], fp_profile: dict) -> List[str]:
        """Pattern iyilestirme onerileri."""
        recs = []
        
        # En iyi pattern'ler
        top = [p for p in perf if p["status"] == "high_performer" and p["combined_signals"] >= MIN_SIGNALS_FOR_EVAL]
        if top:
            names = ", ".join(t["name"][:30] for t in top[:3])
            recs.append(f"En iyi pattern'ler: {names}. Bunlara daha fazla agirlik ver.")

        # En kotu pattern'ler
        worst = [p for p in perf if p["status"] == "underperformer" and p["combined_signals"] >= MIN_SIGNALS_FOR_EVAL]
        if worst:
            recs.append(f"{len(worst)} pattern dusuk performansli: precision < %30. Prune onerilir.")
        
        # Genel FP onerileri
        recs.extend(fp_profile.get("suggestions", []))
        
        # Yeni pattern onerisi
        recs.append(
            "Yeni pattern egitimi icin vision_analyzer.py ile daha fazla gorsel analiz edin.\n"
            "  -> python vision_analyzer.py <chart.png> --train"
        )
        
        return recs
    
    def _format_summary(self, report: dict) -> str:
        """Insan okunabilir ozet."""
        perf = report["pattern_performance"]
        total = len(perf)
        high = sum(1 for p in perf if p["status"] == "high_performer")
        mod = sum(1 for p in perf if p["status"] == "moderate")
        low = sum(1 for p in perf if p["status"] == "underperformer")
        insuf = sum(1 for p in perf if p["status"] == "insufficient_data")
        
        lines = [
            "=" * 50,
            "RTUG PATTERN EVOLVER — Evrim Raporu",
            "=" * 50,
            f"Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            f"Backtest data: {'VAR' if report['backtest_data'] else 'YOK'}",
            f"Canli alert data: {'VAR' if report['alert_data'] else 'YOK'}",
            f"Dry run: {report['dry_run']}",
            "",
            f"Pattern Degerlendirme ({total} toplam):",
            f"  High performer (>= %%60):     {high}",
            f"  Moderate (%%30-60):           {mod}",
            f"  Underperformer (< %%30):       {low}",
            f"  Yetersiz veri (< {MIN_SIGNALS_FOR_EVAL} sinyal): {insuf}",
            "",
        ]
        
        if report["pruned_patterns"]:
            lines.append(f"Prune edilen: {len(report['pruned_patterns'])}")
            for p in report["pruned_patterns"]:
                lines.append(f"  - {p['name'][:40]}: %{p['precision']*100:.0f} ({p['signals']} sinyal) {'[SILINDI]' if p['removed'] else '[ONERILEN]'}")
            lines.append("")
        
        if report["weight_changes"]:
            lines.append(f"Agirlik guncellemesi: {len(report['weight_changes'])}")
            for w in report["weight_changes"][:5]:
                delta_s = f"+{w['delta']:.2f}" if w['delta'] > 0 else f"{w['delta']:.2f}"
                lines.append(f"  {w['name'][:40]}: {w['old_weight']:.2f} -> {w['new_weight']:.2f} ({delta_s})")
            lines.append("")
        
        lines.append("Oneriler:")
        for i, rec in enumerate(report["recommendations"], 1):
            lines.append(f"  {i}. {rec}")
        
        lines.append("-" * 50)
        lines.append("RTUG Pattern Evolver v1")
        
        return "\n".join(lines)
    
    def _log_evolution(self, report: dict):
        """Evolution log'una kaydet."""
        log_entry = {
            "timestamp": report["timestamp"],
            "pruned": len(report["pruned_patterns"]),
            "weight_updates": len(report.get("weight_changes", [])),
            "dry_run": report["dry_run"],
            "changes_applied": report["changes_applied"],
            "recommendations": report["recommendations"],
        }
        
        try:
            EVOLUTION_LOG.parent.mkdir(parents=True, exist_ok=True)
            
            history = []
            if EVOLUTION_LOG.exists():
                with open(EVOLUTION_LOG, "r", encoding="utf-8") as f:
                    history = json.load(f)
            
            history.append(log_entry)
            
            # Son 100 kaydi tut
            if len(history) > 100:
                history = history[-100:]
            
            with open(EVOLUTION_LOG, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Evolution log: {e}")
