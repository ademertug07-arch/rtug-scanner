const FOOTER_SECTIONS = [
  {
    title: "TradingView",
    links: [
      { label: "Sosyal ağ", url: "https://tr.tradingview.com/social/" },
      { label: "Öne çıkan gönderiler", url: "https://tr.tradingview.com/feed/" },
      { label: "Piyasalar", url: "https://tr.tradingview.com/markets/" },
      { label: "Kripto", url: "https://tr.tradingview.com/crypto/" },
      { label: "Vadeli işlemler", url: "https://tr.tradingview.com/futures/" },
      { label: "Forex", url: "https://tr.tradingview.com/forex/" },
      { label: "Ekonomi", url: "https://tr.tradingview.com/markets/currencies/" },
      { label: "Charts", url: "https://tr.tradingview.com/chart/" },
      { label: "Tarama", url: "https://tr.tradingview.com/screener/" },
      { label: "Göstergeler ve stratejiler", url: "https://tr.tradingview.com/scripts/" },
      { label: "Ticaret fikirlerim", url: "https://tr.tradingview.com/u/#/ideas/" },
    ],
  },
  {
    title: "Sitenin Özellikleri",
    links: [
      { label: "Normal hisse senetleri", url: "https://tr.tradingview.com/screener/" },
      { label: "Döviz çapraz kurları", url: "https://tr.tradingview.com/forex/" },
      { label: "Kripto paralar", url: "https://tr.tradingview.com/crypto/" },
      { label: "Vadeli işlemler", url: "https://tr.tradingview.com/futures/" },
      { label: "Borsa endeksleri", url: "https://tr.tradingview.com/markets/indices/" },
      { label: "Tahviller", url: "https://tr.tradingview.com/markets/bonds/" },
      { label: "ETF'ler", url: "https://tr.tradingview.com/markets/etfs/" },
      { label: "Sektörler", url: "https://tr.tradingview.com/markets/sectors/" },
      { label: "Küresel ekonomik takvim", url: "https://tr.tradingview.com/economic-calendar/" },
      { label: "IPO (Halka arz) takvimi", url: "https://tr.tradingview.com/ipo-calendar/" },
      { label: "Borsa kâr ve zarar hesaplayıcı", url: "https://tr.tradingview.com/profit-calculator/" },
    ],
  },
  {
    title: "Ürünler",
    links: [
      { label: "Hisse senedi tarama", url: "https://tr.tradingview.com/screener/" },
      { label: "Forex tarama", url: "https://tr.tradingview.com/forex-screener/" },
      { label: "Kripto para tarama", url: "https://tr.tradingview.com/crypto-screener/" },
      { label: "Kâr ve zarar hesaplayıcı", url: "https://tr.tradingview.com/profit-calculator/" },
      { label: "Widget'lar", url: "https://tr.tradingview.com/widget/" },
      { label: "Brokerler", url: "https://tr.tradingview.com/broker/" },
      { label: "Macd", url: "https://tr.tradingview.com/support/solutions/43000502022-macd-indicator/" },
      { label: "Rsi", url: "https://tr.tradingview.com/support/solutions/43000502338-relative-strength-index-rsi/" },
      { label: "Sinyal", url: "https://tr.tradingview.com/signals/" },
      { label: "Papağan", url: "https://tr.tradingview.com/support/solutions/43000595494-parabolic-sar/" },
      { label: "Sitemap", url: "https://tr.tradingview.com/sitemap/" },
    ],
  },
  {
    title: "Çözümler",
    links: [
      { label: "Premium", url: "https://tr.tradingview.com/pricing/" },
      { label: "Bireysel yatırımcılar için", url: "https://tr.tradingview.com/retail/" },
      { label: "Kurumlar için", url: "https://tr.tradingview.com/institutional/" },
      { label: "Girişimler için", url: "https://tr.tradingview.com/startups/" },
      { label: "For brokers", url: "https://tr.tradingview.com/broker/" },
      { label: "Sitelere yerleştir", url: "https://tr.tradingview.com/widget/" },
      { label: "Akış verileri", url: "https://tr.tradingview.com/feed/" },
      { label: "TV yayın yönetimine hoş geldiniz", url: "https://tr.tradingview.com/broadcasting/" },
      { label: "Brokerler", url: "https://tr.tradingview.com/broker/" },
    ],
  },
  {
    title: "Hakkında",
    links: [
      { label: "Hakkımızda", url: "https://tr.tradingview.com/about/" },
      { label: "Basın odası", url: "https://tr.tradingview.com/press/" },
      { label: "Müşteri referansları", url: "https://tr.tradingview.com/testimonials/" },
      { label: "Kariyer", url: "https://tr.tradingview.com/careers/" },
      { label: "Açık kaynak katkıları", url: "https://tr.tradingview.com/opensource/" },
      { label: "Fiyatlandırma", url: "https://tr.tradingview.com/pricing/" },
      { label: "Kampanyalar", url: "https://tr.tradingview.com/promotions/" },
      { label: "YouTube", url: "https://www.youtube.com/channel/UCe7fQke1Mz4F4Y5Srh_3t2A" },
    ],
  },
  {
    title: "Yardım",
    links: [
      { label: "Destek Merkezi", url: "https://tr.tradingview.com/support/" },
      { label: "Video eğitimleri", url: "https://tr.tradingview.com/support/solutions/43000501964-video-tutorials/" },
      { label: "Yasal düzenlemeler", url: "https://tr.tradingview.com/support/solutions/43000501962-regulatory-standards/" },
      { label: "Yasal koşullar", url: "https://tr.tradingview.com/support/solutions/43000501963-legal-conditions/" },
      { label: "Gizlilik politikası", url: "https://tr.tradingview.com/support/solutions/43000501958-privacy-policy/" },
      { label: "çerez politikası", url: "https://tr.tradingview.com/support/solutions/43000501956-cookie-policy/" },
      { label: "Risk uyarısı", url: "https://tr.tradingview.com/support/solutions/43000501959-risk-warning/" },
      { label: "Kullanım koşulları", url: "https://tr.tradingview.com/support/solutions/43000501960-terms-of-use/" },
      { label: "Sorumluluk reddi beyanı", url: "https://tr.tradingview.com/support/solutions/43000501955-disclaimer/" },
      { label: "Basın", url: "https://tr.tradingview.com/press/" },
    ],
  },
  {
    title: "Bize ulaşın",
    links: [
      { label: "Yasal işlemler", url: "mailto:legal@tradingview.com" },
      { label: "AB Temsilcimiz", url: "https://prighter.com/q/16306305795/" },
      { label: "İngiltere Temsilcimiz", url: "https://prighter.com/q/16651289811/" },
      { label: "Telif hakkı bildirimi", url: "https://tr.tradingview.com/copyright/" },
      { label: "Geri bildirim", url: "https://tr.tradingview.com/feedback/" },
    ],
  },
  {
    title: "Popüler Semboller",
    links: [
      { label: "SPX", url: "https://tr.tradingview.com/symbols/SPX/" },
      { label: "AAPL", url: "https://tr.tradingview.com/symbols/AAPL/" },
      { label: "TSLA", url: "https://tr.tradingview.com/symbols/TSLA/" },
      { label: "NVDA", url: "https://tr.tradingview.com/symbols/NVDA/" },
      { label: "EURUSD", url: "https://tr.tradingview.com/symbols/EURUSD/" },
      { label: "BTCUSD", url: "https://tr.tradingview.com/symbols/BTCUSD/" },
      { label: "ETHUSD", url: "https://tr.tradingview.com/symbols/ETHUSD/" },
      { label: "XAUUSD", url: "https://tr.tradingview.com/symbols/XAUUSD/" },
      { label: "AAPL", url: "https://tr.tradingview.com/symbols/AAPL/" },
      { label: "TSLA", url: "https://tr.tradingview.com/symbols/TSLA/" },
      { label: "NVDA", url: "https://tr.tradingview.com/symbols/NVDA/" },
      { label: "EURUSD", url: "https://tr.tradingview.com/symbols/EURUSD/" },
      { label: "BTCUSD", url: "https://tr.tradingview.com/symbols/BTCUSD/" },
      { label: "ETHUSD", url: "https://tr.tradingview.com/symbols/ETHUSD/" },
      { label: "XAUUSD", url: "https://tr.tradingview.com/symbols/XAUUSD/" },
    ],
  },
]

