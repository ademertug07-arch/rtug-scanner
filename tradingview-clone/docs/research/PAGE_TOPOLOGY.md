# TradingView (tr.tradingview.com) — Page Topology

## Overview
- **URL:** https://tr.tradingview.com/
- **Language:** tr (Turkish)
- **Viewport:** Desktop 1440px, Mobile 390px
- **Page type:** Landing / Market dashboard
- **Scroll behavior:** Native smooth scroll (no Lenis/Locomotive detected)
- **Layout:** Single column, full-viewport sections

## Section List (top to bottom)

### 1. Navigation Bar (fixed)
- **Type:** Fixed top bar
- **Z-index:** High (overlays everything)
- **Interaction model:** Click-driven (dropdowns on hover/click)
- **Contents:**
  - Logo link (TradingView)
  - Nav links: Ürünler, Topluluk, Piyasalar, Aracı kurum, Daha Fazla (each with dropdown menus)
  - Language selector button
  - User menu button
  - CTA: "Şimdi başlat" button
  - Skip to content button (accessibility)
- **States:** Fixed at top; may have scrolled state (shadow)

### 2. Hero Section
- **Type:** Full-width hero banner
- **Contents:**
  - H1: "En iyi işlemler önce araştırma, sonra kararlılık gerektirir."
  - CTA: "Ücretsiz olarak başlayın" link
  - Free tagline: "Sonsuza kadar 0$, kredi kartı gerekmez"
  - Space mission story: "See our space story" + "With astronaut Scott 'Kidd' Poteet"
  - "Uzay görevi" link
- **Interaction model:** Static (no animation detected)

### 3. Market Overview Section
- **Type:** Full-width section
- **Contents:**
  - H2: "Dünya piyasaları nerede"
  - Subtitle: "Geleceği kendi ellerine alan 100 milyon yatırımcıya katılın."
  - "Özellikleri keşfet" link
  - **Tab bar (6 tabs):** Türk hisseleri, Kripto, Vadeli, Foreks, Ekonomi, Aracı kurum
  - **Active tab:** Türk hisseleri (selected by default)
- **Interaction model:** Click-driven tab switching

### 4. Major Indices Grid
- **Type:** Grid of index cards
- **Contents (7 items):**
  - BIST 100 (XU100) — 14.274,02 G +0,10%
  - BIST 50 (XU050) — 12.852,30 +0,16%
  - S&P 500 (SPX) — 7.380,61 USD +0,31%
  - Nasdaq 100 (NDX) — 29.340,18 POINT −0,34%
  - Japan 225 (NI225) — 69.360,66 JPY −4,15%
  - SSE Composite (000001) — 4.027,2648 POINT −2,26%
  - FTSE 100 (UKX) — 10.508,02 POINT −0,21%
- **Footer:** "Tüm büyük endeksleri görün" link
- **Interaction model:** Static (links to detail pages)

### 5. Crypto Market Section
- **Type:** Section with market overview
- **Contents:**
  - Total crypto market cap: TOTAL 2,06T USD −18,12% (1 ay)
  - Bitcoin dominance: BTC 58,59% / ETH 9,30% / Others 32,12%
  - Bitcoin: BTCUSD 60.114 USD +0,70%
  - Ethereum: ETHUSD 1.585,6 USD +1,30%
  - "Tüm kripto paraları gör" link
- **Interaction model:** Static

### 6. Forex / Commodities Section
- **Type:** Section
- **Contents:**
  - USD/TRY: 46,618800 TRY +1,64% (1 ay)
  - Crude Oil: CL1! 69,07 USD/varil −3,96%
  - Natural Gas: NG1! 3,346 USD/milyon BTU +0,09%
  - Gold: GC1! 4.097,2 USD/troy ons +1,23%
  - Copper: HG1! 6,1470 USD/libre +1,20%
  - "Tüm vadelileri gör" link
- **Interaction model:** Static

### 7. Economic Indicators (Turkey)
- **Type:** Section
- **Contents:**
  - Turkey 10-year bond yield: 30,750% (0,00% 1 ay)
  - Turkey annual inflation: TRIRYY (link)
  - Turkey interest rate: Current 37%, Forecast —, Next release 23 Jul 2026
  - "Tüm ekonomik göstergeleri görün" link
- **Interaction model:** Static

### 8. Featured IPOs
- **Type:** Card grid
- **Contents (9 items):**
  - SPCX (SpaceX): Last $157.44, Offer $135.00, Market cap $2.08T
  - STRIPE (Stripe): NASDAQ, Offer —
  - KRAKEN (Payward): NASDAQ, Offer —
  - DISCORD (Discord): NASDAQ, Offer —
  - ANTHROPIC (Anthropic): NASDAQ, Offer —
  - REVOLUT (Revolut): NASDAQ, Offer —
  - OPENAI (OpenAI): NASDAQ, Offer —
  - CANVA (Canva): NASDAQ, Offer —
  - POLYMARKET (Polymarket): NASDAQ, Offer —
- **Footer:** "Daha fazla olay gör" link
- **Interaction model:** Static cards

### 9. Community Ideas
- **Type:** Card feed with tabs
- **Tabs:** Editörün Seçtikleri (selected), Popüler
- **Contents (10+ ideas):** Each with:
  - Title, description text, author avatar/name, date, symbol tag, signal (Alış/Satış)
- **Footer:** "Tüm editörlerin seçtiği fikirleri görün" link
- **Interaction model:** Click-driven tab switching

### 10. Scripts & Indicators
- **Type:** Card feed with tabs
- **Tabs:** Editörün Seçtikleri (selected), Popüler
- **Contents (10+ scripts):** Each with:
  - Script name, description, tag (Pine Script göstergesi / kütüphanesi), author
- **Footer:** "Tüm göstergeleri ve stratejileri görün" link
- **Interaction model:** Click-driven tab switching

### 11. Turkish Stocks Section
- **Type:** Section
- **Contents:**
  - H2: "Türk hisseleri"
  - H3: "Topluluk trendleri" — list of trending stocks (TCKRC, EREGL, VESTL, SNICA, TERA, NETCD, ARCLK, ALARK, PAPIL, INFO)
  - H3: "İşlem fikirleri" — trading ideas cards
- **Interaction model:** Static / links

### 12. Footer
- **Type:** Full-width footer
- **Contents (from app stores snapshot):**
  - Mobile app badges (App Store, Google Play)
  - Exchange/regulation info
  - Link lists (not fully captured in snapshot)

## Global Patterns
- **Background:** Dark theme (#131722 or similar dark blue/navy)
- **Text:** White/light gray (#ffffff, #d1d4dc)
- **Accent:** Blue (#2962FF, #1E53E5) for links/CTAs
- **Positive change:** Green (#089981)
- **Negative change:** Red (#F23645)
- **Cards:** Slightly lighter background (#1e222d)
- **Borders:** Subtle (#2a2e39)
- **Container max-width:** ~1260px centered
