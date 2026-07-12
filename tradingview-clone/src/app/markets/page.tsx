"use client"

import { useEffect, useState, useCallback } from "react"
import NavBar from "@/components/NavBar"

type MarketData = {
  symbol: string
  name: string
  price: number | null
  change: number | null
  changePercent: number | null
  volume: number | null
  high: number | null
  low: number | null
  open: number | null
  previousClose: number | null
  marketState: string | null
}

type MarketGroups = {
  indices: MarketData[]
  crypto: MarketData[]
  forex: MarketData[]
  commodities: MarketData[]
  turkish: MarketData[]
}

const TABS = ["Endeksler", "Kripto", "Forex", "Emtia", "Türk Hisse"] as const
type Tab = (typeof TABS)[number]

const TAB_GROUP: Record<Tab, keyof MarketGroups> = {
  Endeksler: "indices",
  Kripto: "crypto",
  Forex: "forex",
  Emtia: "commodities",
  "Türk Hisse": "turkish",
}

export default function MarketsPage() {
  const [data, setData] = useState<MarketGroups | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>("Endeksler")
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<string>("")

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch("/api/markets")
      const json = await res.json()
      if (!json.error) {
        setData(json)
        setLastUpdate(new Date().toLocaleTimeString("tr-TR"))
      }
    } catch (e) {
      console.error("Market fetch error:", e)
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 15000)
    return () => clearInterval(interval)
  }, [fetchData])

  const activeGroup = data ? data[TAB_GROUP[activeTab]] : []
  const sortedData = [...activeGroup].sort((a, b) => (a.price ?? 0) > (b.price ?? 0) ? -1 : 1)

  return (
    <>
      <NavBar />
      <div className="min-h-screen bg-black pt-24">
        <div className="mx-auto max-w-[1260px] px-4 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-[#f7f8f8]">Canlı Piyasalar</h1>
              {lastUpdate && (
                <p className="text-xs text-[#787b86] mt-1">Son güncelleme: {lastUpdate}</p>
              )}
            </div>
          </div>

          <div role="tablist" className="flex flex-wrap gap-2 mb-6">
            {TABS.map((tab) => (
              <button
                key={tab}
                role="tab"
                aria-selected={activeTab === tab}
                onClick={() => setActiveTab(tab)}
                className={`px-5 py-2 text-sm rounded-[14px] border transition-colors ${
                  activeTab === tab
                    ? "bg-[#2962ff] border-[#2962ff] text-white"
                    : "bg-[#2e2e2e] border-[#0f0f0f] text-white hover:bg-[#3a3a3a]"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#2962ff] border-t-transparent" />
            </div>
          ) : (
            <div className="rounded-lg border border-[#2a2e39] overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#2a2e39] bg-[#1e222d]">
                    <th className="px-4 py-3 text-left text-xs font-medium text-[#787b86] uppercase">Sembol</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-[#787b86] uppercase">İsim</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-[#787b86] uppercase">Fiyat</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-[#787b86] uppercase">Değişim</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-[#787b86] uppercase">%</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-[#787b86] uppercase">Hacim</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-[#787b86] uppercase">Yüksek</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-[#787b86] uppercase">Düşük</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedData.map((item) => {
                    const isPositive = (item.change ?? 0) >= 0
                    return (
                      <tr key={item.symbol} className="border-b border-[#2a2e39] hover:bg-[#1e222d] transition-colors">
                        <td className="px-4 py-3">
                          <a href={`/coin/${encodeURIComponent(item.symbol)}`} className="font-semibold text-[#f7f8f8] hover:text-[#2962ff] transition-colors">{item.symbol}</a>
                        </td>
                        <td className="px-4 py-3 text-[#787b86] max-w-[200px] truncate">{item.name}</td>
                        <td className="px-4 py-3 text-right font-semibold text-[#f7f8f8]">
                          {item.price?.toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? "—"}
                        </td>
                        <td className={`px-4 py-3 text-right font-medium ${isPositive ? "text-[#089981]" : "text-[#f23645]"}`}>
                          {item.change != null ? (isPositive ? "+" : "") + item.change.toFixed(2) : "—"}
                        </td>
                        <td className={`px-4 py-3 text-right font-medium ${isPositive ? "text-[#089981]" : "text-[#f23645]"}`}>
                          {item.changePercent != null ? (isPositive ? "+" : "") + item.changePercent.toFixed(2) + "%" : "—"}
                        </td>
                        <td className="px-4 py-3 text-right text-[#787b86]">
                          {item.volume != null ? (item.volume / 1000000).toFixed(1) + "M" : "—"}
                        </td>
                        <td className="px-4 py-3 text-right text-[#787b86]">
                          {item.high?.toFixed(2) ?? "—"}
                        </td>
                        <td className="px-4 py-3 text-right text-[#787b86]">
                          {item.low?.toFixed(2) ?? "—"}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          <p className="mt-4 text-[10px] text-[#434651] text-center">
            Veriler Yahoo Finance aracılığıyla sağlanmaktadır. 15 saniyede bir güncellenir. Gerçek zamanlı değildir.
          </p>
        </div>
      </div>
    </>
  )
}
