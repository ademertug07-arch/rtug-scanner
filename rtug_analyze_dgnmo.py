#!/usr/bin/env python3
"""
RTUG DGNMO Derin Analiz — Programatik olarak divergence degerlerini hesaplar.
Screenshot'a gerek kalmadan renkleri ve pattern'leri sayisal olarak tespit eder.
"""
import sys, os
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

sys.path.insert(0, r"C:\Users\cagda\OneDrive\Masaustu\open code mode")
from rtug_scanner_core import RTUGSignalEngine, BreakoutType

def main():
    print("=" * 70)
    print("  RTUG DERIN ANALIZ -- DGNMO (Doganlar Mobilya)")
    print("=" * 70)
    
    # 1. Veriyi indir
    print("\n[*] Yahoo Finance'den DGNMO verisi cekiliyor...")
    df = yf.download("DGNMO.IS", period="2y", interval="1d")
    
    # MultiIndex column fix
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    print(f"    Periyot: {df.index[0].strftime('%d %b %Y')} - {df.index[-1].strftime('%d %b %Y')}")
    print(f"    Bar sayisi: {len(df)}")
    print(f"    Son fiyat: {float(df['Close'].iloc[-1]):.2f} TRY")
    
    close = np.asarray(df['Close'].values, dtype=float).flatten()
    volume = np.asarray(df['Volume'].values, dtype=float).flatten()
    dates = df.index.tolist()
    
    # 2. RTUG Engine ile analiz
    print("\n[*] RTUG divergence hesaplaniyor...")
    engine = RTUGSignalEngine()
    result = engine.analyze(close, volume)
    
    # 3. Son durum raporu
    print(f"\n{'='*70}")
    print(f"  SON DURUM RAPORU ({dates[-1].strftime('%d %b %Y')})")
    print(f"{'='*70}")
    
    d1_c = "MOR UP" if result.div1 > 0 else "PEMBE DN"
    d2_c = "KIRMIZI UP" if result.div2 > 0 else "TURUNCU DN"
    d3_c = "YESIL UP" if result.div3 > 0 else "SARI DN"
    d5_c = "PEMBE UP" if result.div5 > 0 else "MOR DN"
    d6_c = "MAVI UP" if result.div6 > 0 else "KAHVE DN"
    
    print(f"  Fiyat: {result.price:.2f} TRY")
    print(f"  OBV Norm: {result.obv_norm:+.4f}")
    print(f"  Bull: {result.bull_count}/5 | Bear: {result.bear_count}/5")
    print(f"  Sinyal: {result.breakout_type or 'YOK'}")
    print(f"  Surround: {result.surround_icons or 'YOK'}")
    print()
    print(f"  Div1 (100/20): {result.div1:+.4f} --> {d1_c}")
    print(f"  Div2 (70/15):  {result.div2:+.4f} --> {d2_c}")
    print(f"  Div3 (50/20):  {result.div3:+.4f} --> {d3_c}")
    print(f"  Div5 (15/5):   {result.div5:+.4f} --> {d5_c}")
    print(f"  Div6 (8/3):    {result.div6:+.4f} --> {d6_c}")
    
    # 4. Gecmis pattern taramasi
    print(f"\n{'='*70}")
    print(f"  GECMIS PATTERN TARAMASI")
    print(f"{'='*70}")
    
    patterns_found = []
    for i in range(200, len(close)):
        c = close[:i+1]
        v = volume[:i+1]
        r = engine.analyze(c, v)
        if r.has_signal or r.surround_type:
            date_str = dates[i].strftime('%Y-%m-%d')
            patterns_found.append({
                'date': date_str,
                'price': float(r.price),
                'type': r.breakout_type or r.surround_type,
                'bull': r.bull_count,
                'bear': r.bear_count,
                'd1': r.div1, 'd2': r.div2, 'd3': r.div3, 'd5': r.div5, 'd6': r.div6,
            })
    
    print(f"  Toplam {len(patterns_found)} pattern bulundu")
    
    # Son 6 aydaki pattern'ler
    six_months_ago = datetime.now() - timedelta(days=180)
    recent = [p for p in patterns_found if p['date'] >= six_months_ago.strftime('%Y-%m-%d')]
    
    if recent:
        print(f"\n  Son 6 aydaki pattern'ler ({len(recent)} adet):")
        print(f"  {'Tarih':<14} {'Fiyat':<8} {'Pattern':<30} {'D1':>5} {'D2':>5} {'D6':>5}")
        print(f"  {'-'*14} {'-'*8} {'-'*30} {'-'*5} {'-'*5} {'-'*5}")
        for p in recent[-30:]:
            d1_i = "MOR" if p['d1'] > 0 else "PMBE"
            d2_i = "KRMZ" if p['d2'] > 0 else "TRNC"
            d6_i = "MAVI" if p['d6'] > 0 else "KHVE"
            print(f"  {p['date']:<14} {p['price']:<8.2f} {p['type']:<30} {d1_i:>5} {d2_i:>5} {d6_i:>5}")
    
    # 5. Surround pattern analizi
    print(f"\n{'='*70}")
    print(f"  SURROUND PATTERN ANALIZI (DAIRE ICINDEKI PATTERN)")
    print(f"{'='*70}")
    
    surrounds = [p for p in patterns_found if 'SURROUND' in str(p['type']) or 'CIRCLE' in str(p['type'])]
    print(f"  Toplam surround pattern: {len(surrounds)} adet")
    
    # Sirali olarak goster
    if len(surrounds) > 0:
        print(f"\n  Tum surround pattern'ler (kronolojik):")
        print(f"  {'Tarih':<14} {'Fiyat':<8} {'D1':>5} {'D2':>5} {'D6':>5} {'Bull':<5} {'Type'}")
        print(f"  {'-'*14} {'-'*8} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*25}")
        for s in surrounds:
            d1_i = "MOR" if s['d1'] > 0 else "PMBE"
            d2_i = "KRMZ" if s['d2'] > 0 else "TRNC"
            d6_i = "MAVI" if s['d6'] > 0 else "KHVE"
            print(f"  {s['date']:<14} {s['price']:<8.2f} {d1_i:>5} {d2_i:>5} {d6_i:>5} {s['bull']:<5} {s['type']}")
    
    # 6. Simdiki durum
    print(f"\n{'='*70}")
    print(f"  SMDIKI DURUM")
    print(f"{'='*70}")
    print(f"  Div1 (Uzun): {d1_c}")
    print(f"  Div2 (Orta): {d2_c}")
    print(f"  Div6 (Kisa): {d6_c}")
    
    if result.surround_type:
        print(f"\n  --> AKTIF SURROUND: {result.surround_icons}")
        print(f"  Bu pattern sistemde TANIMLI ve CALISIYOR.")
    else:
        print(f"\n  --> Su an aktif surround pattern yok.")
    
    # Analiz
    print(f"\n{'='*70}")
    print(f"  ANALIZ")
    print(f"{'='*70}")
    
    # Uzun donem trend
    if result.div1 > 0:
        print(f"  - Uzun trend (Div1): MOR yukari -- yukselis trendinde")
    else:
        print(f"  - Uzun trend (Div1): PEMBE asagi -- dusus trendinde")
    
    if result.div6 > 0:
        print(f"  - Kisa trend (Div6): MAVI yukari -- kisa vadeli yukselis")
    else:
        print(f"  - Kisa trend (Div6): KAHVE asagi -- kisa vadeli dusus")
    
    # Surround tespit
    if result.div1 > 0 and result.div6 > 0 and result.div2 < 0:
        print(f"\n  !! Div1(Mor+)+Div6(Mavi+) ayni yonde, Div2(Kirmizi-) ters!")
        print(f"  Bu sistemdeki BOGA SARMA (BULLISH SURROUND) patterni.")
        print(f"  Sistem zaten bunu algiliyor ve Telegram'a bildiriyor.")
    elif result.div1 < 0 and result.div6 < 0 and result.div2 > 0:
        print(f"\n  !! Div1(Pembe-)+Div6(Kahve-) ayni yonde, Div2(Kirmizi+) ters!")
        print(f"  Bu sistemdeki AYI SARMA (BEARISH SURROUND) patterni.")
        print(f"  Sistem zaten bunu algiliyor ve Telegram'a bildiriyor.")
    else:
        print(f"\n  Su an DGNMO'da aktif bir surround pattern yok.")
    
    print(f"\n{'='*70}")
    print(f"  SENIN YUVARLAK ICINDE GOSTERDIGIN PATTERN")
    print(f"{'='*70}")
    print(f"""
  Beyaz daire icindeki pattern'i ogrenmek icin 3 renk yeterli:

  Div1 (Mor/Pembe) --> ?
  Div2 (Kirmizi/Turuncu) --> ?
  Div6 (Mavi/Kahve) --> ?

  Ornek: "Mor yukari, Mavi yukari, Kirmizi asagi"
  --> Bu sistemdeki BOGA SARMA, zaten calisiyor!

  Yeni bir pattern varsa: "Mor yukari, Mavi asagi, Kirmizi yukari" gibi
  --> Sisteme EKLEYEYIM!

  Tek cumle yeter. Pattern'i gorur gormez Telegram bildirimi eklerim.
""")

if __name__ == "__main__":
    main()
