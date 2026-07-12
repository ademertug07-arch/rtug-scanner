"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import dynamic from "next/dynamic"
import NavBar from "@/components/NavBar"
import {
  createChart, CandlestickSeries, LineSeries, HistogramSeries,
  type IChartApi, type ISeriesApi,
} from "lightweight-charts"
import {
  generateSampleData, calculateSMA, calculateEMA, calculateRSI,
  calculateMACD, calculateBollingerBands, calculateSuperTrend, calculateVWAP,
  type CandleWithVolume,
} from "@/lib/indicators"

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => <div className="h-full bg-[#1e1e1e] flex items-center justify-center text-[#787b86] text-xs">Editor yükleniyor...</div>,
})

type ScriptTab = { id: string; name: string; code: string; active: boolean }
type PanelView = "editor" | "templates" | "saved"

const TEMPLATE_CALCS: Record<string, (d: CandleWithVolume[]) => { series: any[]; type: string; options?: any }[]> = {
  "SMA Crossover": (d) => {
    const f = calculateSMA(d, 9), s = calculateSMA(d, 21)
    return [{ series: f, type: "Line", options: { color: "#2962FF", lineWidth: 2 } }, { series: s, type: "Line", options: { color: "#F23645", lineWidth: 2 } }]
  },
  "RSI": (d) => [{ series: calculateRSI(d, 14), type: "Line", options: { color: "#7F77DD", lineWidth: 2 } }],
  "MACD": (d) => {
    const { macdLine, signalLine, histogram } = calculateMACD(d, 12, 26, 9)
    return [{ series: macdLine, type: "Line", options: { color: "#2962FF" } }, { series: signalLine, type: "Line", options: { color: "#F23645" } }, { series: histogram, type: "Histogram", options: {} }]
  },
  "Bollinger Bands": (d) => {
    const { middle, upper, lower } = calculateBollingerBands(d, 20, 2)
    return [{ series: upper, type: "Line", options: { color: "#2962FF" } }, { series: middle, type: "Line", options: { color: "#2962FF", lineWidth: 2 } }, { series: lower, type: "Line", options: { color: "#2962FF" } }]
  },
  "SuperTrend": (d) => [{ series: calculateSuperTrend(d, 10, 3).superTrend, type: "Line", options: { color: "#089981", lineWidth: 2 } }],
  "VWAP + Support/Resistance": (d) => [{ series: calculateVWAP(d), type: "Line", options: { color: "#7F77DD", lineWidth: 2 } }],
  "EMA Crossover with Alerts": (d) => {
    const f = calculateEMA(d, 9), s = calculateEMA(d, 21), fl = calculateSMA(d, 200)
    return [{ series: f, type: "Line", options: { color: "#2962FF", lineWidth: 2 } }, { series: s, type: "Line", options: { color: "#F23645", lineWidth: 2 } }, { series: fl, type: "Line", options: { color: "#787B86", lineWidth: 1 } }]
  },
  "Volume Profile": (d) => [{ series: calculateVWAP(d), type: "Line", options: { color: "#7F77DD", lineWidth: 2 } }, { series: calculateEMA(d, 20), type: "Line", options: { color: "#FF9800", lineWidth: 1 } }],
  "Stochastic RSI": (d) => [{ series: calculateRSI(d, 14), type: "Line", options: { color: "#7F77DD", lineWidth: 2 } }],
  "Ichimoku Cloud": (d) => [{ series: calculateSMA(d, 9), type: "Line", options: { color: "#2962FF" } }, { series: calculateSMA(d, 26), type: "Line", options: { color: "#F23645" } }],
}

function makeTab(name = "Gösterge 1"): ScriptTab {
  return { id: crypto.randomUUID(), name, code: `//@version=5\nindicator("${name}", overlay=true)\n\nplot(close)`, active: false }
}

