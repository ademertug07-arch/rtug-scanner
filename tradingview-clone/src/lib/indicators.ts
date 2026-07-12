import type { CandlestickData, LineData, HistogramData } from "lightweight-charts"

export type CandleWithVolume = CandlestickData & { volume: number }

export function calculateSMA(data: CandlestickData[], period: number): LineData[] {
  const result: LineData[] = []
  for (let i = period - 1; i < data.length; i++) {
    let sum = 0
    for (let j = i - period + 1; j <= i; j++) sum += data[j].close
    result.push({ time: data[i].time, value: sum / period })
  }
  return result
}

export function calculateEMA(data: CandlestickData[], period: number): LineData[] {
  const result: LineData[] = []
  const multiplier = 2 / (period + 1)
  let ema = data[0].close
  result.push({ time: data[0].time, value: ema })
  for (let i = 1; i < data.length; i++) {
    ema = (data[i].close - ema) * multiplier + ema
    result.push({ time: data[i].time, value: ema })
  }
  return result
}

export function calculateRSI(data: CandlestickData[], period: number): LineData[] {
  const result: LineData[] = []
  let gains = 0, losses = 0
  for (let i = 1; i <= period; i++) {
    const diff = data[i].close - data[i - 1].close
    if (diff >= 0) gains += diff; else losses -= diff
  }
  let avgGain = gains / period
  let avgLoss = losses / period
  let rs = avgLoss === 0 ? 100 : avgGain / avgLoss
  result.push({ time: data[period].time, value: 100 - 100 / (1 + rs) })

  for (let i = period + 1; i < data.length; i++) {
    const diff = data[i].close - data[i - 1].close
    const gain = diff >= 0 ? diff : 0
    const loss = diff < 0 ? -diff : 0
    avgGain = (avgGain * (period - 1) + gain) / period
    avgLoss = (avgLoss * (period - 1) + loss) / period
    rs = avgLoss === 0 ? 100 : avgGain / avgLoss
    result.push({ time: data[i].time, value: 100 - 100 / (1 + rs) })
  }
  return result
}

export function calculateMACD(data: CandlestickData[], fast: number, slow: number, signal: number) {
  const emaFast = calculateEMA(data, fast)
  const emaSlow = calculateEMA(data, slow)
  const macdLine: LineData[] = []
  for (let i = 0; i < Math.min(emaFast.length, emaSlow.length); i++) {
    macdLine.push({ time: emaFast[i].time, value: emaFast[i].value - emaSlow[i].value })
  }
  const signalLine = calculateEMAFromValues(macdLine, signal)
  const histogram: HistogramData[] = []
  for (let i = 0; i < Math.min(macdLine.length, signalLine.length); i++) {
    histogram.push({
      time: macdLine[i].time,
      value: macdLine[i].value - signalLine[i].value,
      color: macdLine[i].value - signalLine[i].value >= 0 ? "#089981" : "#f23645",
    })
  }
  return { macdLine, signalLine, histogram }
}

function calculateEMAFromValues(data: LineData[], period: number): LineData[] {
  const result: LineData[] = []
  const multiplier = 2 / (period + 1)
  let ema = data[0].value
  result.push({ time: data[0].time, value: ema })
  for (let i = 1; i < data.length; i++) {
    ema = (data[i].value - ema) * multiplier + ema
    result.push({ time: data[i].time, value: ema })
  }
  return result
}

export function calculateBollingerBands(data: CandlestickData[], period: number, stdDev: number) {
  const middle = calculateSMA(data, period)
  const upper: LineData[] = []
  const lower: LineData[] = []

  for (let i = 0; i < middle.length; i++) {
    const idx = i + period - 1
    let sumSq = 0
    for (let j = idx - period + 1; j <= idx; j++) sumSq += (data[j].close - middle[i].value) ** 2
    const std = Math.sqrt(sumSq / period)
    upper.push({ time: middle[i].time, value: middle[i].value + std * stdDev })
    lower.push({ time: middle[i].time, value: middle[i].value - std * stdDev })
  }
  return { middle, upper, lower }
}

export function calculateSuperTrend(data: CandlestickData[], atrPeriod: number, multiplier: number) {
  const result: LineData[] = []
  const atrValues = calculateATR(data, atrPeriod)
  let trend = 1
  let upper = 0, lower = 0

  for (let i = atrPeriod; i < data.length; i++) {
    const hl2 = (data[i].high + data[i].low) / 2
    const atrVal = atrValues[i - atrPeriod]
    const src = (data[i].high + data[i].low) / 2
    const prevUpperBand = upper
    const prevLowerBand = lower

    upper = src + multiplier * atrVal
    lower = src - multiplier * atrVal

    if (i === atrPeriod) {
      upper = upper
      lower = lower
    } else {
      upper = data[i].close > prevUpperBand ? Math.max(upper, prevUpperBand) : upper
      lower = data[i].close < prevLowerBand ? Math.min(lower, prevLowerBand) : lower
    }

    if (data[i].close > lower && trend === -1) {
      trend = 1
    } else if (data[i].close < upper && trend === 1) {
      trend = -1
    }

    const bandValue = trend === 1 ? lower : upper
    result.push({ time: data[i].time, value: bandValue })
  }
  return { superTrend: result, trend }
}

function calculateATR(data: CandlestickData[], period: number): number[] {
  const tr: number[] = []
  for (let i = 1; i < data.length; i++) {
    const hl = data[i].high - data[i].low
    const hc = Math.abs(data[i].high - data[i - 1].close)
    const lc = Math.abs(data[i].low - data[i - 1].close)
    tr.push(Math.max(hl, hc, lc))
  }
  const atr: number[] = []
  let sum = 0
  for (let i = 0; i < period; i++) sum += tr[i]
  atr.push(sum / period)
  for (let i = period; i < tr.length; i++) {
    atr.push((atr[atr.length - 1] * (period - 1) + tr[i]) / period)
  }
  return atr
}

export function calculateVWAP(data: CandleWithVolume[]): LineData[] {
  const result: LineData[] = []
  let cumVol = 0, cumVP = 0
  for (const d of data) {
    const typical = (d.high + d.low + d.close) / 3
    cumVP += typical * d.volume
    cumVol += d.volume
    result.push({ time: d.time, value: cumVP / cumVol })
  }
  return result
}

export function generateSampleData(count: number): CandleWithVolume[] {
  const data: CandleWithVolume[] = []
  let price = 45000
  let vol = 1000
  const now = Math.floor(Date.now() / 1000)
  for (let i = count; i >= 0; i--) {
    const change = price * (Math.random() - 0.48) * 0.02
    const open = price
    const close = price + change
    const high = Math.max(open, close) * (1 + Math.random() * 0.01)
    const low = Math.min(open, close) * (1 - Math.random() * 0.01)
    data.push({
      time: (now - i * 3600) as any,
      open: Math.round(open * 100) / 100,
      high: Math.round(high * 100) / 100,
      low: Math.round(low * 100) / 100,
      close: Math.round(close * 100) / 100,
      volume: Math.round(vol * (0.8 + Math.random() * 0.4)),
    })
    price = close
    vol = vol * (0.9 + Math.random() * 0.2)
  }
  return data
}
