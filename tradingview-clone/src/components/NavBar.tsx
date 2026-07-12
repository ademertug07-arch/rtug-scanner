"use client"

import { useState } from "react"
import { SearchIcon, GlobeIcon, UserIcon, ArrowRightIcon } from "./icons"
import TickerBar from "./TickerBar"

const NAV_LINKS = [
  { label: "Piyasalar", url: "/markets" },
  { label: "Dashboard", url: "/dashboard" },
  { label: "Pine Editor", url: "/pine-editor" },
  { label: "Topluluk", url: "/ideas" },
  { label: "Aracı kurum", url: "/brokers" },
  { label: "Daha Fazla", url: "/support" },
]

export default function NavBar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <>
      <TickerBar />
      <header className="fixed top-8 left-0 right-0 z-50 bg-black/95 backdrop-blur-sm border-b border-[#2a2e39]">
      <div className="mx-auto flex h-14 items-center justify-between px-4 max-w-[1260px]">
        <div className="flex items-center gap-6">
          <a href="/" className="flex items-center gap-2">
            <img src="/tradertug.png" alt="tradertuğ" className="h-8 w-auto rounded-full" />
            <span className="text-[#f7f8f8] font-semibold text-base">tradertuğ</span>
          </a>
          <nav className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map((link) => (
              <a
                key={link.label}
                href={link.url}
                className="px-3 py-1.5 text-sm font-medium text-[#f7f8f8] hover:text-white/80 transition-colors rounded-md"
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <button className="p-2 text-[#787b86] hover:text-[#f7f8f8] transition-colors rounded-md" aria-label="Ara">
            <SearchIcon className="h-5 w-5" />
          </button>
          <button
            className="hidden md:flex p-2 text-[#787b86] hover:text-[#f7f8f8] transition-colors rounded-md"
            aria-label="Dil menüsünü açın"
          >
            <GlobeIcon className="h-5 w-5" />
          </button>
          <button
            className="hidden md:flex p-2 text-[#787b86] hover:text-[#f7f8f8] transition-colors rounded-md"
            aria-label="Kullanıcı menüsünü aç"
          >
            <UserIcon className="h-5 w-5" />
          </button>
          <a
            href="/register"
            className="ml-2 flex items-center gap-1 rounded-full bg-[#2962ff] px-5 py-1.5 text-sm font-medium text-white hover:bg-[#1e53e5] transition-colors"
          >
            Şimdi başlat
            <ArrowRightIcon className="h-3.5 w-3.5" />
          </a>
          <button
            className="md:hidden p-2 text-[#f7f8f8]"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Menü"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#2a2e39] bg-black">
          <div className="px-4 py-3 space-y-1">
            {NAV_LINKS.map((link) => (
              <a
                key={link.label}
                href={link.url}
                className="block px-3 py-2 text-sm text-[#f7f8f8] hover:bg-[#1e222d] rounded-md"
              >
                {link.label}
              </a>
            ))}
            <hr className="border-[#2a2e39] my-2" />
            <button className="flex w-full items-center gap-2 px-3 py-2 text-sm text-[#787b86]">
              <GlobeIcon className="h-4 w-4" />
              Dil
            </button>
            <button className="flex w-full items-center gap-2 px-3 py-2 text-sm text-[#787b86]">
              <UserIcon className="h-4 w-4" />
              Giriş Yap
            </button>
          </div>
        </div>
      )}
    </header>
    </>
  )
}
