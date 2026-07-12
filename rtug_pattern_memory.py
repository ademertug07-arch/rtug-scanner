"""
RTUG PATTERN MEMORY — AI Pattern Database & Matching Engine
============================================================
Gorsel analizden cikarilan pattern'leri kaydeder, canli veri ile
karsilastirir ve eslesme buldugunda tetikleme yapar.

KAIROS benzeri bellek: pattern_signature + domain + embedding + success_rate

KULLANIM:
    from rtug_pattern_memory import PatternMemory
    
    memory = PatternMemory()
    memory.add_pattern("BTC_BREAKOUT_BEFORE", {...})
    match = memory.find_best_match(current_state)
    if match and match.similarity > 0.85:
        print("Pattern eslesti!")
"""

import os
import json
import copy
import math
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

logger = logging.getLogger("rtug-pattern-memory")

# ─── Memory File ──────────────────────────────────────────
MEMORY_DIR = Path(__file__).parent / ".rtug-memory"
MEMORY_DIR.mkdir(exist_ok=True)
MEMORY_FILE = MEMORY_DIR / "pattern_memory.json"
GOLDEN_FILE = MEMORY_DIR / "golden_patterns.json"


class IndicatorState:
    """
    Indicator state'ini temsil eder — Div1-Div6, OBV, price action.
    
    Bu sinif, hem gorsel analizden cikan pattern'i hem de canli
    RTUGSignalEngine'den gelen state'i ayni formatta tutar.
    """
    
    def __init__(self, data: Optional[dict] = None):
        self.div1: float = 0.0      # Div1 degeri
        self.div2: float = 0.0      # Div2 degeri
        self.div3: float = 0.0      # Div3 degeri
        self.div5: float = 0.0      # Div5 degeri
        self.div6: float = 0.0      # Div6 degeri
        self.obv_norm: float = 0.0  # OBV normalize
        self.price: float = 0.0     # Son fiyat
        
        # Yon bilgisi (>0 = bull/up, <0 = bear/down)
        self.div1_dir: int = 0      # 1=UP, -1=DOWN, 0=FLAT
        self.div2_dir: int = 0
        self.div3_dir: int = 0
        self.div5_dir: int = 0
        self.div6_dir: int = 0
        self.obv_dir: int = 0
        
        # Renk kodlari (gorsel analizden)
        self.div1_color: str = ""
        self.div2_color: str = ""
        self.div3_color: str = ""
        self.div5_color: str = ""
        self.div6_color: str = ""
        self.obv_color: str = ""
        
        # Pattern metadata
        self.symbol: str = ""
        self.timeframe: str = ""
        self.pattern_type: str = ""  # breakout_before, outflow_before, vb
        self.price_action: str = ""  # rising, falling, ranging, consolidation
        self.description: str = ""
        
        if data:
            self.__dict__.update(data)
    
    def to_dict(self) -> dict:
        return copy.deepcopy(self.__dict__)
    
    @property
    def bull_count(self) -> int:
        """Kac divergence bullish (>0)"""
        return sum(1 for d in [self.div1_dir, self.div2_dir, self.div3_dir, self.div5_dir, self.div6_dir] if d > 0)
    
    @property
    def bear_count(self) -> int:
        """Kac divergence bearish (<0)"""
        return sum(1 for d in [self.div1_dir, self.div2_dir, self.div3_dir, self.div5_dir, self.div6_dir] if d < 0)
    
    @property
    def direction_vector(self) -> List[int]:
        """Yon vektoru — pattern esleme icin kullanilir"""
        return [self.div1_dir, self.div2_dir, self.div3_dir, self.div5_dir, self.div6_dir, self.obv_dir]
    
    @property
    def value_vector(self) -> List[float]:
        """Deger vektoru — ince esleme icin"""
        return [self.div1, self.div2, self.div3, self.div5, self.div6, self.obv_norm]
    
    def __repr__(self) -> str:
        return (f"IndState(D1:{self.div1_dir} D2:{self.div2_dir} D3:{self.div3_dir} "
                f"D5:{self.div5_dir} D6:{self.div6_dir} OBV:{self.obv_dir} | "
                f"Bull:{self.bull_count}/5 Bear:{self.bear_count}/5)")


class PatternRecord:
    """
    Bellekteki bir pattern kaydi.
    Hem gorsel analizden gelen pattern'i hem de metadata'yi icerir.
    """
    
    def __init__(self, name: str, state: IndicatorState, 
                 source: str = "vision", weight: float = 1.0):
        self.name = name
        self.state = state
        self.source = source          # "vision" veya "numerical"
        self.weight = weight          # 0.0 - 1.0 onem derecesi
        self.created = datetime.now().isoformat()
        self.updated = self.created
        self.match_count = 0          # Kac kez eslesti
        self.success_rate = 0.0       # 0.0 - 1.0 basari orani
        self.last_match = ""
        self.tags: List[str] = []
        self.notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.to_dict(),
            "source": self.source,
            "weight": self.weight,
            "created": self.created,
            "updated": self.updated,
            "match_count": self.match_count,
            "success_rate": self.success_rate,
            "last_match": self.last_match,
            "tags": self.tags,
            "notes": self.notes,
        }


