import { NextRequest, NextResponse } from "next/server"
import YahooFinance from "yahoo-finance2"

const yahooFinance = new YahooFinance()

const VALID_RANGES = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"] as const

export async function GET(req: NextRequest) {
  const symbol = req.nextUrl.searchParams.get("symbol")?.toUpperCase()
  const range = (req.nextUrl.searchParams.get("range") || "1mo") as string
  const type = req.nextUrl.searchParams.get("type") || "quote"

  if (!symbol) return NextResponse.json({ error: "Symbol required" }, { status: 400 })

  try {
    if (type === "chart") {
      const validRange = VALID_RANGES.includes(range as any) ? range : "1mo"
      const result = await yahooFinance.chart(symbol, {
        period1: getPeriod1(validRange),
        interval: getInterval(validRange),
      })
      return NextResponse.json(result)
    }

    const quote = await yahooFinance.quote(symbol)
    return NextResponse.json(quote)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch market data", details: String(error) }, { status: 500 })
  }
}

function getPeriod1(range: string): Date {
  const now = new Date()
  switch (range) {
    case "1d": return new Date(now.getTime() - 24 * 60 * 60 * 1000)
    case "5d": return new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000)
    case "1mo": return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    case "3mo": return new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
    case "6mo": return new Date(now.getTime() - 180 * 24 * 60 * 60 * 1000)
    case "1y": return new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000)
    case "5y": return new Date(now.getTime() - 5 * 365 * 24 * 60 * 60 * 1000)
    default: return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
  }
}

function getInterval(range: string): "1m" | "5m" | "15m" | "30m" | "1h" | "1d" | "1wk" {
  switch (range) {
    case "1d": return "5m"
    case "5d": return "15m"
    case "1mo": return "1h"
    case "3mo":
    case "6mo": return "1d"
    default: return "1wk"
  }
}
