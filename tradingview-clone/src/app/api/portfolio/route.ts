import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/prisma"

export async function GET() {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const items = await prisma.portfolio.findMany({
    where: { userId: session.user.id },
    orderBy: { createdAt: "desc" },
  })
  return NextResponse.json(items)
}

export async function POST(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const { symbol, quantity, avgPrice } = await req.json()
  if (!symbol || !quantity || !avgPrice) return NextResponse.json({ error: "symbol, quantity, avgPrice required" }, { status: 400 })

  const existing = await prisma.portfolio.findUnique({
    where: { userId_symbol: { userId: session.user.id, symbol: symbol.toUpperCase() } },
  })

  if (existing) {
    const totalQty = existing.quantity + quantity
    const totalCost = existing.quantity * existing.avgPrice + quantity * avgPrice
    const item = await prisma.portfolio.update({
      where: { id: existing.id },
      data: { quantity: totalQty, avgPrice: totalCost / totalQty },
    })
    return NextResponse.json(item)
  }

  const item = await prisma.portfolio.create({
    data: { userId: session.user.id, symbol: symbol.toUpperCase(), quantity, avgPrice },
  })
  return NextResponse.json(item)
}

export async function DELETE(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const id = req.nextUrl.searchParams.get("id")
  if (!id) return NextResponse.json({ error: "id required" }, { status: 400 })

  await prisma.portfolio.deleteMany({ where: { id, userId: session.user.id } })
  return NextResponse.json({ success: true })
}
