# TradingView — Behavior Research

## Interaction Sweep Results

### Scroll Behavior
- **Header:** Fixed top bar (position: fixed). No visible shrink/grow on scroll detected.
- **Scroll-driven animations:** None detected (no fade-in, slide-up, or parallax observed)
- **Smooth scroll:** Browser default (no Lenis or Locomotive classes detected)
- **Scroll snap:** None detected
- **Sticky elements:** Only the header is fixed

### Click Interactions
- **Nav dropdowns:** Each main nav item (Ürünler, Topluluk, Piyasalar, Aracı kurum, Daha Fazla) has an expandable popup menu (haspopup="menu")
- **Language selector:** Click to open language menu (haspopup="menu")
- **User menu:** Click to open user menu
- **Tab switching (Market overview):** 6 tabs — clicking switches visible content (not yet tested per tab)
- **Tab switching (Community ideas):** "Editörün Seçtikleri" / "Popüler" tabs
- **Tab switching (Scripts):** "Editörün Seçtikleri" / "Popüler" tabs
- **Card clicks:** Every card/instrument links to its detail page

### Hover States
- **Nav links:** Hover likely triggers underline or color change (standard web pattern)
- **CTA buttons:** Hover likely changes background shade or adds shadow
- **Cards:** Hover may highlight border or background
- **Links:** Standard color/text-decoration changes expected

### Responsive Behavior
- **Desktop (1440px):** Multi-column layouts for indices grid, IPO cards, idea cards
- **Mobile (390px):** All sections stack vertically, font sizes reduce, cards become full-width
- **Breakpoints:** TV uses standard breakpoints (~768px tablet, ~480px mobile)

### Tab Content States (Market Overview - Pending Extraction)
- Tab 1: Türk hisseleri — Turkish stock indices + data
- Tab 2: Kripto — Cryptocurrency prices
- Tab 3: Vadeli — Futures/commodities
- Tab 4: Foreks — Forex pairs
- Tab 5: Ekonomi — Economic indicators
- Tab 6: Aracı kurum — Broker information
- **Note:** Only Tab 1 (Türk hisseleri) is visible on page load. Other tabs need clicking.

### Tab Content States (Community Ideas)
- Tab 1: Editörün Seçtikleri (selected by default)
- Tab 2: Popüler — popular community ideas

### Tab Content States (Scripts)
- Tab 1: Editörün Seçtikleri (selected by default)
- Tab 2: Popüler — popular scripts
