#!/usr/bin/env python3
"""
RTUG Vision Analyzer v2 — TradingView Chart Görsel Analizi + Pattern Memory
===========================================================================
Bir TradingView ekran görüntüsünü alır, Gemini 2.5 Flash Vision API ile
analiz eder ve chart'taki renk pattern'lerini, divergence durumlarını
ve surround pattern'lerini tespit eder. Elde ettigi pattern'i RTUG Pattern
Memory'e kaydeder.

KULLANIM:
    python vision_analyzer.py <gorsel_yolu>                      # Sadece analiz
    python vision_analyzer.py <gorsel_yolu> --save <pattern_ad>   # Analiz + pattern kaydet
    python vision_analyzer.py <gorsel_yolu> --train               # Analiz + memory'e ekle
    python vision_analyzer.py --batch <klasor>                    # Toplu analiz
    python vision_analyzer.py --list                               # Pattern'leri listele
"""

import os
import sys
import json
import base64
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Console encoding fix
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv

# Gemini API
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[HATA] google-genai paketi yuklu degil. Yüklemek icin:")
    print("    pip install google-genai")
    sys.exit(1)

# Pillow
try:
    from PIL import Image
except ImportError:
    Image = None

# RTUG Pattern Memory
from rtug_pattern_memory import PatternMemory, IndicatorState

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rtug-vision")

# ─── Gemini Vision Analizi ───────────────────────────────

ANALYSIS_PROMPT = """You are a TradingView chart analysis expert specializing in RTUG (Real-Time Ultra-Genius) divergence indicator system.

LOOK CAREFULLY at this TradingView chart screenshot and describe EXACTLY what you see.

The RTUG system has these colored divergence lines in the lower indicator panel:
- DIV1 (100/20): Purple when UP, Pink when DOWN — Long term trend
- DIV2 (70/15): Red when UP, Orange when DOWN — Medium term trend  
- DIV3 (50/20): Green when UP, Yellow-Green when DOWN — Medium term
- DIV5 (15/5): Pink when UP, Purple when DOWN — Short term
- DIV6 (8/3): Blue/Teal when UP, Brown when DOWN — Ultra short term

There is also an OBV (On-Balance Volume) line in the indicator panel, usually shown as a white/yellow line.

CRITICAL: I need to extract NUMERICAL VALUES for the pattern. Estimate them based on the visual:
- Div values range roughly from -100 to +100 (normalized)
- OBV ranges from -1 to +1

ANALYZE AND RETURN:
1. What asset/ticker is shown? (look at the top left of the chart)
2. What timeframe? (daily, weekly, hourly, 15min, 5min, 1min)
3. For EACH divergence line (Div1-Div6), what COLOR and DIRECTION (up/down/flat)?
4. What is the OBV doing? (up/down/sideways)
5. Are there any notable patterns:
   - "SURROUND" pattern: When Div1 and Div6 move in the SAME direction while Div2 moves in the OPPOSITE direction
   - "CROSS" pattern: When a line crosses above/below zero
   - "DEEP" pattern: When 4/5 divergences agree
   - "REVERSE CIRCLE" pattern
   - "TRIPLE" pattern: Div1+Div2+Div6 all same direction
   - "BOX BREAKOUT": consolidation then explosion
6. What is the PRICE ACTION doing? (rising/falling/ranging/consolidation/breaking out)
7. What is the SECOND INDICATOR showing? Describe it in detail.
8. What is the circle or highlighted area showing?

Be VERY precise about colors. Say "PURPLE UP" not just "up". Say "RED POSITIVE" not just "positive".

Return your analysis in THIS EXACT JSON format (and ONLY the JSON, no other text):

{
  "sembol": "BTC/USDT",
  "zaman_araligi": "gunluk",
  "div1_durum": "YUKARI",
  "div1_renk": "Mor",
  "div1_deger": 45,
  "div1_yon": 1,
  "div2_durum": "ASAGI",
  "div2_renk": "Turuncu",
  "div2_deger": -30,
  "div2_yon": -1,
  "div3_durum": "YUKARI",
  "div3_renk": "Yesil",
  "div3_deger": 20,
  "div3_yon": 1,
  "div5_durum": "YUKARI",
  "div5_renk": "Pembe",
  "div5_deger": 15,
  "div5_yon": 1,
  "div6_durum": "YUKARI",
  "div6_renk": "Mavi",
  "div6_deger": 10,
  "div6_yon": 1,
  "obv_durum": "YUKARI",
  "obv_renk": "Beyaz",
  "obv_deger": 0.5,
  "obv_yon": 1,
  "bull_count": 4,
  "bear_count": 1,
  "fiyat_aksiyonu": "yukseliyor",
  "tespit_edilen_pattern": "TRIPLE_BULL",
  "pattern_aciklamasi": "Div1+Div2+Div6 hepsi yukari - guclu boğa uyumu",
  "ikinci_indikator_aciklamasi": "RSI 65'te yukari trendde",
  "daire_icerisindeki_alan": "Blok çıkış öncesi son 6 aylık konsolidasyon bölgesi",
  "strateji_onerisi": "Bu pattern boğa kırılımı öncesi tipik bir TRIPLE uyum. Blok çıkış başladığında pozisyona gir."
}
"""


