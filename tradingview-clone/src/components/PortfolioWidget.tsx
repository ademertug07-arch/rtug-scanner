"use client"

import { useEffect, useState, useCallback } from "react"

type PortfolioItem = {
  id: string
  symbol: string
  quantity: number
  avgPrice: number
}

type PriceMap = Record<string, { price: number; changePercent: number }>

export default function PortfolioWidget() {
  const [items, setItems] = useState<PortfolioItem[]>([])
  const [prices, setPrices] = useState<PriceMap>({})
  const [showForm, setShowForm] = useState(false)
  const [symbol, setSymbol] = useState("")
  const [quantity, setQuantity] = useState("")
  const [avgPrice, setAvgPrice] = useState("")

  const fetchPortfolio = useCallback(async () => {
    try {
      const res = await fetch("/api/portfolio")
      const data = await res.json()
      if (Array.isArray(data)) setItems(data)
    } catch {}
  }, [])

  useEffect(() => { fetchPortfolio() }, [fetchPortfolio])

  useEffect(() => {
    if (items.length === 0) return
    const symbols = items.map((i) => i.symbol)
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/markets`)
        const data = await res.json()
        if (data.error) return
        const priceMap: PriceMap = {}
        for (const key of ["indices", "crypto", "forex", "commodities", "turkish"] as const) {
          for (const item of data[key] || []) {
            if (item.price != null) {
              priceMap[item.symbol] = { price: item.price, changePercent: item.changePercent ?? 0 }
            }
          }
        }
        setPrices(priceMap)
      } catch {}
    }, 15000)
    return () => clearInterval(interval)
  }, [items])

  async function addPosition(e: React.FormEvent) {
    e.preventDefault()
    const res = await fetch("/api/portfolio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol: symbol.toUpperCase(), quantity: parseFloat(quantity), avgPrice: parseFloat(avgPrice) }),
    })
    if (res.ok) {
      setSymbol(""); setQuantity(""); setAvgPrice(""); setShowForm(false)
      fetchPortfolio()
    }
  }

  async function deletePosition(id: string) {
    await fetch(`/api/portfolio?id=${id}`, { method: "DELETE" })
    fetchPortfolio()
  }

  let totalPL = 0
  let totalCost = 0
  let totalValue = 0

  return (
    <div className="rounded-lg bg-[#1e222d] p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-[#f7f8f8]">Portföy</h2>
        <button onClick={() => setShowForm(!showForm)} className="text-xs text-[#2962ff] hover:text-[#1e53e5]">
          {showForm ? "İptal" : "+ Ekle"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={addPosition} className="mb-3 space-y-2 p-3 bg-[#131722] rounded-lg">
          <input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="Sembol (örn. BTC-USD)" className="w-full rounded border border-[#2a2e39] bg-[#0f0f0f] px-3 py-1.5 text-xs text-[#f7f8f8] outline-none focus:border-[#2962ff]" required />
          <div className="flex gap-2">
            <input type="number" step="any" value={quantity} onChange={(e) => setQuantity(e.target.value)} placeholder="Miktar" className="flex-1 rounded border border-[#2a2e39] bg-[#0f0f0f] px-3 py-1.5 text-xs text-[#f7f8f8] outline-none focus:border-[#2962ff]" required />
            <input type="number" step="any" value={avgPrice} onChange={(e) => setAvgPrice(e.target.value)} placeholder="Ort. maliyet" className="flex-1 rounded border border-[#2a2e39] bg-[#0f0f0f] px-3 py-1.5 text-xs text-[#f7f8f8] outline-none focus:border-[#2962ff]" required />
          </div>
          <button type="submit" className="w-full rounded bg-[#2962ff] py-1.5 text-xs font-medium text-white hover:bg-[#1e53e5]">Ekle</button>
        </form>
      )}

      {items.length === 0 ? (
        <p className="text-xs text-[#787b86]">Henüz portföy öğen yok. Sembol ekleyerek takip etmeye başla.</p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => {
            const current = prices[item.symbol]
            const currentPrice = current?.price ?? item.avgPrice
            const cost = item.quantity * item.avgPrice
            const value = item.quantity * currentPrice
            const pl = value - cost
            const plPercent = cost > 0 ? (pl / cost) * 100 : 0
            totalPL += pl
            totalCost += cost
            totalValue += value

            return (
              <div key={item.id} className="flex items-center justify-between px-2 py-1.5 rounded hover:bg-[#131722] text-xs">
                <div className="flex-1">
                  <span className="font-semibold text-[#f7f8f8]">{item.symbol}</span>
                  <span className="ml-2 text-[#787b86]">{item.quantity} adet</span>
                </div>
                <div className="text-right">
                  <div className="text-[#f7f8f8]">${value.toFixed(2)}</div>
                  <div className={`font-medium ${pl >= 0 ? "text-[#089981]" : "text-[#f23645]"}`}>
                    {pl >= 0 ? "+" : ""}${pl.toFixed(2)} ({plPercent >= 0 ? "+" : ""}{plPercent.toFixed(1)}%)
                  </div>
                </div>
                <button onClick={() => deletePosition(item.id)} className="ml-2 text-[#787b86] hover:text-[#f23645]">✕</button>
              </div>
            )
          })}
          <div className="border-t border-[#2a2e39] pt-2 mt-2">
            <div className="flex justify-between text-xs">
              <span className="text-[#787b86]">Toplam Maliyet</span>
              <span className="text-[#f7f8f8]">${totalCost.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-[#787b86]">Güncel Değer</span>
              <span className="text-[#f7f8f8]">${totalValue.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm font-semibold mt-1">
              <span className="text-[#787b86]">Toplam Kâr/Zarar</span>
              <span className={totalPL >= 0 ? "text-[#089981]" : "text-[#f23645]"}>
                {totalPL >= 0 ? "+" : ""}${totalPL.toFixed(2)} ({totalCost > 0 ? (totalPL / totalCost * 100).toFixed(1) : "0.0"}%)
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
