"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { createChart, CandlestickSeries, HistogramSeries, LineSeries, ColorType, type IChartApi, type ISeriesApi, type CandlestickData, type HistogramData, type LineData } from "lightweight-charts"
import NavBar from "@/components/NavBar"
import AlertManager from "@/components/AlertManager"
import PortfolioWidget from "@/components/PortfolioWidget"

const SYMBOLS = ["BTC-USD", "ETH-USD", "AAPL", "TSLA", "NVDA", "SPY", "QQQ", "EURUSD=X", "GC=F", "CL=F"] as const

type Range = "1d" | "5d" | "1mo" | "3mo" | "6mo" | "1y"

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const chartRef = useRef<HTMLDivElement>(null)
  const chartApiRef = useRef<IChartApi | null>(null)
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null)
  const smaSeriesRef = useRef<ISeriesApi<"Line"> | null>(null)
  const emaSeriesRef = useRef<ISeriesApi<"Line"> | null>(null)
  const [showSMA, setShowSMA] = useState(false)
  const [showEMA, setShowEMA] = useState(false)
  const [candleData, setCandleData] = useState<CandlestickData[]>([])
  const [symbol, setSymbol] = useState("BTC-USD")
  const [searchInput, setSearchInput] = useState("BTC-USD")
  const [range, setRange] = useState<Range>("1mo")
  const [quote, setQuote] = useState<any>(null)
  const [watchlist, setWatchlist] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (status === "unauthenticated") router.push("/login")
  }, [status, router])

  useEffect(() => {
    if (status !== "authenticated" || !chartRef.current) return

    const chart = createChart(chartRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#131722" },
        textColor: "#787b86",
      },
      grid: {
        vertLines: { color: "#2a2e39" },
        horzLines: { color: "#2a2e39" },
      },
      crosshair: { mode: 0 },
      rightPriceScale: { borderColor: "#2a2e39" },
      timeScale: { borderColor: "#2a2e39", timeVisible: true },
      width: chartRef.current.clientWidth,
      height: 500,
    })

    chartApiRef.current = chart

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#089981",
      downColor: "#f23645",
      borderDownColor: "#f23645",
      borderUpColor: "#089981",
      wickDownColor: "#f23645",
      wickUpColor: "#089981",
    })
    candleSeriesRef.current = candleSeries

    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: "#2962ff",
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    })
    volumeSeriesRef.current = volumeSeries

    const crosshairHandler = (param: import("lightweight-charts").MouseEventParams) => {
      if (param.time && volumeSeriesRef.current) {
        volumeSeriesRef.current.applyOptions({ color: "#2962ff" })
      }
    }
    chart.subscribeCrosshairMove(crosshairHandler)

    const handleResize = () => {
      if (chartRef.current) {
        chart.applyOptions({ width: chartRef.current.clientWidth })
      }
    }
    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      chart.unsubscribeCrosshairMove(crosshairHandler)
      chart.remove()
    }
  }, [status])

  const fetchData = useCallback(async (sym: string, rng: Range) => {
    setLoading(true)
    try {
      const [chartRes, quoteRes] = await Promise.all([
        fetch(`/api/market?symbol=${sym}&type=chart&range=${rng}`),
        fetch(`/api/market?symbol=${sym}&type=quote`),
      ])
      const chartData = await chartRes.json()
      const quoteData = await quoteRes.json()

      if (chartData?.quotes?.length && candleSeriesRef.current && volumeSeriesRef.current) {
        const candles: CandlestickData[] = []
        const volumes: HistogramData[] = []

        for (const q of chartData.quotes) {
          if (q.open && q.high && q.low && q.close && q.volume) {
            candles.push({
              time: Math.floor(new Date(q.date).getTime() / 1000) as any,
              open: q.open,
              high: q.high,
              low: q.low,
              close: q.close,
            })
            volumes.push({
              time: Math.floor(new Date(q.date).getTime() / 1000) as any,
              value: q.volume,
              color: q.close >= q.open ? "#089981" : "#f23645",
            })
          }
        }

        if (chartData.meta) {
          candleSeriesRef.current.setData(candles)
          volumeSeriesRef.current.setData(volumes)
          setCandleData(candles)
          chartApiRef.current?.timeScale().fitContent()
        }
      }
      setQuote(quoteData)
    } catch (e) {
      console.error("Failed to fetch data:", e)
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    if (!candleSeriesRef.current || candleData.length === 0) return
    const closes = candleData.map((c) => c.close)
    const times = candleData.map((c) => c.time)

    if (showSMA) {
      if (!smaSeriesRef.current) {
        smaSeriesRef.current = chartApiRef.current!.addSeries(LineSeries, { color: "#ff9800", lineWidth: 1, priceLineVisible: false, lastValueVisible: false })
      }
      const period = 20
      const smaData: LineData[] = []
      for (let i = period - 1; i < closes.length; i++) {
        let sum = 0
        for (let j = i - period + 1; j <= i; j++) sum += closes[j]
        smaData.push({ time: times[i] as any, value: sum / period })
      }
      smaSeriesRef.current.setData(smaData)
    } else if (smaSeriesRef.current) {
      smaSeriesRef.current.setData([])
    }

    if (showEMA) {
      if (!emaSeriesRef.current) {
        emaSeriesRef.current = chartApiRef.current!.addSeries(LineSeries, { color: "#2962ff", lineWidth: 1, priceLineVisible: false, lastValueVisible: false })
      }
      const period = 12
      const multiplier = 2 / (period + 1)
      const emaData: LineData[] = []
      let ema = closes[0]
      for (let i = 0; i < closes.length; i++) {
        if (i === 0) ema = closes[i]
        else ema = (closes[i] - ema) * multiplier + ema
        emaData.push({ time: times[i] as any, value: ema })
      }
      emaSeriesRef.current.setData(emaData)
    } else if (emaSeriesRef.current) {
      emaSeriesRef.current.setData([])
    }
  }, [showSMA, showEMA, candleData])

  useEffect(() => {
    if (status === "authenticated") fetchData(symbol, range)
  }, [symbol, range, status, fetchData])

  useEffect(() => {
    if (status !== "authenticated") return
    fetch("/api/watchlist").then((r) => r.json()).then((items) => {
      if (Array.isArray(items)) setWatchlist(items.map((i: any) => i.symbol))
    })
  }, [status])

  async function toggleWatchlist(sym: string) {
    if (watchlist.includes(sym)) {
      await fetch(`/api/watchlist?symbol=${sym}`, { method: "DELETE" })
      setWatchlist((prev) => prev.filter((s) => s !== sym))
    } else {
      await fetch("/api/watchlist", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ symbol: sym }) })
      setWatchlist((prev) => [...prev, sym])
    }
  }

  function handleSymbolSelect(sym: string) {
    setSymbol(sym)
    setSearchInput(sym)
  }

  if (status === "loading") {
    return <div className="flex min-h-screen items-center justify-center bg-black"><p className="text-[#787b86]">Yükleniyor...</p></div>
  }
  if (status !== "authenticated") return null

  return (
    <>
      <NavBar />
      <div className="min-h-screen bg-black pt-24">
        <div className="mx-auto max-w-[1260px] px-4 py-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-semibold text-[#f7f8f8]">Dashboard</h1>
            <div className="flex items-center gap-3">
              <span className="text-sm text-[#787b86]">{session.user?.email}</span>
              <button onClick={() => signOut({ callbackUrl: "/" })} className="text-xs text-[#787b86] hover:text-[#f23645]">
                Çıkış Yap
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mb-4">
            {SYMBOLS.map((sym) => (
              <button
                key={sym}
                onClick={() => handleSymbolSelect(sym)}
                className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                  symbol === sym
                    ? "bg-[#2962ff] border-[#2962ff] text-white"
                    : "bg-[#2e2e2e] border-[#0f0f0f] text-[#f7f8f8] hover:bg-[#3a3a3a]"
                }`}
              >
                {sym}
              </button>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-2 mb-4">
            <div className="relative flex-1 max-w-xs">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSymbolSelect(searchInput)}
                placeholder="Sembol ara (örn. AAPL)"
                className="w-full rounded-md border border-[#2a2e39] bg-[#1e222d] px-3 py-2 text-sm text-[#f7f8f8] outline-none focus:border-[#2962ff]"
              />
            </div>
            <button
              onClick={() => toggleWatchlist(symbol)}
              className={`px-3 py-2 text-sm rounded-md transition-colors ${
                watchlist.includes(symbol)
                  ? "bg-[#089981]/20 text-[#089981]"
                  : "bg-[#2e2e2e] text-[#787b86] hover:text-[#f7f8f8]"
              }`}
            >
              {watchlist.includes(symbol) ? "★ İzlendi" : "☆ İzle"}
            </button>
            {(["1d", "5d", "1mo", "3mo", "6mo", "1y"] as Range[]).map((r) => (
              <button
                key={r}
                onClick={() => setRange(r)}
                className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                  range === r
                    ? "bg-[#2962ff] border-[#2962ff] text-white"
                    : "bg-[#2e2e2e] border-[#0f0f0f] text-[#787b86] hover:text-[#f7f8f8]"
                }`}
              >
                {r}
              </button>
            ))}
            <div className="w-px h-5 bg-[#2a2e39]" />
            <button
              onClick={() => setShowSMA(!showSMA)}
              className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                showSMA
                  ? "bg-[#ff9800] border-[#ff9800] text-white"
                  : "bg-[#2e2e2e] border-[#0f0f0f] text-[#787b86] hover:text-[#f7f8f8]"
              }`}
            >
              SMA 20
            </button>
            <button
              onClick={() => setShowEMA(!showEMA)}
              className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                showEMA
                  ? "bg-[#2962ff] border-[#2962ff] text-white"
                  : "bg-[#2e2e2e] border-[#0f0f0f] text-[#787b86] hover:text-[#f7f8f8]"
              }`}
            >
              EMA 12
            </button>
          </div>

          {quote && (
            <div className="flex items-baseline gap-3 mb-4">
              <span className="text-3xl font-semibold text-[#f7f8f8]">
                {quote.regularMarketPrice?.toFixed(2) || "—"}
              </span>
              <span className={`text-sm font-medium ${(quote.regularMarketChangePercent || 0) >= 0 ? "text-[#089981]" : "text-[#f23645]"}`}>
                {(quote.regularMarketChangePercent || 0) >= 0 ? "+" : ""}{(quote.regularMarketChangePercent || 0)?.toFixed(2)}%
              </span>
              <span className="text-xs text-[#787b86]">
                {quote.regularMarketVolume ? `Hacim: ${(quote.regularMarketVolume / 1000000).toFixed(1)}M` : ""}
              </span>
            </div>
          )}

          <div className="rounded-lg bg-[#131722] overflow-hidden">
            <div ref={chartRef} />
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            <div className="rounded-lg bg-[#1e222d] p-4">
              <h2 className="text-sm font-semibold text-[#f7f8f8] mb-3">İzleme Listem</h2>
              {watchlist.length === 0 ? (
                <p className="text-xs text-[#787b86]">Henüz sembol eklemedin. Sembollere tıklayarak izleme listene ekleyebilirsin.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {watchlist.map((sym) => (
                    <button
                      key={sym}
                      onClick={() => handleSymbolSelect(sym)}
                      className="px-3 py-1 text-sm rounded-full bg-[#2e2e2e] text-[#f7f8f8] hover:bg-[#3a3a3a] transition-colors"
                    >
                      {sym}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-lg bg-[#1e222d] p-4">
              <h2 className="text-sm font-semibold text-[#f7f8f8] mb-3">Hızlı Bilgiler</h2>
              {quote ? (
                <div className="space-y-2 text-xs text-[#787b86]">
                  <div className="flex justify-between"><span>Açılış</span><span className="text-[#f7f8f8]">{quote.regularMarketOpen?.toFixed(2) || "—"}</span></div>
                  <div className="flex justify-between"><span>Günlük Yüksek</span><span className="text-[#f7f8f8]">{quote.regularMarketDayHigh?.toFixed(2) || "—"}</span></div>
                  <div className="flex justify-between"><span>Günlük Düşük</span><span className="text-[#f7f8f8]">{quote.regularMarketDayLow?.toFixed(2) || "—"}</span></div>
                  <div className="flex justify-between"><span>Kapanış</span><span className="text-[#f7f8f8]">{quote.regularMarketPreviousClose?.toFixed(2) || "—"}</span></div>
                  <div className="flex justify-between"><span>52 Hafta Yüksek</span><span className="text-[#f7f8f8]">{quote.fiftyTwoWeekHigh?.toFixed(2) || "—"}</span></div>
                  <div className="flex justify-between"><span>52 Hafta Düşük</span><span className="text-[#f7f8f8]">{quote.fiftyTwoWeekLow?.toFixed(2) || "—"}</span></div>
                </div>
              ) : (
                <p className="text-xs text-[#787b86]">Veri yükleniyor...</p>
              )}
            </div>
            <AlertManager currentPrice={quote?.regularMarketPrice ?? null} currentSymbol={symbol} />
            <PortfolioWidget />
          </div>
        </div>
      </div>
    </>
  )
}