const PINED_LANG = {
  defaultToken: "", tokenPostfix: ".pine",
  keywords: ["and","or","not","if","else","for","var","varip","true","false","na","bool","int","float","string","color","input","plot","hline","fill","bgcolor","plotshape","alertcondition","strategy","indicator","library","export"],
  typeKeywords: ["open","high","low","close","volume","hl2","hlc3","ohlc4","time","bar_index","tickerid"],
  builtinFunctions: ["ta.sma","ta.ema","ta.rsi","ta.macd","ta.bb","ta.supertrend","ta.atr","ta.vwap","ta.vwma","ta.crossover","ta.crossunder","ta.highest","ta.lowest","ta.stdev","ta.change","ta.roc","ta.mom","ta.pivothigh","ta.pivotlow","ta.valuewhen","ta.barssince","ta.tr","ta.stoch","ta.stochrsi","ta.wma","ta.hma","ta.alma","ta.linreg","ta.correlation","ta.median","ta.mode","math.abs","math.max","math.min","math.sqrt","math.log","math.pow","math.round","math.ceil","math.floor","strategy.entry","strategy.exit","strategy.close","strategy.close_all","strategy.order","color.new","color.rgb","line.new","line.set_xy1","line.set_color","line.set_width","label.new","label.set_xy","label.set_text","label.set_color","label.set_size","table.new","table.cell","table.merge_cells","box.new","box.set_border_color","box.set_bgcolor","request.security","syminfo.ticker","syminfo.tickerid","syminfo.currency","syminfo.description","timeframe.period","barstate.isconfirmed","barstate.isnew","barstate.isfirst"],
  operators: /[=><!|&+\-*/^%]+/,
  tokenizer: {
    root: [
      { include: "@whitespace" },
      [/[a-z_$][\w$]*/, { cases: { "@typeKeywords": "keyword", "@keywords": "keyword", "@builtinFunctions": "type.identifier", "@default": "identifier" } }],
      [/[{}()\[\]]/, "@brackets"], [/@operators/, "operator"],
      [/\d*\.\d+([eE][\-+]?\d+)?/, "number.float"], [/\d+/, "number"],
      [/"/, { token: "string.quote", bracket: "@open", next: "@string" }],
      [/'/, { token: "string.quote", bracket: "@open", next: "@string_single" }],
    ],
    string: [[/[^\\"]+/, "string"],[/\\./, "string.escape"],[  /"/, { token: "string.quote", bracket: "@close", next: "@pop" }]],
    string_single: [[/[^\\']+/, "string"],[/\\./, "string.escape"],[  /'/, { token: "string.quote", bracket: "@close", next: "@pop" }]],
    whitespace: [[/[ \t\r\n]+/, "white"],[/\/\/.*$/, "comment"],[/\/\*/, "comment","@comment"]],
    comment: [[/[^\/*]+/, "comment"],[/\*\//, "comment","@pop"],[/[\/*]/, "comment"]],
  },
}

export default function PineEditorPage() {
  const [tabs, setTabs] = useState<ScriptTab[]>(() => [makeTab()])
  const [activeId, setActiveId] = useState("")
  const [templates, setTemplates] = useState<any[]>([])
  const [savedScripts, setSavedScripts] = useState<any[]>([])
  const [view, setView] = useState<PanelView>("editor")
  const [msg, setMsg] = useState("")
  const [panelH, setPanelH] = useState(300)
  const [showPanel, setShowPanel] = useState(true)
  const [chartReady, setChartReady] = useState(false)
  const [monacoReady, setMonacoReady] = useState(false)

  const chartRef = useRef<HTMLDivElement>(null)
  const chartApi = useRef<IChartApi | null>(null)
  const candleSeries = useRef<ISeriesApi<any> | null>(null)
  const seriesMap = useRef<Map<string, ISeriesApi<any>[]>>(new Map())
  const sampleRef = useRef<CandleWithVolume[]>([])
  const panelRef = useRef<HTMLDivElement>(null)
  const activeTabRef = useRef(tabs[0])

  const activeTab = tabs.find(t => t.id === activeId) || tabs[0]
  activeTabRef.current = activeTab

  useEffect(() => {
    if (tabs.length > 0 && !activeId) setActiveId(tabs[0].id)
  }, [tabs, activeId])

  useEffect(() => {
    fetch("/api/scripts?template=true").then(r => r.json()).then(setTemplates).catch(() => {})
    fetch("/api/scripts").then(r => r.json()).then(d => { if (!d.error) setSavedScripts(d) }).catch(() => {})
  }, [])

  const getData = useCallback(() => {
    if (sampleRef.current.length === 0) sampleRef.current = generateSampleData(200)
    return sampleRef.current
  }, [])

  // Chart setup with ResizeObserver
  useEffect(() => {
    if (!chartRef.current || chartApi.current) return
    const container = chartRef.current
    const w = container.clientWidth || 600
    const h = container.clientHeight || 400

    const ch = createChart(container, {
      layout: { background: { color: "#131722" }, textColor: "#787b86" },
      grid: { vertLines: { color: "#1e222d" }, horzLines: { color: "#1e222d" } },
      crosshair: { mode: 0 },
      rightPriceScale: { borderColor: "#2a2e39" },
      timeScale: { borderColor: "#2a2e39", timeVisible: true },
      width: w, height: h,
    })
    chartApi.current = ch
    const cs = ch.addSeries(CandlestickSeries, {
      upColor: "#089981", downColor: "#f23645", borderDownColor: "#f23645", borderUpColor: "#089981",
      wickDownColor: "#f23645", wickUpColor: "#089981",
    })
    cs.setData(getData())
    candleSeries.current = cs
    setChartReady(true)

    const ro = new ResizeObserver(entries => {
      for (const entry of entries) {
        const box = entry.contentBoxSize?.[0]
        const w = box ? box.inlineSize : entry.contentRect.width
        const h = box ? box.blockSize : entry.contentRect.height
        ch.applyOptions({ width: Math.floor(w), height: Math.floor(h) })
      }
    })
    ro.observe(container)

    return () => { ro.disconnect(); ch.remove(); chartApi.current = null; candleSeries.current = null; setChartReady(false) }
  }, [getData])

  const removeSeries = useCallback((id: string) => {
    const ss = seriesMap.current.get(id)
    if (ss && chartApi.current) { ss.forEach(s => { try { chartApi.current!.removeSeries(s) } catch {} }); seriesMap.current.delete(id) }
  }, [])

  const applySeries = useCallback((tab: ScriptTab) => {
    if (!chartApi.current) return
    removeSeries(tab.id)
    const m = tab.code.match(/indicator\(["']([^"']+)["']\)/)
    const title = m?.[1] || tab.name
    const calc = TEMPLATE_CALCS[title]
    if (!calc) { setMsg(`ℹ "${title}" önizleme`); setTimeout(() => setMsg(""), 2500); return }
    const indicators = calc(getData())
    const added: ISeriesApi<any>[] = []
    for (const ind of indicators) {
      if (!chartApi.current) break
      let s: ISeriesApi<any> | null = null
      if (ind.type === "Line") s = chartApi.current.addSeries(LineSeries, { ...ind.options, priceScaleId: tab.code.includes("overlay=true") ? "right" : "left" })
      else if (ind.type === "Histogram") s = chartApi.current.addSeries(HistogramSeries, { ...ind.options })
      if (s) { s.setData(ind.series); added.push(s) }
    }
    seriesMap.current.set(tab.id, added)
    setMsg(`✓ "${title}" eklendi`)
    setTimeout(() => setMsg(""), 2500)
  }, [getData])

  const toggleScript = (id: string) => {
    setTabs(prev => prev.map(t => {
      if (t.id !== id) return t
      if (t.active) removeSeries(t.id); else applySeries(t)
      return { ...t, active: !t.active }
    }))
  }

  const addTab = () => { const t = makeTab(`Gösterge ${tabs.length + 1}`); setTabs(prev => [...prev, t]); setActiveId(t.id) }

  const closeTab = (id: string) => {
    removeSeries(id)
    setTabs(prev => {
      const next = prev.filter(t => t.id !== id)
      if (next.length === 0) { const n = makeTab(); setActiveId(n.id); return [n] }
      return next
    })
    if (activeId === id) {
      const idx = tabs.findIndex(t => t.id === id)
      const remaining = tabs.filter(t => t.id !== id)
      if (remaining.length > 0) setActiveId(remaining[Math.min(idx, remaining.length - 1)].id)
    }
  }

  const updateCode = (code: string) => setTabs(prev => prev.map(t => t.id === activeIdRef.current ? { ...t, code } : t))
  const updateName = (name: string) => setTabs(prev => prev.map(t => t.id === activeId ? { ...t, name } : t))
  const loadTmpl = (name: string) => {
    const t = templates.find(x => x.name === name)
    if (t) setTabs(prev => prev.map(x => x.id === activeId ? { ...x, name: t.name, code: t.code } : x))
  }

  const saveScript = async () => {
    const tab = activeTabRef.current
    if (!tab) return
    const exists = savedScripts.find(s => s.name === tab.name)
    try {
      const r = await fetch("/api/scripts", {
        method: exists ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(exists ? { id: exists.id, name: tab.name, code: tab.code } : { name: tab.name, code: tab.code, description: "", category: "custom" }),
      })
      if (r.ok) { const s = await r.json(); setMsg(`✓ "${tab.name}" kaydedildi`); setSavedScripts(prev => { const f = prev.filter(x => x.id !== s.id); return [s, ...f] }) }
    } catch {}
    setTimeout(() => setMsg(""), 2500)
  }

  const loadSaved = (s: any) => { setTabs(prev => prev.map(t => t.id === activeId ? { ...t, name: s.name, code: s.code } : t)); setView("editor") }
  const deleteSaved = async (id: string) => { await fetch(`/api/scripts?id=${id}`, { method: "DELETE" }); setSavedScripts(p => p.filter(s => s.id !== id)) }

  const activeIdRef = useRef(activeId)
  activeIdRef.current = activeId

  // Panel resize - querySelector on document, not panelRef
  useEffect(() => {
    let y = 0, h = 0
    const onMd = (e: MouseEvent) => { y = e.clientY; h = panelH; document.addEventListener("mousemove", onMv); document.addEventListener("mouseup", onMu); document.body.style.cursor = "ns-resize"; document.body.style.userSelect = "none" }
    const onMv = (e: MouseEvent) => { const dh = y - e.clientY; setPanelH(Math.max(120, Math.min(700, h - dh))) }
    const onMu = () => { document.removeEventListener("mousemove", onMv); document.removeEventListener("mouseup", onMu); document.body.style.cursor = ""; document.body.style.userSelect = "" }
    const handle = document.querySelector(".pine-handle") as HTMLElement
    if (handle) { handle.addEventListener("mousedown", onMd); return () => handle.removeEventListener("mousedown", onMd) }
  }, [panelH])

  const beforeMount = (m: any) => { m.languages.register({ id: "pinescript" }); m.languages.setMonarchTokensProvider("pinescript", PINED_LANG); setMonacoReady(true) }

  return (
    <div className="h-screen bg-black flex flex-col">
      <NavBar />
      <div className="flex-1 flex flex-col overflow-hidden" style={{ paddingTop: "5.5rem" }}>
        {/* Chart */}
        <div className="relative flex-1 min-h-0">
          <div ref={chartRef} className="absolute inset-0" />
        </div>

        {/* Reopen button */}
        {!showPanel && (
          <button onClick={() => setShowPanel(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1e222d] border-t border-[#2a2e39] text-[#787b86] hover:text-[#f7f8f8] text-[11px] transition-colors shrink-0">
            ▲ Pine Editor
          </button>
        )}

        {/* Resize handle */}
        {showPanel && <div className="pine-handle h-[3px] bg-[#2a2e39] hover:bg-[#2962ff] cursor-ns-resize relative z-10 transition-colors shrink-0" />}

        {/* Bottom panel */}
        {showPanel && (
          <div ref={panelRef} className="flex flex-col border-t border-[#2a2e39] bg-[#131722] shrink-0" style={{ height: panelH }}>
            {/* Tab bar */}
            <div className="flex items-center bg-[#1e222d] border-b border-[#2a2e39] min-h-[30px]">
              <div className="flex items-center flex-1 overflow-x-auto">
                {tabs.map(tab => (
                  <div key={tab.id} onClick={() => setActiveId(tab.id)}
                    className={`flex items-center gap-1.5 px-2.5 py-[5px] text-[11px] cursor-pointer border-r border-[#2a2e39] transition-colors select-none whitespace-nowrap ${
                      activeId === tab.id ? "bg-[#131722] text-[#f7f8f8]" : "bg-[#1e222d] text-[#787b86] hover:text-[#d1d4dc]"
                    }`}>
                    <span onClick={e => { e.stopPropagation(); toggleScript(tab.id) }}
                      className={`w-[7px] h-[7px] rounded-full shrink-0 ${tab.active ? "bg-[#089981]" : "bg-[#434651]"}`} />
                    <input value={tab.name} onChange={e => updateName(e.target.value)}
                      className="bg-transparent outline-none text-inherit w-28 text-[11px]" />
                    {tabs.length > 1 && (
                      <button onClick={e => { e.stopPropagation(); closeTab(tab.id) }}
                        className="text-[#434651] hover:text-[#f23645] text-[10px] leading-none ml-0.5">✕</button>
                    )}
                  </div>
                ))}
              </div>
              <button onClick={addTab} className="px-2.5 py-[5px] text-[#787b86] hover:text-[#f7f8f8] text-[13px] border-l border-[#2a2e39] shrink-0">+</button>
              <button onClick={() => setShowPanel(false)} className="px-2.5 py-[5px] text-[#787b86] hover:text-[#f7f8f8] text-[11px] border-l border-[#2a2e39] shrink-0">✕</button>
            </div>

            {/* Toolbar */}
            <div className="flex items-center gap-2 px-2 py-[5px] bg-[#131722] border-b border-[#2a2e39] min-h-[30px]">
              {view === "editor" && (
                <>
                  <select onChange={e => { const v = e.target.value; if (v) loadTmpl(v) }} defaultValue=""
                    className="bg-[#1e222d] text-[#787b86] text-[11px] rounded px-2 py-[3px] border border-[#2a2e39] outline-none cursor-pointer hover:border-[#434651]">
                    <option value="" disabled>Şablon Ekle</option>
                    {templates.map(t => <option key={t.id} value={t.name}>{t.name}</option>)}
                  </select>
                  <button onClick={() => { const tab = activeTabRef.current; if (tab) toggleScript(tab.id) }}
                    className={`text-[11px] px-2.5 py-[3px] rounded font-medium transition-colors ${
                      activeTab?.active ? "bg-transparent text-[#f23645] border border-[#f23645] hover:bg-[#f23645]/10" : "bg-[#2962ff] text-white hover:bg-[#1e53e5]"
                    }`}>
                    {activeTab?.active ? "Kaldır" : "Grafiğe Uygula"}
                  </button>
                  <div className="w-px h-3.5 bg-[#2a2e39]" />
                  <button onClick={saveScript} className="text-[11px] px-2 py-[3px] text-[#787b86] hover:text-[#f7f8f8] transition-colors">Kaydet</button>
                  <div className="w-px h-3.5 bg-[#2a2e39]" />
                </>
              )}
              <div className="flex ml-auto gap-0.5">
                {(["editor","templates","saved"] as PanelView[]).map(v => (
                  <button key={v} onClick={() => setView(v)}
                    className={`text-[11px] px-2 py-[3px] rounded transition-colors ${view === v ? "bg-[#2a2e39] text-[#f7f8f8]" : "text-[#787b86] hover:text-[#f7f8f8]"}`}>
                    {v === "editor" ? "Düzenleyici" : v === "templates" ? "Şablonlar" : "Kayıtlı"}
                  </button>
                ))}
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-h-0">
              {view === "editor" ? (
                <div className="h-full">
                  {activeTab && (
                    <div className="h-full" key={activeTab.id}>
                      <MonacoEditor
                        language="pinescript"
                        theme="vs-dark"
                        value={activeTab.code}
                        onChange={v => updateCode(v || "")}
                        beforeMount={beforeMount}
                        options={{
                          minimap: { enabled: false }, fontSize: 12,
                          fontFamily: "Consolas, 'Courier New', monospace",
                          lineNumbers: "on", renderLineHighlight: "none",
                          scrollBeyondLastLine: false, automaticLayout: true,
                          padding: { top: 4 }, lineNumbersMinChars: 3,
                          folding: false, glyphMargin: false,
                          overviewRulerBorder: false, contextmenu: false,
                          bracketPairColorization: { enabled: true },
                          smoothScrolling: true, cursorBlinking: "smooth",
                        }}
                      />
                    </div>
                  )}
                </div>
              ) : view === "templates" ? (
                <div className="h-full overflow-y-auto p-2">
                  <div className="grid grid-cols-2 gap-1.5">
                    {templates.map(t => (
                      <button key={t.id} onClick={() => { loadTmpl(t.name); setView("editor") }}
                        className="text-left p-2.5 rounded hover:bg-[#1e222d] transition-colors border border-[#2a2e39]">
                        <div className="text-[#f7f8f8] text-[12px] font-medium">{t.name}</div>
                        <div className="text-[#787b86] text-[10px] mt-0.5 leading-tight">{t.description}</div>
                        <span className="inline-block mt-1 text-[9px] text-[#2962ff] bg-[#2962ff]/10 px-1 py-0.5 rounded">{t.category}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="h-full overflow-y-auto p-2">
                  {savedScripts.length === 0 ? (
                    <p className="text-[#787b86] text-[11px] text-center pt-8">Henüz kayıtlı script yok</p>
                  ) : (
                    <div className="grid grid-cols-2 gap-1.5">
                      {savedScripts.map(s => (
                        <div key={s.id} className="flex items-center justify-between p-2.5 rounded hover:bg-[#1e222d] transition-colors border border-[#2a2e39]">
                          <button onClick={() => loadSaved(s)} className="text-left flex-1 min-w-0">
                            <div className="text-[#f7f8f8] text-[12px] font-medium truncate">{s.name}</div>
                            <div className="text-[#787b86] text-[9px]">{s.category}</div>
                          </button>
                          <button onClick={() => deleteSaved(s.id)} className="text-[#f23645] hover:text-[#ff6b6b] text-[10px] px-1.5 py-0.5 shrink-0">Sil</button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Status bar */}
            <div className="flex items-center justify-between px-2.5 py-[3px] bg-[#1e222d] border-t border-[#2a2e39] text-[10px] text-[#787b86] min-h-[22px] shrink-0">
              <div className="flex items-center gap-3">
                <span>Pine Script v5</span>
                <span>{activeTab?.code.split("\n").length || 0} satır</span>
                <span className={`w-[7px] h-[7px] rounded-full ${activeTab?.active ? "bg-[#089981]" : "bg-[#434651]"}`} />
                <span>{activeTab?.active ? "Grafikte" : "Beklemede"}</span>
              </div>
              <span>{msg || "Önizleme modu"}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