def analyze_chart(image_path: str) -> dict:
    """
    Bir TradingView ekran goruntusunu Gemini Vision API ile analiz et.
    
    Returns:
        dict: Analiz sonucu (JSON format)
    """
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"hata": "GEMINI_API_KEY bulunamadi"}
    
    path = Path(image_path)
    if not path.exists():
        return {"hata": f"Dosya bulunamadi: {image_path}"}
    
    if path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp']:
        return {"hata": f"Desteklenmeyen format: {path.suffix}"}
    
    # Gorsel bilgisi
    if Image:
        try:
            with Image.open(path) as img:
                w, h = img.size
                logger.info(f"Gorsel: {path.name} ({w}x{h}px)")
        except:
            pass
    
    # Gorseli base64 encode et
    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    mime_map = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.webp': 'image/webp', '.gif': 'image/gif', '.bmp': 'image/bmp'
    }
    mime_type = mime_map.get(path.suffix.lower(), 'image/png')
    
    # Gemini API
    client = genai.Client(api_key=api_key)
    
    logger.info("Gemini API'ye gonderiliyor...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                ANALYSIS_PROMPT,
                types.Part.from_bytes(data=base64.b64decode(image_data), mime_type=mime_type)
            ],
        )
        
        result_text = response.text
        
        # Token bilgisi
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            usage = response.usage_metadata
            logger.info(f"Token: {usage.prompt_token_count}giris + {usage.candidates_token_count}cikis")
        
        # JSON parse et
        try:
            # Markdown code block icinden JSON cikar
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_str = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = result_text.strip()
            
            result = json.loads(json_str)
            logger.info("Analiz basarili: JSON parse edildi")
            return result
        except json.JSONDecodeError:
            logger.warning("JSON parse edilemedi, ham metin donduruluyor")
            return {"ham_analiz": result_text, "hata": "JSON parse hatasi"}
    
    except Exception as e:
        logger.error(f"Gemini API hatasi: {e}")
        return {"hata": f"Gemini API hatasi: {e}"}


def extract_indicator_state(analysis: dict) -> Optional[IndicatorState]:
    """Gemini analiz sonucundan IndicatorState cikar."""
    if not analysis or "hata" in analysis or "ham_analiz" in analysis:
        return None
    
    try:
        state = IndicatorState()
        state.symbol = analysis.get("sembol", "UNKNOWN")
        state.timeframe = analysis.get("zaman_araligi", "")
        state.pattern_type = analysis.get("tespit_edilen_pattern", "")
        state.description = analysis.get("pattern_aciklamasi", "")
        state.price_action = analysis.get("fiyat_aksiyonu", "")
        
        # Div1
        state.div1 = float(analysis.get("div1_deger", 0))
        state.div1_dir = int(analysis.get("div1_yon", 0))
        state.div1_color = analysis.get("div1_renk", "")
        
        # Div2
        state.div2 = float(analysis.get("div2_deger", 0))
        state.div2_dir = int(analysis.get("div2_yon", 0))
        state.div2_color = analysis.get("div2_renk", "")
        
        # Div3
        state.div3 = float(analysis.get("div3_deger", 0))
        state.div3_dir = int(analysis.get("div3_yon", 0))
        state.div3_color = analysis.get("div3_renk", "")
        
        # Div5
        state.div5 = float(analysis.get("div5_deger", 0))
        state.div5_dir = int(analysis.get("div5_yon", 0))
        state.div5_color = analysis.get("div5_renk", "")
        
        # Div6
        state.div6 = float(analysis.get("div6_deger", 0))
        state.div6_dir = int(analysis.get("div6_yon", 0))
        state.div6_color = analysis.get("div6_renk", "")
        
        # OBV
        state.obv_norm = float(analysis.get("obv_deger", 0))
        state.obv_dir = int(analysis.get("obv_yon", 0))
        state.obv_color = analysis.get("obv_renk", "")
        
        logger.info(f"IndicatorState cikarildi: Bull={state.bull_count}/5 Bear={state.bear_count}/5")
        logger.info(f"  Div yonleri: {state.direction_vector}")
        
        return state
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"IndicatorState cikarma hatasi: {e}")
        return None


