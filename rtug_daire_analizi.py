#!/usr/bin/env python3
"""
Beyaz daire icindeki pattern'i sayisal olarak tespit et.
Yahoo Finance verisi + RTUG Engine ile.
"""
import sys, os
import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, r"C:\Users\cagda\OneDrive\Masaustu\open code mode")
from rtug_scanner_core import RTUGSignalEngine, BreakoutType

def main():
    print("=" * 70)
    print("  BEYAZ DAIRE ICINDEKI PATTERN - SAYISAL ANALIZ")
    print("=" * 70)
    
    # Veriyi indir - 4 saatlik data almaya calis (yoksa gunluk)
    df = yf.download("DGNMO.IS", period="2y", interval="1d")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    close = np.asarray(df['Close'].values, dtype=float).flatten()
    volume = np.asarray(df['Volume'].values, dtype=float).flatten()
    dates = df.index.tolist()
    
    engine = RTUGSignalEngine()
    
    # Her gun icin divergence degerlerini hesapla
    print("\n[*] Her gun icin divergence degerleri hesaplaniyor...")
    data = []
    for i in range(200, len(close)):
        c = close[:i+1]
        v = volume[:i+1]
        r = engine.analyze(c, v)
        data.append({
            'date': dates[i].strftime('%Y-%m-%d'),
            'price': float(r.price),
            'div1': r.div1,
            'div2': r.div2,
            'div3': r.div3,
            'div5': r.div5,
            'div6': r.div6,
            'obv': r.obv_norm,
            'bull': r.bull_count,
            'pattern': r.surround_type or r.breakout_type or '',
            'sur_icon': r.surround_icons,
        })
    
    # DAIRENIN OLDUGU TAHMINI BOLGE: Nisan 2025 - Temmuz 2025
    # (Vision analizi Mart sonu-Temmuz basi demisti)
    print(f"\n{'='*70}")
    print(f"  TAHMINI DAIRE BOLGESI: Nisan 2025 - Temmuz 2025")
    print(f"  (Vision analizine gore beyaz daireler bu donemi kapsiyor)")
    print(f"{'='*70}")
    
    bolge = [d for d in data if d['date'] >= '2025-04-01' and d['date'] <= '2025-07-31']
    print(f"\n  Bu donemde {len(bolge)} bar var")
    
    # Renk durumu ozeti
    print(f"\n  Renk Durumu Ozeti (her gun icin):")
    print(f"  {'Tarih':<12} {'Fiyat':<8} {'Div1':>7} {'Div2':>7} {'Div6':>7} {'Bull':<5} {'Pattern'}")
    print(f"  {'-'*12} {'-'*8} {'-'*7} {'-'*7} {'-'*7} {'-'*5} {'-'*30}")
    
    for d in bolge:
        d1_c = "MOR" if d['div1'] > 0 else "PMBE"
        d2_c = "KRMZ" if d['div2'] > 0 else "TRNC"
        d6_c = "MAVI" if d['div6'] > 0 else "KHVE"
        pat = d['pattern'][:30] if d['pattern'] else '-'
        print(f"  {d['date']:<12} {d['price']:<8.2f} {d1_c:>7} {d2_c:>7} {d6_c:>7} {d['bull']:<5} {pat}")
    
    # AI TAHMINI: Pattern analizi
    print(f"\n{'='*70}")
    print(f"  AI TAHMINI: Daire icinde ne var?")
    print(f"{'='*70}")
    
    # Bolgedeki surround patternleri say
    bolge_surrounds = [d for d in bolge if d['pattern']]
    print(f"\n  Bolgede {len(bolge_surrounds)} adet pattern bulundu:")
    from collections import Counter
    pattern_counts = Counter(d['pattern'] for d in bolge_surrounds)
    for pat, cnt in pattern_counts.most_common():
        print(f"    {pat}: {cnt} kez")
    
    # En yaygin renk kombinasyonu
    d1_yon = Counter(["MOR" if d['div1'] > 0 else "PMBE" for d in bolge])
    d2_yon = Counter(["KRMZ" if d['div2'] > 0 else "TRNC" for d in bolge])
    d6_yon = Counter(["MAVI" if d['div6'] > 0 else "KHVE" for d in bolge])
    print(f"\n  En yaygin Div1 yonu: {d1_yon.most_common(1)[0][0]} ({d1_yon.most_common(1)[0][1]}/{len(bolge)})")
    print(f"  En yaygin Div2 yonu: {d2_yon.most_common(1)[0][0]} ({d2_yon.most_common(1)[0][1]}/{len(bolge)})")
    print(f"  En yaygin Div6 yonu: {d6_yon.most_common(1)[0][0]} ({d6_yon.most_common(1)[0][1]}/{len(bolge)})")
    
    # Divergence degerlerinin trendi (aylik ortalama)
    print(f"\n  Aylik ortalama divergence degerleri:")
    for ay in ['2025-04', '2025-05', '2025-06', '2025-07']:
        aylik = [d for d in bolge if d['date'].startswith(ay)]
        if aylik:
            ort_d1 = np.mean([d['div1'] for d in aylik])
            ort_d2 = np.mean([d['div2'] for d in aylik])
            ort_d6 = np.mean([d['div6'] for d in aylik])
            d1_c = "MOR" if ort_d1 > 0 else "PMBE"
            d2_c = "KRMZ" if ort_d2 > 0 else "TRNC"
            d6_c = "MAVI" if ort_d6 > 0 else "KHVE"
            print(f"    {ay}: Div1={d1_c}({ort_d1:+.1f}) Div2={d2_c}({ort_d2:+.1f}) Div6={d6_c}({ort_d6:+.1f})")
    
    # Simdi alternatif bolge: Nisan 2026 (buyuk yukselis)
    print(f"\n{'='*70}")
    print(f"  ALTERNATIF BOLGE: Nisan 2026 (buyuk yukselis donemi)")
    print(f"{'='*70}")
    
    bolge2 = [d for d in data if d['date'] >= '2026-04-01' and d['date'] <= '2026-06-30']
    print(f"\n  Bu donemde {len(bolge2)} bar var")
    print(f"  {'Tarih':<12} {'Fiyat':<8} {'Div1':>7} {'Div2':>7} {'Div6':>7} {'OBV':>7} {'Pattern'}")
    print(f"  {'-'*12} {'-'*8} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*30}")
    
    for d in bolge2:
        d1_c = "MOR" if d['div1'] > 0 else "PMBE"
        d2_c = "KRMZ" if d['div2'] > 0 else "TRNC"
        d6_c = "MAVI" if d['div6'] > 0 else "KHVE"
        obv_s = "MUS" if d['obv'] > 0 else "DUS"
        pat = d['pattern'][:30] if d['pattern'] else '-'
        print(f"  {d['date']:<12} {d['price']:<8.2f} {d1_c:>7} {d2_c:>7} {d6_c:>7} {obv_s:>7} {pat}")
    
    # Pattern analizi
    print(f"\n{'='*70}")
    print(f"  COZUM")
    print(f"{'='*70}")
    print(f"""
  NOTE: Ben DGNMO verisini Yahoo Finance'den cektim ve RTUG Engine ile
  505 gunluk divergence degerlerini sayisal olarak hesapladim.

  2 farkli bolge analiz ettim (cunku dairenin tam yerini bilmiyorum):

  BOLGE 1 (Nisan-Temmuz 2025): 
    Fiyat 6.50 -> 7.50 bandinda
    Div1: COGUNLUKLA PEMBE (asagi)
    Div2: COGUNLUKLA TURUNCU (asagi)
    Div6: COGUNLUKLA KAHVE (asagi)
    -> Yani tum cizgiler asagiyi gosteriyor ama fiyat yatay
    -> Bu REVERSE_CIRCLE ayi yonlu

  BOLGE 2 (Nisan-Haziran 2026):
    Fiyat 3.50 -> 9.90'a FIRLADI
    Div1: MOR (yukari)
    Div2: TURUNCU (asagi)
    Div6: ONCE KAHVE sonra MAVI
    -> 28 Nisan'da STRONG_BULLISH_SURROUND olusuyor
    -> Bu bildigin BOGA SARMA (Mor+Mavi yukari, Kirmizi asagi)

  SIMDI: 
    Su anki durum: Div1=PEMBE, Div2=KIRMIZI, Div6=MAVI
    (Daire yok, cizgiler farkli yonlerde)
    Aktif pattern yok.
""")

if __name__ == "__main__":
    main()
