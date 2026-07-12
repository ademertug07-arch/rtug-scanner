"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { signIn } from "next-auth/react"

export default function RegisterPage() {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError("")

    const res = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    })

    if (!res.ok) {
      const data = await res.json()
      setError(data.error || "Registration failed")
      setLoading(false)
      return
    }

    await signIn("credentials", { email, password, redirect: false })
    router.push("/dashboard")
    router.refresh()
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-black px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-lg bg-[#1e222d] p-8">
        <h1 className="mb-6 text-2xl font-semibold text-[#f7f8f8]">Kayıt Ol</h1>

        {error && <p className="mb-4 text-sm text-[#f23645]">{error}</p>}

        <div className="mb-4">
          <label className="mb-1 block text-xs text-[#787b86]" htmlFor="name">İsim</label>
          <input
            id="name" type="text" value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-md border border-[#2a2e39] bg-[#0f0f0f] px-3 py-2 text-sm text-[#f7f8f8] outline-none focus:border-[#2962ff]"
          />
        </div>

        <div className="mb-4">
          <label className="mb-1 block text-xs text-[#787b86]" htmlFor="email">Email</label>
          <input
            id="email" type="email" value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-[#2a2e39] bg-[#0f0f0f] px-3 py-2 text-sm text-[#f7f8f8] outline-none focus:border-[#2962ff]"
            required
          />
        </div>

        <div className="mb-6">
          <label className="mb-1 block text-xs text-[#787b86]" htmlFor="password">Şifre</label>
          <input
            id="password" type="password" value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-[#2a2e39] bg-[#0f0f0f] px-3 py-2 text-sm text-[#f7f8f8] outline-none focus:border-[#2962ff]"
            required
            minLength={6}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-[#2962ff] py-2 text-sm font-medium text-white hover:bg-[#1e53e5] disabled:opacity-50"
        >
          {loading ? "Kaydediliyor..." : "Kayıt Ol"}
        </button>

        <p className="mt-4 text-center text-xs text-[#787b86]">
          Zaten hesabın var mı?{" "}
          <a href="/login" className="text-[#2962ff] hover:underline">Giriş Yap</a>
        </p>
      </form>
    </div>
  )
}
