"""
RTUG ALERT TRACKER — Paper Trading Bridge
===========================================
Canli olarak gonderilen pattern alarmlarini takip eder, N bar sonra
breakout olup olmadigini kontrol eder, canli precision metrikleri uretir.

AKIS:
  1. Alert gonderildiginde -> track_alert() cagrilir
  2. Her scan cycle -> validate_pending() kucuk sembolleri kontrol eder
  3. Validasyon tamamlananlar -> raporlanir
  4. Haftalik -> generate_report() ile canli metrikler

KULLANIM:
    from rtug_alert_tracker import AlertTracker
    tracker = AlertTracker()
    tracker.track_alert("BTC/USDT", 50000, "TRIPLE_BULL", "crypto")
    tracker.validate_pending()  # Her scan'de
    report = tracker.generate_report()
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from rtug_scanner_core import RTUGSignalEngine

logger = logging.getLogger("rtug-alert-tracker")

LOOKAHEAD_BARS = 10
BREACH_PCT = 0.05
REPORT_DIR = Path(__file__).parent / ".rtug-alerts"
ALERTS_FILE = REPORT_DIR / "alerts.json"
METRICS_FILE = REPORT_DIR / "metrics.json"


class AlertRecord:
    """Tek bir pattern alarmi kaydi."""
    
    def __init__(self, alert_id: str, symbol: str, price: float, pattern_name: str,
                 pattern_similarity: float, mtf_confidence: float, market: str,
                 breakout_type: str, timestamp: str = None):
        self.alert_id = alert_id
        self.symbol = symbol
        self.price = price
        self.pattern_name = pattern_name
        self.pattern_similarity = pattern_similarity
        self.mtf_confidence = mtf_confidence
        self.market = market
        self.breakout_type = breakout_type
        self.timestamp = timestamp or datetime.now().isoformat()
        
        # Validasyon alanlari
        self.validated = False
        self.is_tp = False
        self.lead_bars = 0
        self.max_return_pct = 0.0
        self.validated_at = ""
        self.validation_error = ""
    
    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "symbol": self.symbol,
            "price": self.price,
            "pattern_name": self.pattern_name,
            "pattern_similarity": round(self.pattern_similarity, 3),
            "mtf_confidence": round(self.mtf_confidence, 3),
            "market": self.market,
            "breakout_type": self.breakout_type,
            "timestamp": self.timestamp,
            "validated": self.validated,
            "is_tp": self.is_tp,
            "lead_bars": self.lead_bars,
            "max_return_pct": round(self.max_return_pct, 4),
            "validated_at": self.validated_at,
            "validation_error": self.validation_error,
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> "AlertRecord":
        r = cls(d["alert_id"], d["symbol"], d["price"], d["pattern_name"],
                d["pattern_similarity"], d["mtf_confidence"], d["market"],
                d["breakout_type"], d.get("timestamp"))
        r.validated = d.get("validated", False)
        r.is_tp = d.get("is_tp", False)
        r.lead_bars = d.get("lead_bars", 0)
        r.max_return_pct = d.get("max_return_pct", 0.0)
        r.validated_at = d.get("validated_at", "")
        r.validation_error = d.get("validation_error", "")
        return r


class AlertTracker:
    """
    Pattern alarmlarini takip eder ve canli precision metrikleri uretir.
    
    Her scan cycle'da validate_pending() cagrilir -> pending alert'lerin
    sembol verilerini gunceller -> breakout kontrolu yapar -> TP/FP clasify.
    """
    
    def __init__(self):
        self.alerts: Dict[str, AlertRecord] = {}
        self.engine = RTUGSignalEngine()
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        self._load()
    
    def track_alert(self, symbol: str, price: float, pattern_name: str,
                    pattern_similarity: float, market: str, breakout_type: str,
                    mtf_confidence: float = 0.0) -> str:
        """Yeni bir pattern alarmini kaydet."""
        alert_id = f"{symbol}:{pattern_name}:{int(time.time())}"
        record = AlertRecord(
            alert_id=alert_id, symbol=symbol, price=price,
            pattern_name=pattern_name, pattern_similarity=pattern_similarity,
            mtf_confidence=mtf_confidence, market=market,
            breakout_type=breakout_type
        )
        self.alerts[alert_id] = record
        self._save()
        logger.info(f"Alert tracked: {symbol} -> {pattern_name} @ ${price:.4f}")
        return alert_id
    
    def validate_pending(self, lookahead: int = LOOKAHEAD_BARS,
                         breach: float = BREACH_PCT) -> Tuple[int, int]:
        """
        Bekleyen (validasyon yapilmamis) tum alarmlari kontrol et.
        
        Returns:
            (validated_count, tp_count)
        """
        pending = [a for a in self.alerts.values() if not a.validated]
        if not pending:
            return 0, 0
        
        validated = 0
        tp_count = 0
        
        # Gruplara ayir (market tipine gore)
        crypto_alerts = [a for a in pending if a.market == "crypto"]
        stock_alerts = [a for a in pending if a.market != "crypto"]
        
        # Crypto kontrol
        if crypto_alerts:
            symbols = list(set(a.symbol for a in crypto_alerts))
            tp_count += self._validate_batch(crypto_alerts, symbols, "ccxt", lookahead, breach)
            validated += len(crypto_alerts)
        
        # Stock kontrol
        if stock_alerts:
            symbols = list(set(a.symbol for a in stock_alerts))
            tp_count += self._validate_batch(stock_alerts, symbols, "yahoo", lookahead, breach)
            validated += len(stock_alerts)
        
        self._save()
        return validated, tp_count
    
    def _validate_batch(self, alerts: List[AlertRecord], symbols: List[str],
                        source: str, lookahead: int, breach: float) -> int:
        """Bir grup sembolu validate et."""
        from rtug_pattern_monitor import DataProvider
        
        data = {}
        try:
            if source == "ccxt":
                data = DataProvider.from_ccxt(symbols, limit=lookahead + 20)
            else:
                data = DataProvider.from_yahoo(symbols, period="1mo")
        except Exception as e:
            logger.error(f"Data fetch error: {e}")
            return 0
        
        tp_count = 0
        for alert in alerts:
            if alert.symbol not in data:
                alert.validation_error = "No data"
                alert.validated = True
                continue
            
            close, volume = data[alert.symbol]
            if len(close) < lookahead + 2:
                alert.validation_error = f"Too few bars: {len(close)}"
                alert.validated = True
                continue
            
            # Find the bar closest to alert time
            # (We use the last bar as reference since we're checking forward)
            entry_idx = max(0, len(close) - lookahead - 5)
            
            # Breakout check (same logic as backtest)
            entry_price = float(close[entry_idx])
            if entry_price <= 0:
                alert.validation_error = "Invalid price"
                alert.validated = True
                continue
            
            is_breakout = False
            lead = 0
            max_ret = 0.0
            
            future = close[entry_idx + 1:entry_idx + lookahead + 1]
            if len(future) > 0:
                max_ret = float(np.max(future)) / entry_price - 1
                for offset in range(1, min(lookahead + 1, len(close) - entry_idx)):
                    ret = float(close[entry_idx + offset]) / entry_price - 1
                    if ret >= breach:
                        is_breakout = True
                        lead = offset
                        break
            
            alert.lead_bars = lead
            alert.max_return_pct = max_ret
            alert.is_tp = is_breakout
            alert.validated = True
            alert.validated_at = datetime.now().isoformat()
            
            if is_breakout:
                tp_count += 1
        
        return tp_count
    
    def get_metrics(self) -> dict:
        """Canli precision metriklerini hesapla."""
        validated = [a for a in self.alerts.values() if a.validated]
        pending = [a for a in self.alerts.values() if not a.validated]
        
        total = len(validated)
        if total == 0:
            return {
                "total_alerts": len(self.alerts),
                "validated": 0,
                "pending": len(pending),
                "precision": 0.0,
                "avg_return": 0.0,
                "avg_lead": 0.0,
            }
        
        tp_count = sum(1 for a in validated if a.is_tp)
        avg_ret = np.mean([a.max_return_pct for a in validated if a.is_tp]) if tp_count > 0 else 0.0
        avg_lead = np.mean([a.lead_bars for a in validated if a.is_tp]) if tp_count > 0 else 0.0
        
        return {
            "total_alerts": len(self.alerts),
            "validated": total,
            "pending": len(pending),
            "true_positives": tp_count,
            "false_positives": total - tp_count,
            "precision": round(tp_count / total, 4) if total > 0 else 0.0,
            "avg_return": round(float(avg_ret), 4),
            "avg_lead_bars": round(float(avg_lead), 1),
            "last_updated": datetime.now().isoformat(),
        }
    
    def get_pattern_metrics(self) -> Dict[str, dict]:
        """Pattern bazinda metrikler."""
        pattern_stats = {}
        for a in self.alerts.values():
            if not a.validated:
                continue
            pn = a.pattern_name
            if pn not in pattern_stats:
                pattern_stats[pn] = {"signals": 0, "tp": 0, "fp": 0}
            pattern_stats[pn]["signals"] += 1
            if a.is_tp:
                pattern_stats[pn]["tp"] += 1
            else:
                pattern_stats[pn]["fp"] += 1
        
        for pn, ps in pattern_stats.items():
            total = ps["tp"] + ps["fp"]
            ps["precision"] = round(ps["tp"] / total, 4) if total > 0 else 0.0
        
        return pattern_stats
    
    def generate_report(self) -> str:
        """Haftalik/text raporu olustur."""
        metrics = self.get_metrics()
        pattern_m = self.get_pattern_metrics()
        
        lines = [
            "=" * 50,
            "RTUG ALERT TRACKER — Canli Performans Raporu",
            "=" * 50,
            f"Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            f"Toplam alarm: {metrics['total_alerts']}",
            f"Validasyon: {metrics['validated']}/{metrics['total_alerts']}",
            f"Bekleyen: {metrics['pending']}",
            "",
            f"Canli Precision: %{metrics['precision']*100:.1f}",
            f"  TP: {metrics['true_positives']} | FP: {metrics['false_positives']}",
            f"  Ort Getiri (TP): %{metrics['avg_return']*100:.2f}",
            f"  Ort Lead: {metrics['avg_lead_bars']} bar",
            "",
            "Pattern Bazinda:",
        ]
        
        for pname, ps in sorted(pattern_m.items(), key=lambda x: -x[1]["precision"]):
            lines.append(
                f"  {pname[:40]:40s} | {ps['signals']:3d} sinyal "
                f"| TP:{ps['tp']:2d} FP:{ps['fp']:2d} "
                f"| %{ps['precision']*100:.0f}"
            )
        
        lines.append("-" * 50)
        lines.append("RTUG Alert Tracker v1 (Paper Trading)")
        
        return "\n".join(lines)
    
    def _save(self):
        """Alert kayitlarini dosyaya yaz."""
        data = {aid: a.to_dict() for aid, a in self.alerts.items()}
        try:
            with open(ALERTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Alert kaydetme hatasi: {e}")
        
        # Ayri metrik dosyasi
        metrics = self.get_metrics()
        metrics["pattern_breakdown"] = self.get_pattern_metrics()
        try:
            with open(METRICS_FILE, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def _load(self):
        """Alert kayitlarini yukle."""
        if not ALERTS_FILE.exists():
            return
        try:
            with open(ALERTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for aid, d in data.items():
                self.alerts[aid] = AlertRecord.from_dict(d)
            logger.info(f"Alert tracker yuklendi: {len(self.alerts)} kayit")
        except Exception as e:
            logger.error(f"Alert tracker yukleme hatasi: {e}")


# ─── Monitor Entegrasyonu ─────────────────────────────────

def integrate_into_monitor():
    """
    Pattern monitor'u ile AlertTracker'i birlestir.
    Bu fonksiyon monitor'un scan_and_match'ine cagri olarak eklenir.
    
    Kullanim:
        tracker = AlertTracker()
        
        # Alert gonderildiginde:
        tracker.track_alert(symbol, price, pattern_name, similarity, market, breakout, mtf_conf)
        
        # Her scan cycle sonunda:
        validated, tp = tracker.validate_pending()
        if tp > 0 or validated > 0:
            logger.info(f"Alert validation: {tp} TP / {validated} total")
    """
    pass
