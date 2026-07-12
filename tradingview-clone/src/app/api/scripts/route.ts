import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/prisma"

export async function GET(req: NextRequest) {
  const session = await auth()
  const template = req.nextUrl.searchParams.get("template")

  if (template === "true") {
    const templates = await prisma.script.findMany({
      where: { isTemplate: true },
      orderBy: { name: "asc" },
    })
    return NextResponse.json(templates)
  }

  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const scripts = await prisma.script.findMany({
    where: { userId: session.user.id },
    orderBy: { updatedAt: "desc" },
  })
  return NextResponse.json(scripts)
}

export async function POST(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const { name, description, code, category } = await req.json()
  if (!name || !code) return NextResponse.json({ error: "Name and code required" }, { status: 400 })

  const script = await prisma.script.create({
    data: { userId: session.user.id, name, description, code, category: category || "custom" },
  })
  return NextResponse.json(script)
}

export async function PUT(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const { id, name, description, code } = await req.json()
  if (!id) return NextResponse.json({ error: "Id required" }, { status: 400 })

  const existing = await prisma.script.findUnique({ where: { id } })
  if (!existing || existing.userId !== session.user.id) {
    return NextResponse.json({ error: "Not found" }, { status: 404 })
  }

  const script = await prisma.script.update({
    where: { id },
    data: { name, description, code },
  })
  return NextResponse.json(script)
}

export async function DELETE(req: NextRequest) {
  const session = await auth()
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })

  const id = req.nextUrl.searchParams.get("id")
  if (!id) return NextResponse.json({ error: "Id required" }, { status: 400 })

  const existing = await prisma.script.findUnique({ where: { id } })
  if (!existing || existing.userId !== session.user.id) {
    return NextResponse.json({ error: "Not found" }, { status: 404 })
  }

  await prisma.script.delete({ where: { id } })
  return NextResponse.json({ success: true })
}