export default function Footer() {
  return (
    <footer className="bg-[#0f0f0f] py-8 md:py-12">
      <div className="mx-auto max-w-[1260px] px-4">
        <div className="flex items-center gap-3 mb-10">
          <svg viewBox="0 0 40 40" className="h-8 w-8" fill="none">
            <rect width="40" height="40" rx="8" fill="#2962ff" />
            <path d="M12 28L20 12l8 16H12z" fill="white" />
          </svg>
          <span className="text-lg font-semibold text-[#f7f8f8]">TradingView</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-8 gap-6">
          {FOOTER_SECTIONS.map((section) => (
            <div key={section.title}>
              <h4 className="text-xs font-semibold text-[#787b86] uppercase mb-3 tracking-wider">{section.title}</h4>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.url}
                      className="text-xs text-[#787b86] hover:text-[#f7f8f8] transition-colors"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 pt-8 border-t border-[#2a2e39]">
          <p className="text-[10px] text-[#434651] leading-relaxed text-center">
            © 2025 TradingView. Tüm hakları saklıdır.
            <br />
            Bu site TradingView&apos;in resmi olmayan bir UI klonudur. Yalnızca eğitim ve görsel referans amaçlıdır.
            <br />
            Tüm ticari markalar, logolar ve marka isimleri ilgili sahiplerinin mülkiyetindedir.
          </p>
        </div>
      </div>
    </footer>
  )
}