class MatchResult:
    """Pattern eslesme sonucu."""
    def __init__(self, pattern: PatternRecord, similarity: float, 
                 matched_state: IndicatorState):
        self.pattern = pattern
        self.similarity = similarity      # 0.0 - 1.0
        self.matched_state = matched_state
        self.is_match = similarity >= 0.75
    
    def __repr__(self) -> str:
        return (f"Match({self.pattern.name}: {self.similarity:.1%} | "
                f"Match:{'YES' if self.is_match else 'NO'})")


class PatternMemory:
    """
    Pattern bellek sistemi.
    - Pattern ekle (gorsel/sayisal)
    - Pattern ara (benzerlik)
    - Pattern eslestir (canli veri ile)
    - Kaydet/yukle (JSON)
    """
    
    def __init__(self, memory_file: Path = MEMORY_FILE):
        self.memory_file = memory_file
        self.patterns: Dict[str, PatternRecord] = {}
        self.load()
    
    # ─── Kaydet / Yukle ─────────────────────────────────
    
    def save(self):
        """Pattern'leri JSON'a kaydet."""
        data = {
            "version": 2,
            "updated": datetime.now().isoformat(),
            "pattern_count": len(self.patterns),
            "patterns": {name: p.to_dict() for name, p in self.patterns.items()}
        }
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Pattern memory kaydedildi: {len(self.patterns)} pattern")
    
    def load(self):
        """JSON'dan pattern'leri yukle."""
        if not self.memory_file.exists():
            logger.info("Pattern memory dosyasi bulunamadi, yeni baslatiliyor")
            return
        
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            patterns = data.get("patterns", {})
            for name, pdata in patterns.items():
                state = IndicatorState(pdata.get("state", {}))
                record = PatternRecord(name, state)
                record.source = pdata.get("source", "vision")
                record.weight = pdata.get("weight", 1.0)
                record.created = pdata.get("created", "")
                record.updated = pdata.get("updated", "")
                record.match_count = pdata.get("match_count", 0)
                record.success_rate = pdata.get("success_rate", 0.0)
                record.last_match = pdata.get("last_match", "")
                record.tags = pdata.get("tags", [])
                record.notes = pdata.get("notes", "")
                self.patterns[name] = record
            
            logger.info(f"Pattern memory yuklendi: {len(self.patterns)} pattern")
        except Exception as e:
            logger.error(f"Pattern memory yukleme hatasi: {e}")
    
    # ─── Pattern Ekle / Sil / Listele ────────────────────
    
    def add_pattern(self, name: str, state: IndicatorState, 
                    source: str = "vision", weight: float = 1.0,
                    tags: Optional[List[str]] = None,
                    notes: str = "") -> PatternRecord:
        """Yeni pattern ekle veya varsa guncelle."""
        if name in self.patterns:
            record = self.patterns[name]
            record.state = state
            record.updated = datetime.now().isoformat()
            record.weight = weight
            if tags:
                record.tags = list(set(record.tags + tags))
            if notes:
                record.notes = notes
            logger.info(f"Pattern guncellendi: {name}")
        else:
            record = PatternRecord(name, state, source, weight)
            if tags:
                record.tags = tags
            if notes:
                record.notes = notes
            self.patterns[name] = record
            logger.info(f"Yeni pattern eklendi: {name}")
        
        self.save()
        return record
    
    def remove_pattern(self, name: str) -> bool:
        """Pattern sil."""
        if name in self.patterns:
            del self.patterns[name]
            self.save()
            logger.info(f"Pattern silindi: {name}")
            return True
        return False
    
    def get_pattern(self, name: str) -> Optional[PatternRecord]:
        return self.patterns.get(name)
    
    def list_patterns(self) -> List[dict]:
        """Tum pattern'leri listele."""
        return [
            {
                "name": p.name,
                "bull_count": p.state.bull_count,
                "bear_count": p.state.bear_count,
                "direction": "/".join(str(d) for d in p.state.direction_vector),
                "weight": p.weight,
                "source": p.source,
                "match_count": p.match_count,
                "success_rate": p.success_rate,
                "tags": p.tags,
                "notes": p.notes[:100] if p.notes else "",
            }
            for p in sorted(self.patterns.values(), 
                          key=lambda x: x.weight, reverse=True)
        ]
    
    # ─── Pattern Eslestirme ──────────────────────────────
    
    def _direction_similarity(self, v1: List[int], v2: List[int]) -> float:
        """Iki yon vektoru arasindaki benzerlik (0.0 - 1.0)."""
        if not v1 or not v2:
            return 0.0
        
        matches = sum(1 for a, b in zip(v1, v2) if a == b and a != 0)
        # FLAT (0) eslesmeleri daha az puan
        flats_ok = sum(1 for a, b in zip(v1, v2) if a == 0 and b == 0)
        
        total = len(v1)
        # Flat eslesmeleri %50 agirlikli say
        score = (matches + flats_ok * 0.5) / total
        return min(1.0, score)
    
    def _value_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Iki deger vektoru arasindaki benzerlik.
        
        Not: Her iki deger de sifira yakin (set edilmemis) -> nötr (0.5)
        Sadece biri set edilmis -> dusuk (0.0)
        Ikisi de set edilmis -> oran bazli benzerlik
        """
        if not v1 or not v2:
            return 0.0
        
        scores = []
        for a, b in zip(v1, v2):
            both_zero = abs(a) < 0.01 and abs(b) < 0.01
            one_zero = abs(a) < 0.01 or abs(b) < 0.01
            
            if both_zero:
                scores.append(0.5)  # Nötr - deger yok
            elif one_zero:
                scores.append(0.0)  # Biri var biri yok - eslesme yok
            else:
                ratio = min(abs(a), abs(b)) / max(abs(a), abs(b)) if max(abs(a), abs(b)) != 0 else 0
                scores.append(ratio)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _price_action_similarity(self, patterns: List[str], 
                                  current: str) -> float:
        """Fiyat aksiyonu benzerligi."""
        if not patterns or not current:
            return 0.5  # Bilinmiyorsa nötr
        
        return 1.0 if current in patterns else 0.3
    
    def find_best_match(self, current_state: IndicatorState, 
                        min_similarity: float = 0.70,
                        symbol_filter: Optional[str] = None) -> Optional[MatchResult]:
        """
        Canli state'e en uygun pattern'i bul.
        
        Args:
            current_state: Anlik indicator state
            min_similarity: Minimum eslesme orani (0.0-1.0)
            symbol_filter: Sembol filtresi (opsiyonel)
            
        Returns:
            MatchResult veya None
        """
        if not self.patterns:
            return None
        
        current_vec = current_state.direction_vector
        current_vals = current_state.value_vector
        
        best_match = None
        best_score = 0.0
        
        for name, pattern in self.patterns.items():
            pattern_vec = pattern.state.direction_vector
            pattern_vals = pattern.state.value_vector
            
            # Hesapla
            dir_sim = self._direction_similarity(current_vec, pattern_vec)
            val_sim = self._value_similarity(current_vals, pattern_vals)
            
            # Weighted score: yon %60, deger %30, metadata %10
            score = dir_sim * 0.60 + val_sim * 0.30 + 0.10
            
            # Pattern weight factor
            score = score * (0.5 + pattern.weight * 0.5)
            
            if score > best_score:
                best_score = score
                best_match = MatchResult(pattern, score, current_state)
        
        if best_match and best_match.similarity >= min_similarity:
            return best_match
        
        return None
    
    def find_all_matches(self, current_state: IndicatorState,
                         min_similarity: float = 0.70) -> List[MatchResult]:
        """Eslesen tum pattern'leri bul (sirali)."""
        if not self.patterns:
            return []
        
        current_vec = current_state.direction_vector
        current_vals = current_state.value_vector
        
        results = []
        for name, pattern in self.patterns.items():
            pattern_vec = pattern.state.direction_vector
            pattern_vals = pattern.state.value_vector
            
            dir_sim = self._direction_similarity(current_vec, pattern_vec)
            val_sim = self._value_similarity(current_vals, pattern_vals)
            score = dir_sim * 0.60 + val_sim * 0.30 + 0.10
            score = score * (0.5 + pattern.weight * 0.5)
            
            if score >= min_similarity:
                results.append(MatchResult(pattern, score, current_state))
        
        results.sort(key=lambda r: r.similarity, reverse=True)
        return results
    
    def record_match(self, pattern_name: str, success: bool = True):
        """Pattern eslesmesini kaydet (ogrenme)."""
        if pattern_name in self.patterns:
            p = self.patterns[pattern_name]
            p.match_count += 1
            p.last_match = datetime.now().isoformat()
            # Success rate guncelle
            if success:
                p.success_rate = (p.success_rate * (p.match_count - 1) + 1.0) / p.match_count
            else:
                p.success_rate = (p.success_rate * (p.match_count - 1)) / p.match_count
            p.updated = datetime.now().isoformat()
            self.save()
    
    # ─── Golden Pattern'ler (yuksek guvenilirlik) ────────
    
    def get_golden_patterns(self, min_success: float = 0.8) -> List[PatternRecord]:
        """Yuksek basarili pattern'leri getir (golden)."""
        return [
            p for p in self.patterns.values()
            if p.success_rate >= min_success and p.match_count >= 3
        ]
    
    def promote_to_golden(self, pattern_name: str) -> bool:
        """Pattern'i golden status'e yukselt."""
        # Golden = yuksek weight + yuksek success
        if pattern_name in self.patterns:
            p = self.patterns[pattern_name]
            p.weight = min(1.0, p.weight + 0.2)
            p.tags.append("golden")
            self.save()
            logger.info(f"Pattern golden'a yukseltildi: {pattern_name}")
            return True
        return False
    
    def get_statistics(self) -> dict:
        """Bellek istatistikleri."""
        total = len(self.patterns)
        if total == 0:
            return {"total": 0, "message": "Henuz pattern yok"}
        
        vision = sum(1 for p in self.patterns.values() if p.source == "vision")
        numerical = sum(1 for p in self.patterns.values() if p.source == "numerical")
        golden = len(self.get_golden_patterns())
        total_matches = sum(p.match_count for p in self.patterns.values())
        
        return {
            "total": total,
            "vision_sourced": vision,
            "numerical_sourced": numerical,
            "golden_patterns": golden,
            "total_matches": total_matches,
            "avg_success_rate": sum(p.success_rate for p in self.patterns.values()) / total if total > 0 else 0,
        }


