"""RTUG Scanner Core — Test"""
import sys, numpy as np
sys.path.insert(0, '.')
from rtug_scanner_core import RTUGSignalEngine, BreakoutType

np.random.seed(123)
bars = 300
close = 100 + np.cumsum(np.random.randn(bars) * 0.5)
volume = np.abs(np.random.randn(bars) * 1000000 + 5000000)

engine = RTUGSignalEngine()
result = engine.analyze(close, volume)

print("=== RTUG Core Test ===")
print(f"Breakout: {result.breakout_type or 'NONE'}")
print(f"Bull: {result.bull_count}/5 | Bear: {result.bear_count}/5")
print(f"OBV Norm: {result.obv_norm}")
print(f"Div1: {result.div1} | Div2: {result.div2} | Div3: {result.div3} | Div5: {result.div5} | Div6: {result.div6}")
print(f"Score: {result.score}/100")
print(f"Directions: {result.direction_icons}")
print(f"Has Signal: {result.has_signal}")
print()

# Bullish scenario
close2 = 100 + np.cumsum(np.random.randn(bars) * 0.3 + 0.1)
volume2 = np.abs(np.random.randn(bars) * 1000000 + 8000000)
result2 = engine.analyze(close2, volume2)
print("=== Bullish Senaryo ===")
print(f"Breakout: {result2.breakout_type or 'NONE'}")
print(f"Bull: {result2.bull_count}/5 | Bear: {result2.bear_count}/5")
print(f"Score: {result2.score}/100")

print()
print("OK")
