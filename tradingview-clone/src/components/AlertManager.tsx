"use client"

import { useEffect, useState, useCallback } from "react"

type Alert = {
  id: string
  symbol: string
  targetPrice: number
  direction: string
  note: string | null
  triggered: boolean
  createdAt: string
}

export default function AlertManager({ currentPrice, currentSymbol }: { currentPrice: number | null; currentSymbol: string }) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [targetPrice, setTargetPrice] = useState("")
  const [direction, setDirection] = useState<"above" | "below">("above")
  const [note, setNote] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [triggeredMsgs, setTriggeredMsgs] = useState<string[]>([])

  const fetchAlerts = useCallback(async () => {
    try {
      const res = await fetch("/api/alerts")
      const data = await res.json()
      if (Array.isArray(data)) setAlerts(data)
    } catch {}
  }, [])

  useEffect(() => { fetchAlerts() }, [fetchAlerts])

  useEffect(() => {
    if (currentPrice == null) return
    for (const alert of alerts) {
      if (alert.triggered || alert.symbol !== currentSymbol) continue
      const hit = alert.direction === "above"
        ? currentPrice >= alert.targetPrice
        : currentPrice <= alert.targetPrice
      if (hit) {
        const msg = `${alert.symbol} ${alert.direction === "above" ? "üstüne çıktı" : "altına indi"}: $${alert.targetPrice} (şu an $${currentPrice.toFixed(2)})`
        setTriggeredMsgs((prev) => [msg, ...prev].slice(0, 5))
        fetch("/api/alerts", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: alert.id, triggered: true }) })
        fetchAlerts()
      }
    }
  }, [currentPrice, alerts, currentSymbol, fetchAlerts])

  async function createAlert(e: React.FormEvent) {
    e.preventDefault()
    const res = await fetch("/api/alerts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol: currentSymbol, targetPrice: parseFloat(targetPrice), direction, note }),
    })
    if (res.ok) {
      setTargetPrice(""); setNote(""); setShowForm(false)
      fetchAlerts()
    }
  }

  async function deleteAlert(id: string) {
    await fetch(`/api/alerts?id=${id}`, { method: "DELETE" })
    fetchAlerts()
  }

  const activeAlerts = alerts.filter((a) => !a.triggered && a.symbol === currentSymbol)

  return (
    <div className="rounded-lg bg-[#1e222d] p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-[#f7f8f8]">
          Alarmlar {activeAlerts.length > 0 && <span className="text-[#787b86] font-normal">({activeAlerts.length})</span>}
        </h2>
        <button onClick={() => setShowForm(!showForm)} className="text-xs text-[#2962ff] hover:text-[#1e53e5]">
          {showForm ? "İptal" : "+ Yeni Alarm"}
        </button>
      </div>

      {triggeredMsgs.length > 0 && (
        <div className="mb-3 space-y-1">
          {triggeredMsgs.map((msg, i) => (
            <p key={i} className="text-xs text-[#f23645] bg-[#f23645]/10 px-2 py-1 rounded">{msg}</p>
          ))}
        </div>
      )}

      {showForm && (
        <form onSubmit={createAlert} className="mb-3 space-y-2 p-3 bg-[#131722] rounded-lg">
          <p className="text-xs text-[#787b86]">{currentSymbol} için alarm</p>
          <div className="flex gap-2">
            <button type="button" onClick={() => setDirection("above")} className={`px-3 py-1 text-xs rounded-full ${direction === "above" ? "bg-[#089981] text-white" : "bg-[#2e2e2e] text-[#787b86]"}`}>Üstünde</button>
            <button type="button" onClick={() => setDirection("below")} className={`px-3 py-1 text-xs rounded-full ${direction === "below" ? "bg-[#f23645] text-white" : "bg-[#2e2e2e] text-[#787b86]"}`}>Altında</button>
          </div>
          <input type="number" step="any" value={targetPrice} onChange={(e) => setTargetPrice(e.target.value)} placeholder="Hedef fiyat" className="w-full rounded border border-[#2a2e39] bg-[#0f0f0f] px-3 py-1.5 text-xs text-[#f7f8f8] outline-none focus:border-[#2962ff]" required />
          <input type="text" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Not (opsiyonel)" className="w-full rounded border border-[#2a2e39] bg-[#0f0f0f] px-3 py-1.5 text-xs text-[#f7f8f8] outline-none focus:border-[#2962ff]" />
          <button type="submit" className="w-full rounded bg-[#2962ff] py-1.5 text-xs font-medium text-white hover:bg-[#1e53e5]">Alarm Oluştur</button>
        </form>
      )}

      {activeAlerts.length === 0 ? (
        <p className="text-xs text-[#787b86]">Henüz alarm yok.</p>
      ) : (
        <div className="space-y-1 max-h-40 overflow-y-auto">
          {activeAlerts.map((alert) => (
            <div key={alert.id} className="flex items-center justify-between px-2 py-1.5 rounded hover:bg-[#131722] text-xs">
              <div>
                <span className="text-[#f7f8f8] font-medium">{alert.symbol}</span>
                <span className={`ml-2 ${alert.direction === "above" ? "text-[#089981]" : "text-[#f23645]"}`}>
                  {alert.direction === "above" ? "↑" : "↓"} ${alert.targetPrice}
                </span>
                {alert.note && <span className="ml-1 text-[#787b86]">· {alert.note}</span>}
              </div>
              <button onClick={() => deleteAlert(alert.id)} className="text-[#787b86] hover:text-[#f23645]">✕</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