# ─── Command-line Interface ──────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="RTUG Pattern Memory Manager")
    parser.add_argument("--list", action="store_true", help="Pattern'leri listele")
    parser.add_argument("--stats", action="store_true", help="Istatistikleri goster")
    parser.add_argument("--add", type=str, help="Pattern adi")
    parser.add_argument("--remove", type=str, help="Pattern sil")
    parser.add_argument("--show", type=str, help="Pattern detayini goster")
    parser.add_argument("--golden", action="store_true", help="Golden pattern'leri listele")
    
    args = parser.parse_args()
    
    memory = PatternMemory()
    
    if args.list:
        print("\n=== RTUG PATTERN MEMORY ===")
        patterns = memory.list_patterns()
        if not patterns:
            print("Henuz pattern kaydedilmemis.")
        else:
            for p in patterns:
                tags = f" [{','.join(p['tags'])}]" if p.get('tags') else ""
                print(f"  {p['name']:30s} | Bull:{p['bull_count']} Bear:{p['bear_count']} "
                      f"| Kaynak:{p['source']:8s} | Eslesme:{p['match_count']:3d} "
                      f"| Basari:%{p['success_rate']:.0f}{tags}")
    
    elif args.stats:
        stats = memory.get_statistics()
        print("\n=== PATTERN MEMORY ISTATISTIK ===")
        for k, v in stats.items():
            print(f"  {k}: {v}")
    
    elif args.golden:
        goldens = memory.get_golden_patterns()
        print(f"\n=== GOLDEN PATTERN'LER ({len(goldens)}) ===")
        for g in goldens:
            print(f"  {g.name}: %{g.success_rate:.0f} basari, {g.match_count} eslesme")
    
    elif args.show:
        p = memory.get_pattern(args.show)
        if p:
            print(f"\n=== PATTERN: {p.name} ===")
            print(f"  Kaynak: {p.source}")
            print(f"  Weight: {p.weight}")
            print(f"  Olusturma: {p.created}")
            print(f"  Guncelleme: {p.updated}")
            print(f"  Eslesme: {p.match_count}")
            print(f"  Basari: %{p.success_rate:.0f}")
            print(f"  Tags: {p.tags}")
            print(f"  Notlar: {p.notes}")
            print(f"\n  State:")
            s = p.state
            print(f"    Div1: {s.div1:.4f} ({s.div1_dir}) [{s.div1_color}]")
            print(f"    Div2: {s.div2:.4f} ({s.div2_dir}) [{s.div2_color}]")
            print(f"    Div3: {s.div3:.4f} ({s.div3_dir}) [{s.div3_color}]")
            print(f"    Div5: {s.div5:.4f} ({s.div5_dir}) [{s.div5_color}]")
            print(f"    Div6: {s.div6:.4f} ({s.div6_dir}) [{s.div6_color}]")
            print(f"    OBV:  {s.obv_norm:.4f} ({s.obv_dir}) [{s.obv_color}]")
            print(f"    Bull:{s.bull_count}/5 Bear:{s.bear_count}/5")
            print(f"    Price Action: {s.price_action}")
        else:
            print(f"Pattern bulunamadi: {args.show}")
    
    elif args.remove:
        if memory.remove_pattern(args.remove):
            print(f"Pattern silindi: {args.remove}")
        else:
            print(f"Pattern bulunamadi: {args.remove}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
