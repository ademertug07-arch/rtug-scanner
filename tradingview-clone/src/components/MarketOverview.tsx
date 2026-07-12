"use client"

import { useState } from "react"
import { ArrowRightIcon, ArrowUpIcon, ArrowDownIcon } from "./icons"
import type { MarketIndex, CryptoTicker, CommodityTicker, EconomicIndicator, DominanceData } from "@/types/market"

const TABS = ["Türk hisseleri", "Kripto", "Vadeli", "Foreks", "Ekonomi", "Aracı kurum"] as const
type Tab = (typeof TABS)[number]

const INDICES: MarketIndex[] = [
  { symbol: "BIST 100", name: "XU100", ticker: "XU100", price: "14.274,02", change: "+14,20", changePercent: "+0,10%", unit: "G", isPositive: true, hasGIndicator: true },
  { symbol: "BIST 50", name: "XU050", ticker: "XU050", price: "12.852,30", change: "+20,55", changePercent: "+0,16%", unit: "POINT", isPositive: true, hasGIndicator: true },
  { symbol: "S&P 500", name: "SPX", ticker: "SPX", price: "7.380,61", change: "+22,81", changePercent: "+0,31%", unit: "USD", isPositive: true },
  { symbol: "Nasdaq 100", name: "NDX", ticker: "NDX", price: "29.340,18", change: "-100,32", changePercent: "−0,34%", unit: "POINT", isPositive: false, hasGIndicator: true },
  { symbol: "Japan 225", name: "NI225", ticker: "NI225", price: "69.360,66", change: "-3.005,34", changePercent: "−4,15%", unit: "JPY", isPositive: false },
  { symbol: "SSE Composite", name: "000001", ticker: "000001", price: "4.027,2648", change: "-93,12", changePercent: "−2,26%", unit: "POINT", isPositive: false, hasGIndicator: true },
  { symbol: "FTSE 100", name: "UKX", ticker: "UKX", price: "10.508,02", change: "-22,08", changePercent: "−0,21%", unit: "POINT", isPositive: false, hasGIndicator: true },
]

const CRYPTO: CryptoTicker[] = [
  { symbol: "Bitcoin", name: "BTCUSD", ticker: "BTCUSD", price: "60.114", unit: "USD", changePercent: "+0,70%", isPositive: true },
  { symbol: "Ethereum", name: "ETHUSD", ticker: "ETHUSD", price: "1.585,6", unit: "USD", changePercent: "+1,30%", isPositive: true },
]

const DOMINANCE: DominanceData = { btcPercent: "58,59%", ethPercent: "9,30%", othersPercent: "32,12%" }

const COMMODITIES: CommodityTicker[] = [
  { symbol: "USD:TRY", name: "USDTRY", ticker: "USDTRY", price: "46,618800", unit: "TRY", changePercent: "+1,64%", isPositive: true },
  { symbol: "Hafif ham petrol", name: "CL1!", ticker: "CL1!", price: "69,07", unit: "USD / varil", changePercent: "−3,96%", isPositive: false, hasGIndicator: true },
  { symbol: "Doğal gaz", name: "NG1!", ticker: "NG1!", price: "3,346", unit: "USD / milyon BTU", changePercent: "+0,09%", isPositive: true, hasGIndicator: true },
  { symbol: "Altın", name: "GC1!", ticker: "GC1!", price: "4.097,2", unit: "USD / troy ons", changePercent: "+1,23%", isPositive: true, hasGIndicator: true },
  { symbol: "Bakır", name: "HG1!", ticker: "HG1!", price: "6,1470", unit: "USD / libre", changePercent: "+1,20%", isPositive: true, hasGIndicator: true },
]

const ECONOMICS: EconomicIndicator[] = [
  { name: "Türkiye 10 yıllık getirisi", ticker: "TRT050935T13", value: "30,750%", subValue: "0,00% 1 ay", link: "/symbols/OTCB-TRT050935T13/" },
  { name: "Türkiye yıllık enflasyon oranı", ticker: "TRIRYY", value: "", link: "/symbols/ECONOMICS-TRIRYY/" },
  { name: "Türkiye faiz oranı", ticker: "TRINTR", value: "Güncel 37%   Tahmin —   Sonraki açıklama 23 Tem 2026", link: "/symbols/ECONOMICS-TRINTR/" },
]

