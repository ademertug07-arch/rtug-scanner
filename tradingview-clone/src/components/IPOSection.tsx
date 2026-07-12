import type { IPOSummary } from "@/types/market"
import { ExternalLinkIcon } from "./icons"

const IPOS: IPOSummary[] = [
  { date: "12 Haz", symbol: "SPCX", companyName: "Space Exploration Technologies Corp", exchange: "NASDAQ", lastPrice: "157,44", offerPrice: "135,00", marketCap: "‪2,08 T", currency: "USD" },
  { date: "18 Eyl", symbol: "STRIPE", companyName: "Stripe Inc.", exchange: "NASDAQ", offerPrice: "—" },
  { date: "9 Eki", symbol: "KRAKEN", companyName: "Payward Inc. (KRAKEN)", exchange: "NASDAQ", offerPrice: "—" },
  { date: "16 Eki", symbol: "DISCORD", companyName: "Discord Inc.", exchange: "NASDAQ", offerPrice: "—" },
  { date: "23 Eki", symbol: "ANTHROPIC", companyName: "Anthropic PBC", exchange: "NASDAQ", offerPrice: "—" },
  { date: "30 Eki", symbol: "REVOLUT", companyName: "Revolut Ltd.", exchange: "NASDAQ", offerPrice: "—" },
  { date: "27 Kas", symbol: "OPENAI", companyName: "OpenAI", exchange: "NASDAQ", offerPrice: "—" },
  { date: "14 May", symbol: "CANVA", companyName: "Canva Pty. Ltd.", exchange: "NASDAQ", offerPrice: "—" },
  { date: "21 May", symbol: "POLYMARKET", companyName: "Polymarket", exchange: "NASDAQ", offerPrice: "—" },
]

export default function IPOSection() {
  return (
    <section className="bg-black py-8 md:py-12">
      <div className="mx-auto max-w-[1260px] px-4">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-[#f7f8f8]">Featured IPOs</h3>
          <a
            href="https://tr.tradingview.com/ipo-calendar/?countries=us"
            className="flex items-center gap-1 text-xs text-[#787b86] hover:text-[#f7f8f8] transition-colors"
          >
            Daha fazla olay gör
            <ExternalLinkIcon className="h-3 w-3" />
          </a>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {IPOS.map((ipo) => (
            <a
              key={ipo.symbol}
              href={`https://tr.tradingview.com/symbols/NASDAQ-${ipo.symbol}/`}
              className="flex flex-col gap-1 rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-[#787b86] uppercase">{ipo.date}</span>
                <span className="text-xs font-bold text-[#f7f8f8]">{ipo.symbol}</span>
              </div>
              <span className="text-xs text-[#f7f8f8] line-clamp-1">{ipo.companyName}</span>
              {ipo.lastPrice && (
                <div className="flex items-center gap-1 mt-1">
                  <span className="text-[10px] text-[#787b86]">Son</span>
                  <span className="text-sm font-semibold text-[#f7f8f8]">{ipo.lastPrice}</span>
                  <span className="text-[10px] text-[#787b86]">{ipo.currency}</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-[10px] text-[#787b86]">
                <span>Teklif fiyatı {ipo.offerPrice}</span>
                {ipo.marketCap && <span>Piyasa değeri {ipo.marketCap} {ipo.currency}</span>}
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}
