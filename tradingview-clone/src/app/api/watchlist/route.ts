import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/prisma"

export async function GET() {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const items = await prisma.watchlist.findMany({
    where: { userId: session.user.id },
    orderBy: { createdAt: "desc" },
  })
  return NextResponse.json(items)
}

export async function POST(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const { symbol, note } = await req.json()
  if (!symbol) return NextResponse.json({ error: "Symbol required" }, { status: 400 })

  const item = await prisma.watchlist.create({
    data: { userId: session.user.id, symbol: symbol.toUpperCase(), note },
  })
  return NextResponse.json(item)
}

export async function DELETE(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const symbol = req.nextUrl.searchParams.get("symbol")?.toUpperCase()
  if (!symbol) return NextResponse.json({ error: "Symbol required" }, { status: 400 })

  await prisma.watchlist.deleteMany({ where: { userId: session.user.id, symbol } })
  return NextResponse.json({ success: true })
}
