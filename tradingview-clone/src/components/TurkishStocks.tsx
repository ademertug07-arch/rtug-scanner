import type { TurkishStock, TradingIdea } from "@/types/market"
import { ArrowRightIcon } from "./icons"

const TRENDING_STOCKS: TurkishStock[] = [
  { symbol: "TCKRC", name: "Kirac Galvaniz Telekominikasyon Metal Makine Insaat Elektrik Sanayi Ve Ticaret AS", link: "https://tr.tradingview.com/symbols/BIST-TCKRC/" },
  { symbol: "EREGL", name: "EREĞLİ DEMİR VE ÇELİK FABRİKALARI T.A.Ş.", link: "https://tr.tradingview.com/symbols/BIST-EREGL/" },
  { symbol: "VESTL", name: "VESTEL ELEKTRONİK SANAYİ VE TİCARET A.Ş.", link: "https://tr.tradingview.com/symbols/BIST-VESTL/" },
  { symbol: "SNICA", name: "SANİCA ISI SANAYİ A.Ş.", link: "https://tr.tradingview.com/symbols/BIST-SNICA/" },
  { symbol: "TERA", name: "TERA YATIRIM MENKUL DEĞERLER A.Ş.", link: "https://tr.tradingview.com/symbols/BIST-TERA/" },
  { symbol: "NETCD", name: "Netcad Yazilim A.S.", link: "https://tr.tradingview.com/symbols/BIST-NETCD/" },
  { symbol: "ARCLK", name: "ARÇELİK A.Ş.", link: "https://tr.tradingview.com/symbols/BIST-ARCLK/" },
  { symbol: "ALARK", name: "ALARKO HOLDİNG A.Ş.", link: "https://tr.tradingview.com/symbols/BIST-ALARK/" },
  { symbol: "PAPIL", name: "PAPİLON SAVUNMA TEKNOLOJİ VE TİCARET A.Ş.", link: "https://tr.tradingview.com/symbols/BIST-PAPIL/" },
  { symbol: "INFO", name: "İNFO YATIRIM MENKUL DEĞERLER A.Ş.", link: "https://tr.tradingview.com/symbols/BIST-INFO/" },
]

const STOCK_IDEAS: TradingIdea[] = [
  {
    title: "OZRDN BOĞA RALLİSİ BAŞLATIR MI?",
    description: "ÖZRDN oluşturduğu çanak formasyonunu kırdı.",
    symbol: "BIST:OZRDN", symbolLogo: "https://s3-symbol-logo.tradingview.com/ozerden-plastik.svg",
    author: "Eurolizm", authorUrl: "https://tr.tradingview.com/u/Eurolizm/",
    date: "Haz 25", link: "https://tr.tradingview.com/chart/OZRDN/AVFBAMDA/",
  },
  {
    title: "Aagyo Butterfly Egitim Asla Ytd ...",
    description: "Butterfly (Kelebek) formasyonu, finansal piyasalardaki olası trend dönüşlerini tespit etmek için kullanılan beş noktalı bir harmonik grafik desenidir.",
    symbol: "BIST:AAGYO", symbolLogo: "https://s3-symbol-logo.tradingview.com/agaoglu-avrasya-gayrimenkul-yatirim-ortakligi-as.svg",
    author: "bisttekniknoktacom", authorUrl: "https://tr.tradingview.com/u/bisttekniknoktacom/",
    date: "Haz 25", signal: "Alış", link: "https://tr.tradingview.com/chart/AAGYO/orGbAoor/",
  },
  {
    title: "TTRAK Türk Traktör ve Ziraat Makineleri A.Ş. — 1G Grafik",
    description: "TTRAK | Harmonik Formasyon + Talep Bölgesi Analizi",
    symbol: "BIST:TTRAK", symbolLogo: "https://s3-symbol-logo.tradingview.com/turk-traktor.svg",
    author: "Ardella", authorUrl: "https://tr.tradingview.com/u/Ardella/",
    date: "Haz 25", signal: "Alış", link: "https://tr.tradingview.com/chart/TTRAK/tEx8tuTm/",
  },
  {
    title: "GOZDE Teknik Analiz Raporu",
    description: "Gözde Girişim, Yıldız Pazar'da işlem gören, 385 milyon TL seviyesindeki ödenmiş sermayesiyle çevik bir yapıya sahiptir.",
    symbol: "BIST:GOZDE", symbolLogo: "https://s3-symbol-logo.tradingview.com/gozde-girisim.svg",
    author: "asilturk", authorUrl: "https://tr.tradingview.com/u/asilturk/",
    date: "Haz 25", signal: "Alış", link: "https://tr.tradingview.com/chart/GOZDE/yl5lqcXF/",
  },
  {
    title: "BOBET Fiyat: 19.16 - En kötüsü geride kalmış olabilir mi?",
    description: "BOBET teknik analiz ve değerlendirme.",
    symbol: "BIST:BOBET", symbolLogo: "",
    author: "analyst", authorUrl: "#",
    date: "Haz 25", link: "#",
  },
]

export default function TurkishStocks() {
  return (
    <section className="bg-black py-8 md:py-12">
      <div className="mx-auto max-w-[1260px] px-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl md:text-3xl font-semibold text-white leading-tight">Türk hisseleri</h2>
          <a
            href="https://tr.tradingview.com/markets/stocks-turkey/"
            className="flex items-center gap-1 text-xs text-[#787b86] hover:text-[#f7f8f8] transition-colors"
          >
            Tümünü gör <ArrowRightIcon className="h-3 w-3" />
          </a>
        </div>

        <h3 className="text-sm font-medium text-[#787b86] mb-3">Topluluk trendleri</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 mb-8">
          {TRENDING_STOCKS.map((stock) => (
            <a
              key={stock.symbol}
              href={stock.link}
              className="flex flex-col gap-0.5 rounded-lg bg-[#1e222d] p-3 hover:bg-[#2a2e39] transition-colors"
            >
              <span className="text-sm font-semibold text-[#f7f8f8]">{stock.symbol}</span>
              <span className="text-[10px] text-[#787b86] line-clamp-1">{stock.name}</span>
            </a>
          ))}
        </div>

        <div className="border-t border-[#2a2e39] pt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-[#f7f8f8]">İşlem fikirleri</h3>
            <a
              href="https://tr.tradingview.com/markets/stocks-turkey/ideas/"
              className="flex items-center gap-1 text-xs text-[#787b86] hover:text-[#f7f8f8] transition-colors"
            >
              Tümünü gör <ArrowRightIcon className="h-3 w-3" />
            </a>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {STOCK_IDEAS.map((idea, i) => (
              <a
                key={i}
                href={idea.link}
                className="flex flex-col gap-2 rounded-lg bg-[#1e222d] p-4 hover:bg-[#2a2e39] transition-colors"
              >
                <span className="text-sm font-medium text-[#f7f8f8] line-clamp-2 leading-snug">{idea.title}</span>
                <p className="text-xs text-[#787b86] line-clamp-2">{idea.description}</p>
                <div className="mt-auto flex items-center justify-between pt-2 border-t border-[#2a2e39]">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-[#2962ff]">{idea.symbol}</span>
                    {idea.signal && (
                      <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${idea.signal === "Alış" ? "bg-[#089981]/20 text-[#089981]" : "bg-[#f23645]/20 text-[#f23645]"}`}>
                        {idea.signal}
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] text-[#787b86]">{idea.author} · {idea.date}</span>
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
