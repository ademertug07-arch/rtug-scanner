import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/prisma"

export async function GET() {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const alerts = await prisma.alert.findMany({
    where: { userId: session.user.id },
    orderBy: { createdAt: "desc" },
  })
  return NextResponse.json(alerts)
}

export async function POST(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const { symbol, targetPrice, direction, note } = await req.json()
  if (!symbol || !targetPrice || !direction) return NextResponse.json({ error: "symbol, targetPrice, direction required" }, { status: 400 })

  const alert = await prisma.alert.create({
    data: {
      userId: session.user.id,
      symbol: symbol.toUpperCase(),
      targetPrice,
      direction,
      note,
    },
  })
  return NextResponse.json(alert)
}

export async function DELETE(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const id = req.nextUrl.searchParams.get("id")
  if (!id) return NextResponse.json({ error: "id required" }, { status: 400 })

  await prisma.alert.deleteMany({ where: { id, userId: session.user.id } })
  return NextResponse.json({ success: true })
}

export async function PATCH(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const { id, triggered } = await req.json()
  if (!id) return NextResponse.json({ error: "id required" }, { status: 400 })

  await prisma.alert.updateMany({ where: { id, userId: session.user.id }, data: { triggered } })
  return NextResponse.json({ success: true })
}
