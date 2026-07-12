import { ArrowRightIcon } from "./icons"

export default function HeroSection() {
  return (
    <section className="relative mt-14 overflow-hidden bg-[#0f0f0f]">
      <div className="mx-auto max-w-[1260px] px-4 py-16 md:py-24">
        <div className="max-w-2xl">
          <h1 className="text-[28px] md:text-[40px] lg:text-[56px] font-bold leading-tight text-[#0f0f0f]">
            En iyi işlemler önce araştırma, sonra kararlılık gerektirir.
          </h1>

          <div className="mt-8 flex flex-col sm:flex-row items-start gap-4">
            <a
              href="https://tr.tradingview.com/pricing/?source=promo_go_pro_button"
              className="inline-flex items-center gap-2 rounded-full bg-[#2962ff] px-6 py-3 text-sm font-medium text-white hover:bg-[#1e53e5] transition-colors"
            >
              Ücretsiz olarak başlayın
              <ArrowRightIcon className="h-4 w-4" />
            </a>
            <span className="text-xs text-[#787b86] pt-3">
              Sonsuza kadar 0$, kredi kartı gerekmez
            </span>
          </div>

          <div className="mt-12 flex items-center gap-3">
            <span className="text-xs text-[#787b86]">See our space story</span>
            <span className="text-xs text-[#787b86]">With astronaut Scott &ldquo;Kidd&rdquo; Poteet</span>
            <a
              href="https://tr.tradingview.com/space-mission/"
              className="inline-flex items-center gap-1 text-xs font-medium text-[#2962ff] hover:text-[#1e53e5] transition-colors"
            >
              Uzay görevi
              <ArrowRightIcon className="h-3 w-3" />
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
