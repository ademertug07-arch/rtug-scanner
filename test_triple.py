import sys, numpy as np, pandas as pd, yfinance as yf
sys.path.insert(0, '.')
from rtug_scanner_core import RTUGSignalEngine, BreakoutType

df = yf.download("DGNMO.IS", period="2y", interval="1d")
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

close = np.asarray(df["Close"].values, dtype=float).flatten()
volume = np.asarray(df["Volume"].values, dtype=float).flatten()
dates = df.index.tolist()

engine = RTUGSignalEngine()

triples = []
for i in range(200, len(close)):
    r = engine.analyze(close[:i+1], volume[:i+1])
    if r.surround_type in [BreakoutType.TRIPLE_BULL, BreakoutType.TRIPLE_BEAR]:
        triples.append((dates[i], r.surround_type, r.bull_count, r.price, r.div1, r.div2, r.div6))

print(f"TRIPLE pattern bulunan gun sayisi: {len(triples)}")
print()
header = f"  {'Tarih':<14} {'Pattern':<22} {'Bull':<5} {'Fiyat':<8} {'Div1':>8} {'Div2':>8} {'Div6':>8}"
print(header)
print("  " + "-"*70)
for date, p, b, f, d1, d2, d6 in triples[-60:]:
    d1_c = "MOR UP" if d1 > 0 else "PMBE DN"
    d2_c = "KRMZ UP" if d2 > 0 else "TRNC DN"
    d6_c = "MAVI UP" if d6 > 0 else "KHVE DN"
    pname = "UCLU BOGA" if p == BreakoutType.TRIPLE_BULL else "UCLU AYI"
    ds = date.strftime("%Y-%m-%d")
    line = f"  {ds:<14} {pname:<22} {b:<5} {f:<8.2f} {d1_c:>8} {d2_c:>8} {d6_c:>8}"
    print(line)

# Son durum
r = engine.analyze(close, volume)
print(f"\nSON DURUM: {r.surround_type or 'YOK'} | {r.surround_icons}")
print(f"Div1: {r.div1:+.1f} | Div2: {r.div2:+.1f} | Div6: {r.div6:+.1f}")
