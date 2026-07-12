import { PrismaClient } from "@prisma/client"
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3"

const adapter = new PrismaBetterSqlite3({ url: "file:./dev.db" })
const prisma = new PrismaClient({ adapter })

const TEMPLATES = [
  {
    name: "SMA Crossover",
    description: "İki hareketli ortalamanın kesişimine göre al/sat sinyali üretir",
    category: "strategy",
    isTemplate: true,
    code: `//@version=5
strategy("SMA Crossover", overlay=true, initial_capital=10000)

// Inputs
fastLen = input.int(9, "Hızlı SMA Periyodu")
slowLen = input.int(21, "Yavaş SMA Periyodu")

// Calculations
fastSMA = ta.sma(close, fastLen)
slowSMA = ta.sma(close, slowLen)

// Signals
buySignal = ta.crossover(fastSMA, slowSMA)
sellSignal = ta.crossunder(fastSMA, slowSMA)

// Strategy
if (buySignal)
    strategy.entry("Long", strategy.long)
if (sellSignal)
    strategy.entry("Short", strategy.short)

// Plot
plot(fastSMA, "Hızlı SMA", color=#2962FF)
plot(slowSMA, "Yavaş SMA", color=#F23645)

// Alerts
alertcondition(buySignal, "AL Sinyali", "{{ticker}} için AL sinyali oluştu")
alertcondition(sellSignal, "SAT Sinyali", "{{ticker}} için SAT sinyali oluştu")`,
  },
  {
    name: "RSI",
    description: "Göreceli Güç Endeksi - aşırı alım/satım bölgelerini gösterir",
    category: "indicator",
    isTemplate: true,
    code: `//@version=5
indicator("RSI", format=format.price, precision=2)

// Inputs
rsiLen = input.int(14, "RSI Periyodu")
obLevel = input.int(70, "Aşırı Alım", group="Seviyeler")
osLevel = input.int(30, "Aşırı Satım", group="Seviyeler")

// Calculation
rsiValue = ta.rsi(close, rsiLen)

// Plot
hline(obLevel, "Aşırı Alım", color=#F23645, linestyle=hline.style_dashed)
hline(50, "Orta", color=#787B86, linestyle=hline.style_dotted)
hline(osLevel, "Aşırı Satım", color=#089981, linestyle=hline.style_dashed)
plot(rsiValue, "RSI", color=#7F77DD)

// Signals
overbought = rsiValue >= obLevel
oversold = rsiValue <= osLevel

bgcolor(overbought ? color.new(#F23645, 85) : na)
bgcolor(oversold ? color.new(#089981, 85) : na)

alertcondition(overbought, "Aşırı Alım", "{{ticker}} aşırı alım bölgesinde")
alertcondition(oversold, "Aşırı Satım", "{{ticker}} aşırı satım bölgesinde")`,
  },
  {
    name: "MACD",
    description: "Hareketli Ortalama Yakınsama Iraksama - trend takip ve momentum göstergesi",
    category: "indicator",
    isTemplate: true,
    code: `//@version=5
indicator("MACD", format=format.price, precision=4)

// Inputs
fastLen = input.int(12, "Hızlı EMA Periyodu")
slowLen = input.int(26, "Yavaş EMA Periyodu")
signalLen = input.int(9, "Sinyal Periyodu")

// Calculation
[macdLine, signalLine, histLine] = ta.macd(close, fastLen, slowLen, signalLen)

// Plot
plot(macdLine, "MACD", color=#2962FF)
plot(signalLine, "Sinyal", color=#F23645)
hline(0, "Sıfır", color=#787B86, linestyle=hline.style_dotted)

// Histogram
plot(histLine, "Histogram", style=plot.style_histogram, color=histLine >= 0 ? #089981 : #F23645)

// Signals
crossOver = ta.crossover(macdLine, signalLine)
crossUnder = ta.crossunder(macdLine, signalLine)

alertcondition(crossOver, "MACD AL", "{{ticker}} MACD yukarı kesişim")
alertcondition(crossUnder, "MACD SAT", "{{ticker}} MACD aşağı kesişim")`,
  },
  {
    name: "Bollinger Bands",
    description: "Bollinger Bandları - volatilite tabanlı fiyat kanalları",
    category: "indicator",
    isTemplate: true,
    code: `//@version=5
indicator("Bollinger Bands", overlay=true)

// Inputs
bbLen = input.int(20, "Periyot")
bbStd = input.float(2.0, "Standart Sapma")
bbSrc = input.source(close, "Kaynak")

// Calculation
[bbMiddle, bbUpper, bbLower] = ta.bb(bbSrc, bbLen, bbStd)

// Plot
p1 = plot(bbUpper, "Üst Bant", color=#2962FF)
p2 = plot(bbMiddle, "Orta Bant", color=#2962FF, linewidth=2)
p3 = plot(bbLower, "Alt Bant", color=#2962FF)
fill(p1, p3, color=color.new(#2962FF, 90))

// Signals
breakoutUp = close > bbUpper
breakoutDown = close < bbLower
squeeze = ta.atr(14) < ta.sma(ta.atr(14), 20)

alertcondition(breakoutUp, "Yukarı Kırılım", "{{ticker}} üst banda kırdı")
alertcondition(breakoutDown, "Aşağı Kırılım", "{{ticker}} alt banda kırdı")
alertcondition(squeeze, "Sıkışma", "{{ticker}} volatilite sıkışması")`,
  },
  {
    name: "Ichimoku Cloud",
    description: "İchimoku Bulutu - trend yönü, destek/direnç ve momentum analizi",
    category: "indicator",
    isTemplate: true,
    code: `//@version=5
indicator("Ichimoku Cloud", overlay=true)

// Inputs
convPeriod = input.int(9, "Dönüşüm Periyodu")
basePeriod = input.int(26, "Temel Periyodu")
spanPeriod = input.int(52, "Öncü Periyodu")
displacement = input.int(26, "Kaydırma")

// Calculation
tenkan = (ta.highest(high, convPeriod) + ta.lowest(low, convPeriod)) / 2
kijun = (ta.highest(high, basePeriod) + ta.lowest(low, basePeriod)) / 2
spanA = (tenkan + kijun) / 2
spanB = (ta.highest(high, spanPeriod) + ta.lowest(low, spanPeriod)) / 2

// Plot
plot(tenkan, "Tenkan-sen", color=#2962FF)
plot(kijun, "Kijun-sen", color=#F23645)
plot(spanA, "Span A", color=#089981, offset=displacement)
plot(spanB, "Span B", color=#F23645, offset=displacement)
fill(plot(spanA, offset=displacement), plot(spanB, offset=displacement), color=spanA > spanB ? color.new(#089981, 85) : color.new(#F23645, 85), offset=displacement)

// Signals
bullish = ta.crossover(tenkan, kijun)
bearish = ta.crossunder(tenkan, kijun)
aboveCloud = close > spanA and close > spanB

alertcondition(bullish, "Boğa Sinyali", "{{ticker}} boğa sinyali")
alertcondition(bearish, "Ayı Sinyali", "{{ticker}} ayı sinyali")`,
  },
  {
    name: "SuperTrend",
    description: "Trend takip göstergesi - volatilite bazlı al/sat sinyalleri",
    category: "indicator",
    isTemplate: true,
    code: `//@version=5
indicator("SuperTrend", overlay=true)

// Inputs
atrPeriod = input.int(10, "ATR Periyodu")
atrMultiplier = input.float(3.0, "ATR Çarpanı")

// Calculation
[supertrend, direction] = ta.supertrend(atrMultiplier, atrPeriod)

// Plot
plot(supertrend, "SuperTrend", color=direction > 0 ? #089981 : #F23645, linewidth=2, style=plot.style_linebr)

// Background
bgcolor(direction > 0 ? color.new(#089981, 90) : color.new(#F23645, 90), title="Trend Arkaplan")

// Signals
buySignal = direction > 0 and direction[1] < 0
sellSignal = direction < 0 and direction[1] > 0

alertcondition(buySignal, "AL Sinyali", "{{ticker}} SuperTrend AL")
alertcondition(sellSignal, "SAT Sinyali", "{{ticker}} SuperTrend SAT")

plotshape(buySignal, "AL", style=shape.triangleup, location=location.belowbar, color=#089981, size=size.small)
plotshape(sellSignal, "SAT", style=shape.triangledown, location=location.abovebar, color=#F23645, size=size.small)`,
  },
  {
    name: "Volume Profile",
    description: "Hacim profili - fiyat seviyelerindeki işlem hacmini gösterir",
    category: "indicator",
    isTemplate: true,
    code: `//@version=5
indicator("Volume Profile", overlay=true)

// Inputs
numRows = input.int(24, "Satır Sayısı")

// Volume bars
volAbove = volume * (close > open ? 1 : 0)
volBelow = volume * (close < open ? 1 : 0)

// Plot volume as histogram on price
plotshape(volAbove > 0, "", style=shape.circle, location=location.abovebar, color=#089981, size=size.tiny)
plotshape(volBelow > 0, "", style=shape.circle, location=location.belowbar, color=#F23645, size=size.tiny)

// VWAP
vwapValue = ta.vwap(hlc3)
plot(vwap, "VWAP", color=#7F77DD, linewidth=2)

// Volume Weighted MA
vwma20 = ta.vwma(close, 20)
plot(vwma20, "VWMA 20", color=#FF9800, linewidth=1)`,
  },
  {
    name: "EMA Crossover with Alerts",
    description: "EMA kesişim stratejisi - 9 ve 21 EMA ile al/sat sinyalleri",
    category: "strategy",
    isTemplate: true,
    code: `//@version=5
strategy("EMA Crossover", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100)

// Inputs
emaFast = input.int(9, "Hızlı EMA")
emaSlow = input.int(21, "Yavaş EMA")
useFilter = input.bool(true, "Trend Filtresi Kullan", group="Filtre")
filterMA = input.int(200, "Filtre MA Periyodu", group="Filtre")

// Calculations
fastEMA = ta.ema(close, emaFast)
slowEMA = ta.ema(close, emaSlow)
trendFilter = ta.sma(close, filterMA)

// Signals
longCondition = ta.crossover(fastEMA, slowEMA)
shortCondition = ta.crossunder(fastEMA, slowEMA)

// Filter
trendUp = close > trendFilter

if (longCondition and (not useFilter or trendUp))
    strategy.entry("EMA Long", strategy.long)

if (shortCondition)
    strategy.entry("EMA Short", strategy.short)

// Plot
plot(fastEMA, "Hızlı EMA", color=#2962FF, linewidth=2)
plot(slowEMA, "Yavaş EMA", color=#F23645, linewidth=2)
plot(useFilter ? trendFilter : na, "Trend Filtre", color=#787B86, linewidth=1)

alertcondition(longCondition, "EMA AL", "{{ticker}} EMA AL")
alertcondition(shortCondition, "EMA SAT", "{{ticker}} EMA SAT")`,
  },
  {
    name: "Stochastic RSI",
    description: "Stokastik RSI - RSI'nın aşırı alım/satım bölgelerini momentumla birleştirir",
    category: "indicator",
    isTemplate: true,
    code: `//@version=5
indicator("Stochastic RSI", format=format.price, precision=2)

// Inputs
smoothK = input.int(3, "K Yumuşatma")
smoothD = input.int(3, "D Yumuşatma")
lengthRSI = input.int(14, "RSI Periyodu")
lengthStoch = input.int(14, "Stokastik Periyodu")
obLevel = input.int(80, "Aşırı Alım")
osLevel = input.int(20, "Aşırı Satım")

// Calculation
kValue = ta.stochrsi(close, lengthRSI, lengthStoch, smoothK, smoothD)

// Plot
hline(obLevel, "Aşırı Alım", color=#F23645, linestyle=hline.style_dashed)
hline(50, "Orta", color=#787B86, linestyle=hline.style_dotted)
hline(osLevel, "Aşırı Satım", color=#089981, linestyle=hline.style_dashed)

plot(kValue, "Stoch RSI K", color=#7F77DD, linewidth=2)

// Signals
crossUp = ta.crossover(kValue, osLevel)
crossDown = ta.crossunder(kValue, obLevel)

bgcolor(crossUp ? color.new(#089981, 85) : na)
bgcolor(crossDown ? color.new(#F23645, 85) : na)

alertcondition(crossUp and kValue < 50, "StochRSI AL", "{{ticker}} StochRSI al sinyali")
alertcondition(crossDown and kValue > 50, "StochRSI SAT", "{{ticker}} StochRSI sat sinyali")`,
  },
  {
    name: "VWAP + Support/Resistance",
    description: "VWAP ile günlük destek/direnç seviyeleri",
    category: "indicator",
    isTemplate: true,
    code: `//@version=5
indicator("VWAP + S/R", overlay=true)

// Inputs
showVWAP = input.bool(true, "VWAP Göster", group="VWAP")
showPivot = input.bool(true, "Pivot Göster", group="Destek/Direnç")
pivotLen = input.int(5, "Pivot Derinliği", group="Destek/Direnç")

// VWAP
vwapValue = ta.vwap(hlc3)
plot(showVWAP ? vwapValue : na, "VWAP", color=#7F77DD, linewidth=2)

// Daily Pivot Points
pivotHigh = ta.pivothigh(high, pivotLen, pivotLen)
pivotLow = ta.pivotlow(low, pivotLen, pivotLen)

// Support/Resistance levels
resistance = ta.valuewhen(pivotHigh, high[pivotLen], 0)
support = ta.valuewhen(pivotLow, low[pivotLen], 0)

plot(showPivot ? resistance : na, "Direnç", color=#F23645, linewidth=1, style=plot.style_circles)
plot(showPivot ? support : na, "Destek", color=#089981, linewidth=1, style=plot.style_circles)

// Alerts
alertcondition(close > resistance, "Direnç Kırılımı", "{{ticker}} direnç seviyesini kırdı")
alertcondition(close < support, "Destek Kırılımı", "{{ticker}} destek seviyesini kırdı")`,
  },
]

async function main() {
  console.log("Seeding Pine Script templates...")

  for (const tmpl of TEMPLATES) {
    await prisma.script.upsert({
      where: { id: `template-${tmpl.name.toLowerCase().replace(/\s+/g, "-")}` },
      update: { code: tmpl.code, description: tmpl.description, category: tmpl.category },
      create: {
        id: `template-${tmpl.name.toLowerCase().replace(/\s+/g, "-")}`,
        name: tmpl.name,
        description: tmpl.description,
        code: tmpl.code,
        category: tmpl.category,
        isTemplate: true,
      },
    })
    console.log(`  ✓ ${tmpl.name}`)
  }

  console.log("Seeding complete!")
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
