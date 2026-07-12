"use client"

import { useEffect, useRef, useState } from "react"
import { useParams } from "next/navigation"
import { createChart, CandlestickSeries, HistogramSeries, LineSeries, ColorType, type IChartApi, type ISeriesApi, type CandlestickData } from "lightweight-charts"
import NavBar from "@/components/NavBar"

type Range = "1d" | "5d" | "1mo" | "3mo" | "6mo" | "1y"

export default function CoinDetailPage() {
  const { symbol } = useParams<{ symbol: string }>()
  const sym = decodeURIComponent(symbol || "BTC-USD")
  const chartRef = useRef<HTMLDivElement>(null)
  const chartApiRef = useRef<IChartApi | null>(null)
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  const [quote, setQuote] = useState<any>(null)
  const [range, setRange] = useState<Range>("1mo")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!chartRef.current) return
    const chart = createChart(chartRef.current, {
      layout: { background: { type: ColorType.Solid, color: "#131722" }, textColor: "#787b86" },
      grid: { vertLines: { color: "#2a2e39" }, horzLines: { color: "#2a2e39" } },
      rightPriceScale: { borderColor: "#2a2e39" },
      timeScale: { borderColor: "#2a2e39", timeVisible: true },
      width: chartRef.current.clientWidth,
      height: 500,
    })
    chartApiRef.current = chart
    candleSeriesRef.current = chart.addSeries(CandlestickSeries, {
      upColor: "#089981", downColor: "#f23645", borderDownColor: "#f23645", borderUpColor: "#089981", wickDownColor: "#f23645", wickUpColor: "#089981",
    })
    const volumeSeries = chart.addSeries(HistogramSeries, { color: "#2962ff", priceFormat: { type: "volume" }, priceScaleId: "volume" })

    const handleResize = () => { chart.applyOptions({ width: chartRef.current!.clientWidth }) }
    window.addEventListener("resize", handleResize)

    async function fetchData() {
      try {
        const [chartRes, quoteRes] = await Promise.all([fetch(`/api/market?symbol=${sym}&type=chart&range=${range}`), fetch(`/api/market?symbol=${sym}&type=quote`)])
        const chartData = await chartRes.json()
        const quoteData = await quoteRes.json()
        setQuote(quoteData)

        if (chartData?.quotes?.length && candleSeriesRef.current) {
          const candles: CandlestickData[] = []
          for (const q of chartData.quotes) {
            if (q.open && q.high && q.low && q.close) {
              candles.push({ time: Math.floor(new Date(q.date).getTime() / 1000) as any, open: q.open, high: q.high, low: q.low, close: q.close })
              const v = { time: Math.floor(new Date(q.date).getTime() / 1000) as any, value: q.volume || 0, color: q.close >= q.open ? "#089981" : "#f23645" }
              try { volumeSeries.update(v) } catch { volumeSeries.setData([v]) }
            }
          }
          if (chartData.meta) { candleSeriesRef.current.setData(candles); chart.timeScale().fitContent() }
        }
      } catch (e) { console.error(e) }
      setLoading(false)
    }
    fetchData()

    return () => { window.removeEventListener("resize", handleResize); chart.remove() }
  }, [sym, range])

  return (
    <>
      <NavBar />
      <div className="min-h-screen bg-black pt-24">
        <div className="mx-auto max-w-[1260px] px-4 py-6">
          <div className="flex items-baseline gap-3 mb-4">
            <h1 className="text-2xl font-semibold text-[#f7f8f8]">{sym}</h1>
            {quote && (
              <>
                <span className="text-3xl font-semibold text-[#f7f8f8]">{quote.regularMarketPrice?.toFixed(2) || "—"}</span>
                <span className={`text-sm font-medium ${(quote.regularMarketChangePercent || 0) >= 0 ? "text-[#089981]" : "text-[#f23645]"}`}>
                  {(quote.regularMarketChangePercent || 0) >= 0 ? "+" : ""}{quote.regularMarketChangePercent?.toFixed(2)}%
                </span>
                <span className="text-xs text-[#787b86]">
                  {quote.regularMarketVolume ? `Hacim: ${(quote.regularMarketVolume / 1000000).toFixed(1)}M` : ""}
                </span>
              </>
            )}
          </div>

          <div className="flex gap-2 mb-4">
            {(["1d", "5d", "1mo", "3mo", "6mo", "1y"] as Range[]).map((r) => (
              <button key={r} onClick={() => setRange(r)}
                className={`px-3 py-1 text-xs rounded-full border transition-colors ${range === r ? "bg-[#2962ff] border-[#2962ff] text-white" : "bg-[#2e2e2e] border-[#0f0f0f] text-[#787b86] hover:text-[#f7f8f8]"}`}
              >{r}</button>
            ))}
          </div>

          <div className="rounded-lg bg-[#131722] overflow-hidden mb-6">
            <div ref={chartRef} />
          </div>

          {quote && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: "Açılış", value: quote.regularMarketOpen?.toFixed(2) },
                { label: "Günlük Yüksek", value: quote.regularMarketDayHigh?.toFixed(2) },
                { label: "Günlük Düşük", value: quote.regularMarketDayLow?.toFixed(2) },
                { label: "Kapanış", value: quote.regularMarketPreviousClose?.toFixed(2) },
                { label: "52 Hafta Yüksek", value: quote.fiftyTwoWeekHigh?.toFixed(2) },
                { label: "52 Hafta Düşük", value: quote.fiftyTwoWeekLow?.toFixed(2) },
                { label: "Hacim", value: quote.regularMarketVolume ? `${(quote.regularMarketVolume / 1000000).toFixed(1)}M` : "—" },
                { label: "Piyasa Değeri", value: quote.marketCap ? `$${(quote.marketCap / 1000000000).toFixed(2)}B` : "—" },
              ].map((s) => (
                <div key={s.label} className="rounded-lg bg-[#1e222d] p-3">
                  <p className="text-[10px] text-[#787b86] uppercase">{s.label}</p>
                  <p className="text-sm font-semibold text-[#f7f8f8] mt-1">{s.value ?? "—"}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
