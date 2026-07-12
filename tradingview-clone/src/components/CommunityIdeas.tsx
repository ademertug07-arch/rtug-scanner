"use client"

import { useState } from "react"
import type { TradingIdea } from "@/types/market"
import { ExternalLinkIcon, TrendingUpIcon } from "./icons"

const IDEAS: Record<string, TradingIdea[]> = {
  "Editörün Seçtikleri": [
    {
      title: "OZRDN BOĞA RALLİSİ BAŞLATIR MI?",
      description: "ÖZRDN oluşturduğu çanak formasyonunu kırdı. Şu an düzeltmenin sonuna yaklaşıyor. Buralardan yukarı yönlü SEKURO grafiğimizde olduğu gibi sert ve güçlü bir boğa trendi başlatması muhtemeldir.",
      symbol: "BIST:OZRDN",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/ozerden-plastik.svg",
      author: "Eurolizm",
      authorUrl: "https://tr.tradingview.com/u/Eurolizm/",
      date: "Haz 25",
      link: "https://tr.tradingview.com/chart/OZRDN/AVFBAMDA/",
    },
    {
      title: "BTC AYLIK ANALİZ",
      description: "Bitcoin Aylık Grafik Analizi: Kritik Destek Bölgesi Bitcoin'in aylık grafiğinde geçmişten günümüze gelen fiyat hareketlerini ve önemli teknik seviyeleri mercek altına aldık.",
      symbol: "BINANCE:BTCUSDT",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/crypto/XTVCBTC.svg",
      author: "Wolcan",
      authorUrl: "https://tr.tradingview.com/u/Wolcan/",
      date: "Haz 25",
      link: "https://tr.tradingview.com/chart/BTCUSDT/6c0S76Ij/",
    },
    {
      title: "TTRAK — Harmonik Formasyon + Talep Bölgesi Analizi",
      description: "Bu analiz yalnızca eğitim ve bilgilendirme amaçlıdır. Kesinlikle yatırım tavsiyesi niteliği taşımamaktadır.",
      symbol: "BIST:TTRAK",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/turk-traktor.svg",
      author: "Ardella",
      authorUrl: "https://tr.tradingview.com/u/Ardella/",
      date: "Haz 25",
      signal: "Alış",
      link: "https://tr.tradingview.com/chart/TTRAK/tEx8tuTm/",
    },
    {
      title: "Bitcoin: Son 6 Güne Dikkat!",
      description: "Herkese merhaba, yeni bir içerik ile karşınızdayım. Umarım sizler için verimli bir yorum olmuştur. Esen kalın!",
      symbol: "BINANCE:BTCUSDT",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/crypto/XTVCBTC.svg",
      author: "BTCraft7",
      authorUrl: "https://tr.tradingview.com/u/BTCraft7/",
      date: "Haz 24",
      signal: "Satış",
      link: "https://tr.tradingview.com/chart/BTCUSDT/H4UqjgzJ/",
    },
    {
      title: "gümüş te takip seviyelerimiz.",
      description: "Gümüş al satçılarına belki faydası olur. Trend desteğine gelmiş görünüyor.",
      symbol: "OANDA:XAGUSD",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/metal/silver.svg",
      author: "beyazcocuk",
      authorUrl: "https://tr.tradingview.com/u/beyazcocuk/",
      date: "Haz 25",
      link: "https://tr.tradingview.com/chart/XAGUSD/2XSVsEDK/",
    },
    {
      title: "BTCUSDT 3S: Market Structure Shift & Re-Test Short Setup",
      description: "BTCUSDT 3 saatlik grafikte piyasa yapısının ayı lehine döndüğü net bir şekilde görülmektedir.",
      symbol: "BINANCE:BTCUSDT.P",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/crypto/XTVCBTC.svg",
      author: "AliHikmetHarun",
      authorUrl: "https://tr.tradingview.com/u/AliHikmetHarun/",
      date: "Haz 25",
      signal: "Satış",
      link: "https://tr.tradingview.com/chart/BTCUSDT.P/KcF1Ebaa/",
    },
    {
      title: "Altın Fiyatlarındaki Düşüş Trendinde Önemli Bir Konsolidasyon Aş",
      description: "Altının genel trendi, tipik bir aşamaya girdi: düşüş trendini takip eden bir konsolidasyon ve geri çekilme bölgesi.",
      symbol: "OANDA:XAUUSD",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/metal/gold.svg",
      author: "Kallie_Gold",
      authorUrl: "https://tr.tradingview.com/u/Kallie_Gold/",
      date: "Haz 23",
      link: "https://tr.tradingview.com/chart/XAUUSD/aAdABmNe/",
    },
    {
      title: "Spot Altın (XAU/USD)",
      description: "Fiyat hareketlerinin rastgele değil, belirli fraktal tohumlar ve geometrik dizilimler etrafında şekillendiğini kanıtlar niteliktedir.",
      symbol: "OANDA:XAUUSD",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/metal/gold.svg",
      author: "marketgeometry77",
      authorUrl: "https://tr.tradingview.com/u/marketgeometry77/",
      date: "Haz 23",
      signal: "Alış",
      link: "https://tr.tradingview.com/chart/XAUUSD/qbMYZczA/",
    },
    {
      title: "astor",
      description: "Astor Enerji Hisse Analizi (Güncelleme) — Hisse, sarı bölgeden başlattığı yükselişi beklentimize uygun şekilde 310 puan seviyesine kadar taşıdı.",
      symbol: "BIST:ASTOR",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/astor-enerji.svg",
      author: "BrkBarbarosoglu",
      authorUrl: "https://tr.tradingview.com/u/BrkBarbarosoglu/",
      date: "Haz 23",
      link: "https://tr.tradingview.com/chart/ASTOR/TiRMVojP/",
    },
    {
      title: "XAG/USD (GÜMÜŞ) MAKRO TEKNİK ANALİZ VE STRATEJİK DURUM RAPORU",
      description: "Gümüş piyasasında Haziran 2025'ten bu yana uyguladığımız makro strateji, teknik analizin gücünü",
      symbol: "OANDA:XAGUSD",
      symbolLogo: "https://s3-symbol-logo.tradingview.com/metal/silver.svg",
      author: "asilturk",
      authorUrl: "https://tr.tradingview.com/u/asilturk/",
      date: "Haz 22",
      signal: "Satış",
      link: "https://tr.tradingview.com/chart/XAGUSD/I08uDQjq/",
    },
  ],
  Popüler: [],
}