def format_analysis_report(analysis: dict) -> str:
    """Analiz sonucunu okunabilir metne cevir."""
    if "hata" in analysis:
        return f"[HATA] {analysis['hata']}"
    
    if "ham_analiz" in analysis:
        return analysis["ham_analiz"]
    
    lines = [
        "=" * 60,
        "  RTUG VISION ANALYZER v2 — Chart Analizi",
        "=" * 60,
        "",
        f"Sembol: {analysis.get('sembol', 'Bilinmiyor')}",
        f"Zaman:  {analysis.get('zaman_araligi', 'Bilinmiyor')}",
        "",
        "--- RENK DURUMU ---",
        f"Div1 (Mor/Pembe):   {analysis.get('div1_durum', '?')} [{analysis.get('div1_renk', '?')}] "
            f"Deger: {analysis.get('div1_deger', '?')}",
        f"Div2 (Kirmizi/Turuncu): {analysis.get('div2_durum', '?')} [{analysis.get('div2_renk', '?')}] "
            f"Deger: {analysis.get('div2_deger', '?')}",
        f"Div3 (Yesil/Sari):  {analysis.get('div3_durum', '?')} [{analysis.get('div3_renk', '?')}] "
            f"Deger: {analysis.get('div3_deger', '?')}",
        f"Div5 (Pembe/Mor):   {analysis.get('div5_durum', '?')} [{analysis.get('div5_renk', '?')}] "
            f"Deger: {analysis.get('div5_deger', '?')}",
        f"Div6 (Mavi/Kahve):  {analysis.get('div6_durum', '?')} [{analysis.get('div6_renk', '?')}] "
            f"Deger: {analysis.get('div6_deger', '?')}",
        f"OBV:                {analysis.get('obv_durum', '?')} [{analysis.get('obv_renk', '?')}] "
            f"Deger: {analysis.get('obv_deger', '?')}",
        "",
        f"Bull: {analysis.get('bull_count', '?')}/5 | Bear: {analysis.get('bear_count', '?')}/5",
        "",
        "--- TESPIT EDILEN PATTERN ---",
        f"Pattern: {analysis.get('tespit_edilen_pattern', 'Yok')}",
        f"Aciklama: {analysis.get('pattern_aciklamasi', '-')}",
        "",
        "--- IKINCI INDIKATOR ---",
        analysis.get('ikinci_indikator_aciklamasi', 'Goruntulenemiyor'),
        "",
        "--- DAIRE ICINDEKI ALAN ---",
        analysis.get('daire_icerisindeki_alan', 'Belirtilmemis'),
        "",
        "--- STRATEJI ONERISI ---",
        analysis.get('strateji_onerisi', 'Henuz oneri yok'),
        "",
        "=" * 60,
    ]
    return "\n".join(lines)