function IndexCard({ item }: { item: MarketIndex }) {
  return (
    <a
      href={`https://tr.tradingview.com/symbols/BIST-${item.ticker}/`}
      className="group flex flex-col gap-1 rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors"
    >
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-[#f7f8f8]">{item.symbol}</span>
        {item.hasGIndicator && <span className="text-[10px] text-[#787b86]">G</span>}
      </div>
      <span className="text-xs text-[#787b86]">{item.ticker}</span>
      <span className="text-lg font-semibold text-[#f7f8f8]">{item.price}</span>
      <div className="flex items-center gap-1">
        {item.isPositive ? (
          <ArrowUpIcon className="h-3 w-3 text-[#089981]" />
        ) : (
          <ArrowDownIcon className="h-3 w-3 text-[#f23645]" />
        )}
        <span className={`text-xs font-medium ${item.isPositive ? "text-[#089981]" : "text-[#f23645]"}`}>
          {item.changePercent}
        </span>
        <span className="text-xs text-[#787b86]">{item.unit}</span>
      </div>
    </a>
  )
}

function CryptoTickerCard({ item }: { item: CryptoTicker }) {
  return (
    <a href={`https://tr.tradingview.com/symbols/${item.ticker}/`} className="group flex flex-col gap-1 rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors">
      <span className="text-sm font-medium text-[#f7f8f8]">{item.symbol}</span>
      <span className="text-xs text-[#787b86]">{item.ticker}</span>
      <span className="text-lg font-semibold text-[#f7f8f8]">{item.price}</span>
      <div className="flex items-center gap-1">
        {item.isPositive ? <ArrowUpIcon className="h-3 w-3 text-[#089981]" /> : <ArrowDownIcon className="h-3 w-3 text-[#f23645]" />}
        <span className={`text-xs font-medium ${item.isPositive ? "text-[#089981]" : "text-[#f23645]"}`}>{item.changePercent}</span>
        <span className="text-xs text-[#787b86]">{item.unit}</span>
      </div>
    </a>
  )
}

function CommodityCard({ item }: { item: CommodityTicker }) {
  return (
    <a href={`https://tr.tradingview.com/symbols/${item.ticker}/`} className="group flex flex-col gap-1 rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-[#f7f8f8]">{item.symbol}</span>
        {item.hasGIndicator && <span className="text-[10px] text-[#787b86]">G</span>}
      </div>
      <span className="text-xs text-[#787b86]">{item.ticker}</span>
      <span className="text-lg font-semibold text-[#f7f8f8]">{item.price}</span>
      <div className="flex items-center gap-1">
        {item.isPositive ? <ArrowUpIcon className="h-3 w-3 text-[#089981]" /> : <ArrowDownIcon className="h-3 w-3 text-[#f23645]" />}
        <span className={`text-xs font-medium ${item.isPositive ? "text-[#089981]" : "text-[#f23645]"}`}>{item.changePercent}</span>
        <span className="text-xs text-[#787b86]">{item.unit}</span>
      </div>
    </a>
  )
}

function EconomicCard({ item }: { item: EconomicIndicator }) {
  return (
    <a href={`https://tr.tradingview.com${item.link}`} className="group flex flex-col gap-1 rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors">
      <span className="text-sm font-medium text-[#f7f8f8]">{item.name}</span>
      <span className="text-xs text-[#787b86]">{item.ticker}</span>
      {item.value && <span className="text-lg font-semibold text-[#f7f8f8]">{item.value}</span>}
      {item.subValue && <span className="text-xs text-[#787b86]">{item.subValue}</span>}
    </a>
  )
}

export default function MarketOverview() {
  const [activeTab, setActiveTab] = useState<Tab>("Türk hisseleri")

  return (
    <section className="bg-black py-8 md:py-12">
      <div className="mx-auto max-w-[1260px] px-4">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8">
          <div>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-semibold text-white leading-tight">
              Dünya piyasaları nerede
            </h2>
            <p className="mt-2 text-sm text-[#787b86]">
              Geleceği kendi ellerine alan 100 milyon yatırımcıya katılın.
            </p>
          </div>
          <a
            href="https://tr.tradingview.com/features/"
            className="inline-flex items-center gap-1 text-sm font-medium text-[#2962ff] hover:text-[#1e53e5] transition-colors shrink-0"
          >
            Özellikleri keşfet
            <ArrowRightIcon className="h-3.5 w-3.5" />
          </a>
        </div>

        <div role="tablist" className="flex flex-wrap gap-2 mb-6">
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

        {activeTab === "Türk hisseleri" && (
          <>
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-[#f7f8f8]">Piyasa özeti</h3>
                <a href="https://tr.tradingview.com/markets/" className="text-xs text-[#787b86] hover:text-[#f7f8f8] transition-colors">
                  Piyasa özeti →
                </a>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
                {INDICES.map((idx) => (
                  <IndexCard key={idx.ticker} item={idx} />
                ))}
              </div>
              <div className="mt-3">
                <a
                  href="https://tr.tradingview.com/markets/indices/quotes-major/"
                  className="text-xs text-[#2962ff] hover:text-[#1e53e5] transition-colors"
                >
                  Tüm büyük endeksleri görün →
                </a>
              </div>
            </div>

            <div className="border-t border-[#2a2e39] pt-6">
              <h3 className="text-lg font-semibold text-[#f7f8f8] mb-4">Majör endeksler</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
                {INDICES.map((idx) => (
                  <IndexCard key={`major-${idx.ticker}`} item={idx} />
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === "Kripto" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <a
              href="https://tr.tradingview.com/markets/cryptocurrencies/dominance"
              className="col-span-full rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-[#f7f8f8]">Kripto piyasa değeri</span>
                <span className="text-xs text-[#787b86]">TOTAL</span>
              </div>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="text-lg font-semibold text-[#f7f8f8]">2,06 T</span>
                <span className="text-xs text-[#787b86]">USD</span>
                <span className="text-xs font-medium text-[#f23645]">−18,12%</span>
                <span className="text-xs text-[#787b86]">1 ay</span>
              </div>
              <div className="mt-2 flex gap-4 text-xs">
                <span><span className="text-[#787b86]">Bitcoin hakimiyeti</span> <span className="text-[#f7f8f8]">Bitcoin {DOMINANCE.btcPercent}</span></span>
                <span className="text-[#089981]">Ethereum {DOMINANCE.ethPercent}</span>
                <span className="text-[#787b86]">Diğerleri {DOMINANCE.othersPercent}</span>
              </div>
            </a>
            {CRYPTO.map((c) => (
              <CryptoTickerCard key={c.ticker} item={c} />
            ))}
            <div className="flex items-end">
              <a
                href="https://tr.tradingview.com/markets/cryptocurrencies/prices-all/"
                className="text-xs text-[#2962ff] hover:text-[#1e53e5] transition-colors"
              >
                Tüm kripto paraları gör →
              </a>
            </div>
          </div>
        )}

        {activeTab === "Vadeli" && (
          <div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
              {COMMODITIES.map((c) => (
                <CommodityCard key={c.ticker} item={c} />
              ))}
            </div>
            <div className="mt-3">
              <a
                href="https://tr.tradingview.com/markets/futures/quotes-all/"
                className="text-xs text-[#2962ff] hover:text-[#1e53e5] transition-colors"
              >
                Tüm vadelileri gör →
              </a>
            </div>
          </div>
        )}

        {activeTab === "Foreks" && (
          <div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
              {COMMODITIES.filter(c => c.ticker === "USDTRY").map((c) => (
                <CommodityCard key={c.ticker} item={c} />
              ))}
            </div>
          </div>
        )}

        {activeTab === "Ekonomi" && (
          <div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {ECONOMICS.map((e) => (
                <EconomicCard key={e.ticker} item={e} />
              ))}
            </div>
            <div className="mt-3">
              <a
                href="https://tr.tradingview.com/markets/world-economy/countries/turkey/"
                className="text-xs text-[#2962ff] hover:text-[#1e53e5] transition-colors"
              >
                Tüm ekonomik göstergeleri görün →
              </a>
            </div>
          </div>
        )}

        {activeTab === "Aracı kurum" && (
          <div className="rounded-lg bg-[#1e222d] p-8 text-center">
            <p className="text-sm text-[#787b86]">Aracı kurum bilgileri</p>
          </div>
        )}
      </div>
    </section>
  )
}
