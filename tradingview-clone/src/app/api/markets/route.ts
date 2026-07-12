import { NextResponse } from "next/server"
import YahooFinance from "yahoo-finance2"

const yahooFinance = new YahooFinance()

const SYMBOLS = {
  indices: ["^XU100", "^XU050", "^GSPC", "^NDX", "^N225", "000001.SS", "^FTSE", "^DJI", "^HSI", "^VIX"],
  crypto: ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "DOT-USD"],
  forex: ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDTRY=X", "EURTRY=X", "AUDUSD=X", "USDCAD=X"],
  commodities: ["GC=F", "CL=F", "NG=F", "SI=F", "HG=F"],
  turkish: ["THYAO.IS", "EREGL.IS", "AKBNK.IS", "GARAN.IS", "KCHOL.IS", "SAHOL.IS", "TUPRS.IS", "ASELS.IS", "SISE.IS", "BIMAS.IS"],
}

export async function GET() {
  const allSymbols = Object.values(SYMBOLS).flat()
  const uniqueSymbols = [...new Set(allSymbols)]

  try {
    const quotes = await yahooFinance.quote(uniqueSymbols)

    const grouped: Record<string, any[]> = {
      indices: [], crypto: [], forex: [], commodities: [], turkish: [],
    }

    const quoteArray = Array.isArray(quotes) ? quotes : [quotes]
    const symbolMap = new Map(quoteArray.map((q: any) => [q.symbol, q]))

    for (const [group, syms] of Object.entries(SYMBOLS)) {
      for (const sym of syms) {
        const q = symbolMap.get(sym)
        if (q) {
          grouped[group].push({
            symbol: sym,
            name: q.shortName || q.longName || sym,
            price: q.regularMarketPrice,
            change: q.regularMarketChange,
            changePercent: q.regularMarketChangePercent,
            volume: q.regularMarketVolume,
            high: q.regularMarketDayHigh,
            low: q.regularMarketDayLow,
            open: q.regularMarketOpen,
            previousClose: q.regularMarketPreviousClose,
            marketState: q.marketState,
          })
        }
      }
    }

    return NextResponse.json(grouped, {
      headers: { "Cache-Control": "no-cache, max-age=0, must-revalidate" },
    })
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch market data", details: String(error) }, { status: 500 })
  }
}