# ─── Ana Fonksiyon ────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RTUG Vision Analyzer v2 — Gorsel Analiz + Pattern Memory")
    parser.add_argument("image", nargs="?", help="Gorsel dosya yolu")
    parser.add_argument("--save", type=str, help="Pattern adi vererek memory'e kaydet")
    parser.add_argument("--train", action="store_true", 
                       help="Analiz et ve pattern memory'e ekle")
    parser.add_argument("--batch", type=str, help="Klasordeki tum gorselleri analiz et")
    parser.add_argument("--list", action="store_true", help="Memory'deki pattern'leri listele")
    parser.add_argument("--stats", action="store_true", help="Memory istatistikleri")
    parser.add_argument("--no-display", action="store_true", 
                       help="Analiz sonucunu konsolda gosterme (sadece kaydet)")
    
    args = parser.parse_args()
    
    memory = PatternMemory()
    
    # Pattern listeleme
    if args.list:
        patterns = memory.list_patterns()
        print("\n=== RTUG PATTERN MEMORY ===")
        if not patterns:
            print("Henuz pattern kaydedilmemis.")
        else:
            for p in patterns:
                tags = f" [{','.join(p['tags'])}]" if p.get('tags') else ""
                print(f"  {p['name']:30s} | Bull:{p['bull_count']} Bear:{p['bear_count']} "
                      f"| {p['source']:8s} | %{p['success_rate']:.0f} | {p['match_count']} eslesme{tags}")
        return
    
    if args.stats:
        stats = memory.get_statistics()
        print("\n=== PATTERN MEMORY ISTATISTIK ===")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        return
    
    # Toplu analiz
    if args.batch:
        folder = Path(args.batch)
        if not folder.is_dir():
            print(f"[HATA] Klasor bulunamadi: {args.batch}")
            return
        
        images = list(folder.glob("*.png")) + list(folder.glob("*.jpg")) + \
                 list(folder.glob("*.jpeg")) + list(folder.glob("*.webp"))
        
        if not images:
            print(f"Gorsel bulunamadi: {args.batch}")
            return
        
        print(f"\n{len(images)} gorsel analiz ediliyor...\n")
        for img_path in sorted(images):
            print(f"[{img_path.name}]")
            result = analyze_chart(str(img_path))
            state = extract_indicator_state(result)
            
            if state:
                pattern_name = f"BATCH_{img_path.stem}"
                memory.add_pattern(pattern_name, state, source="vision", 
                                 notes=result.get("pattern_aciklamasi", ""))
                print(f"  Pattern kaydedildi: {pattern_name}")
                print(f"  Pattern: {result.get('tespit_edilen_pattern', '?')} | "
                      f"Bull:{state.bull_count}/5 Bear:{state.bear_count}/5\n")
            else:
                print(f"  Analiz basarisiz\n")
        
        print(f"Toplam: {len(images)} gorsel, {len(memory.patterns)} pattern")
        return
    
    # Tek gorsel analizi
    if not args.image:
        parser.print_help()
        return
    
    print("=" * 60)
    print("  RTUG VISION ANALYZER v2")
    print("  Gorsel Analiz + Pattern Memory Training")
    print("=" * 60)
    print()
    
    result = analyze_chart(args.image)
    
    if not args.no_display:
        print()
        report = format_analysis_report(result)
        print(report)
    
    # Pattern state cikar
    state = extract_indicator_state(result)
    
    if state and (args.save or args.train):
        pattern_name = args.save or f"VISION_{Path(args.image).stem}"
        
        strategy_text = result.get("strateji_onerisi", "")
        notes = (
            f"Gorsel: {Path(args.image).name}\n"
            f"Pattern: {result.get('tespit_edilen_pattern', '?')}\n"
            f"Ikinci Indikator: {result.get('ikinci_indikator_aciklamasi', '?')}\n"
            f"Daire Alani: {result.get('daire_icerisindeki_alan', '?')}\n"
            f"Strateji: {strategy_text}"
        )
        
        memory.add_pattern(
            pattern_name, state, source="vision", weight=1.0,
            tags=[result.get("tespit_edilen_pattern", "bilinmiyor").lower()],
            notes=notes
        )
        
        print()
        print(f"✅ Pattern memory'e kaydedildi: '{pattern_name}'")
        print(f"   Pattern: {result.get('tespit_edilen_pattern', '?')}")
        print(f"   Bull:{state.bull_count}/5 Bear:{state.bear_count}/5")
        print(f"   Yon vektoru: {state.direction_vector}")
        
        if strategy_text:
            print(f"\n📋 Strateji:")
            print(f"   {strategy_text}")
    
    elif state and not (args.save or args.train):
        print()
        print("💡 Pattern'i memory'e kaydetmek icin:")
        print(f"   python vision_analyzer.py \"{args.image}\" --train")
        print(f"   python vision_analyzer.py \"{args.image}\" --save ozel_adi")
    
    # Golden pattern var mi kontrol
    goldens = memory.get_golden_patterns()
    if goldens:
        print(f"\n🏆 Golden pattern'ler (otomatik esleme icin hazir):")
        for g in goldens:
            print(f"   {g.name}: %{g.success_rate:.0f} basari, {g.match_count} eslesme")


if __name__ == "__main__":
    main()
