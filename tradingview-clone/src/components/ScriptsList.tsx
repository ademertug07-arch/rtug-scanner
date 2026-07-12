"use client"

import { useState } from "react"
import type { ScriptItem } from "@/types/market"
import { ExternalLinkIcon, ChartIcon } from "./icons"

const SCRIPTS: Record<string, ScriptItem[]> = {
  "Editörün Seçtikleri": [
    { name: "Session Edge Profiler | Flux Charts", description: "The Session Edge Profiler is a statistical dashboard indicator that profiles up to five configurable trading sessions across the available completed trading days loaded on the chart.", type: "Pine Script® göstergesi", author: "fluxchart", authorUrl: "https://tr.tradingview.com/u/fluxchart/", link: "https://tr.tradingview.com/script/T1V41Bl5-Session-Edge-Profiler-Flux-Charts/" },
    { name: "Supertrend Parameter Sensitivity 3D [LuxAlgo]", description: "The Supertrend Parameter Sensitivity 3D indicator is a powerful optimization tool that executes 100 simultaneous Supertrend backtests bar-by-bar.", type: "Pine Script® göstergesi", author: "LuxAlgo", authorUrl: "https://tr.tradingview.com/u/LuxAlgo/", link: "https://tr.tradingview.com/script/kSMLs0Hh-Supertrend-Parameter-Sensitivity-3D-LuxAlgo/" },
    { name: "ExprLib", description: "ExprLib is a library for parsing and evaluating string expressions. It allows scripts to expose configurable logic by letting users define custom conditions and calculations.", type: "Pine Script® kütüphanesi", author: "A1trdX", authorUrl: "https://tr.tradingview.com/u/A1trdX/", link: "https://tr.tradingview.com/script/QNGQtaZJ-ExprLib/" },
    { name: "Chart Patterns Screener [Trendoscope]", description: "Chart Patterns Screener is an advanced Pine Script designed to automatically detect and display classical chart patterns on TradingView.", type: "Pine Script® göstergesi", author: "Trendoscope", authorUrl: "https://tr.tradingview.com/u/Trendoscope/", link: "https://tr.tradingview.com/script/a7a6yS0y-Chart-Patterns-Screener-Trendoscope/" },
    { name: "Machine Learning RSI | AI Classification & Ranking (Zeiierman)", description: "An adaptive RSI intelligence system combining momentum analysis, historical analog recognition, ML classification, and confidence scoring.", type: "Pine Script® göstergesi", author: "Zeiierman", authorUrl: "https://tr.tradingview.com/u/Zeiierman/", link: "https://tr.tradingview.com/script/VrTL3VwF-Machine-Learning-RSI-AI-Classification-Ranking-Zeiierman/" },
    { name: "Polynomial/Linear Regression Volume Profile [BigBeluga]", description: "A state-of-the-art charting framework blending advanced statistical modeling with localized volume distribution analysis.", type: "Pine Script® göstergesi", author: "BigBeluga", authorUrl: "https://tr.tradingview.com/u/BigBeluga/", link: "https://tr.tradingview.com/script/4rlNNL5e-Polynomial-Linear-Regression-Volume-Profile-BigBeluga/" },
    { name: "Whale Liquidity and Absorption Profile [AlgoAlpha]", description: "Maps intrabar buying, selling, delta, and absorption activity into stacked horizontal profiles.", type: "Pine Script® göstergesi", author: "AlgoAlpha", authorUrl: "https://tr.tradingview.com/u/AlgoAlpha/", link: "https://tr.tradingview.com/script/cWm8UcfQ-Whale-Liquidity-and-Absorption-Profile-AlgoAlpha/" },
    { name: "Fractional EMA Kalman Filter [D7]", description: "An experimental smoothing and state-estimation tool that combines a Kalman filter framework with a fractional EMA input.", type: "Pine Script® göstergesi", author: "et20tradeview", authorUrl: "https://tr.tradingview.com/u/et20tradeview/", link: "https://tr.tradingview.com/script/c75aF3t1-Fractional-EMA-Kalman-Filter-D7/" },
    { name: "Neural Weight Oscillator (Zeiierman)", description: "An adaptive multi-factor oscillator combining structured decision-making with dynamic market learning.", type: "Pine Script® göstergesi", author: "Zeiierman", authorUrl: "https://tr.tradingview.com/u/Zeiierman/", link: "https://tr.tradingview.com/script/bfu1hmkS-Neural-Weight-Oscillator-Zeiierman/" },
    { name: "NeuraLib: A Native AI and Deep Learning Runtime", description: "A tensor-based, auto-differentiating Machine Learning runtime built natively for Pine Script.", type: "Pine Script® kütüphanesi", author: "Alien_Algorithms", authorUrl: "https://tr.tradingview.com/u/Alien_Algorithms/", link: "https://tr.tradingview.com/script/GewgOj30-NeuraLib-A-Native-AI-and-Deep-Learning-Runtime/" },
  ],
  Popüler: [],
}

const TABS = ["Editörün Seçtikleri", "Popüler"] as const

export default function ScriptsList() {
  const [activeTab, setActiveTab] = useState<string>("Editörün Seçtikleri")
  const scripts = SCRIPTS[activeTab] || []

  return (
    <section className="bg-black py-8 md:py-12">
      <div className="mx-auto max-w-[1260px] px-4">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-[#f7f8f8]">Göstergeler ve stratejiler</h3>
          <a
            href="https://tr.tradingview.com/scripts/"
            className="flex items-center gap-1 text-xs text-[#787b86] hover:text-[#f7f8f8] transition-colors"
          >
            <ExternalLinkIcon className="h-3 w-3" />
          </a>
        </div>

        <div role="tablist" className="flex gap-2 mb-4">
          {TABS.map((tab) => (
            <button
              key={tab}
              role="tab"
              aria-selected={activeTab === tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 text-sm rounded-[14px] border transition-colors ${
                activeTab === tab
                  ? "bg-[#2962ff] border-[#2962ff] text-white"
                  : "bg-[#2e2e2e] border-[#0f0f0f] text-white hover:bg-[#3a3a3a]"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {scripts.map((script, i) => (
            <a
              key={i}
              href={script.link}
              className="flex flex-col gap-2 rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors"
            >
              <span className="text-sm font-medium text-[#f7f8f8] line-clamp-2 leading-snug">{script.name}</span>
              <p className="text-xs text-[#787b86] line-clamp-3 leading-relaxed">{script.description}</p>
              <div className="mt-auto flex items-center justify-between pt-2 border-t border-[#2a2e39]">
                <div className="flex items-center gap-1">
                  <ChartIcon className="h-3 w-3 text-[#2962ff]" />
                  <span className="text-[10px] text-[#787b86]">{script.type}</span>
                </div>
                <span className="text-[10px] text-[#787b86]">{script.author}</span>
              </div>
            </a>
          ))}
        </div>

        <div className="mt-4">
          <a
            href="https://tr.tradingview.com/scripts/editors-picks/"
            className="text-xs text-[#2962ff] hover:text-[#1e53e5] transition-colors"
          >
            Tüm göstergeleri ve stratejileri görün →
          </a>
        </div>
      </div>
    </section>
  )
}
