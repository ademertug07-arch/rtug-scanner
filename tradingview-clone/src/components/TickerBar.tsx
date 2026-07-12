"use client"

import { useEffect, useState, useRef } from "react"

type TickerItem = {
  symbol: string
  price: number | null
  changePercent: number | null
}

export default function TickerBar() {
  const [items, setItems] = useState<TickerItem[]>([])
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    async function fetchTicker() {
      try {
        const res = await fetch("/api/markets")
        const data = await res.json()
        if (data.error) return
        const all: TickerItem[] = []
        for (const key of ["indices", "crypto", "forex", "commodities", "turkish"] as const) {
          for (const item of data[key] || []) {
            if (item.price != null) all.push({ symbol: item.symbol, price: item.price, changePercent: item.changePercent })
          }
        }
        setItems(all.slice(0, 30))
      } catch {}
    }
    fetchTicker()
    const interval = setInterval(fetchTicker, 15000)
    return () => clearInterval(interval)
  }, [])

  if (items.length === 0) return null

  const doubled = [...items, ...items]

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-8 bg-[#131722] border-b border-[#2a2e39] overflow-hidden">
      <div ref={scrollRef} className="flex h-full">
        <div className="flex animate-ticker gap-0">
          {doubled.map((item, i) => {
            const isPositive = (item.changePercent ?? 0) >= 0
            return (
              <div key={`${item.symbol}-${i}`} className="flex items-center gap-2 px-3 whitespace-nowrap text-xs border-r border-[#2a2e39]">
                <span className="font-semibold text-[#f7f8f8]">{item.symbol}</span>
                <span className="text-[#f7f8f8]">{item.price?.toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                <span className={`font-medium ${isPositive ? "text-[#089981]" : "text-[#f23645]"}`}>
                  {isPositive ? "+" : ""}{item.changePercent?.toFixed(2)}%
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