const TABS = ["Editörün Seçtikleri", "Popüler"] as const

export default function CommunityIdeas() {
  const [activeTab, setActiveTab] = useState<string>("Editörün Seçtikleri")
  const ideas = IDEAS[activeTab] || []

  return (
    <section className="bg-black py-8 md:py-12">
      <div className="mx-auto max-w-[1260px] px-4">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-[#f7f8f8]">Topluluk fikirleri</h3>
          <a
            href="https://tr.tradingview.com/ideas/"
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
          {ideas.map((idea, i) => (
            <a
              key={i}
              href={idea.link}
              className="flex flex-col gap-2 rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors"
            >
              <span className="text-sm font-medium text-[#f7f8f8] line-clamp-2 leading-snug">
                {idea.title}
              </span>
              <p className="text-xs text-[#787b86] line-clamp-3 leading-relaxed">{idea.description}</p>
              <div className="mt-auto flex items-center justify-between pt-2 border-t border-[#2a2e39]">
                <div className="flex items-center gap-2">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={idea.symbolLogo} alt="" className="h-4 w-4 rounded-full" />
                  <span className="text-[10px] text-[#2962ff]">{idea.symbol}</span>
                  {idea.signal && (
                    <span
                      className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
                        idea.signal === "Alış" ? "bg-[#089981]/20 text-[#089981]" : "bg-[#f23645]/20 text-[#f23645]"
                      }`}
                    >
                      {idea.signal}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1 text-[10px] text-[#787b86]">
                  <TrendingUpIcon className="h-3 w-3" />
                  <span>{idea.author}</span>
                  <span>·</span>
                  <span>{idea.date}</span>
                </div>
              </div>
            </a>
          ))}
        </div>

        <div className="mt-4">
          <a
            href="https://tr.tradingview.com/ideas/editors-picks/"
            className="text-xs text-[#2962ff] hover:text-[#1e53e5] transition-colors"
          >
            Tüm editörlerin seçtiği fikirleri görün →
          </a>
        </div>
      </div>
    </section>
  )
}
