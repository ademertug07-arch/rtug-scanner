---
description: FULL FUNCTIONAL CLONE — reverse-engineer any site into pixel-perfect + behaviorally identical Next.js + shadcn/ui + Tailwind v4 replica. 8-phase pipeline + live data mode. Eklentiler, özellikler, işleyiş, canlı veri dahil.
model: deepseek-v4
---

# CLONE WEBSITE — 8-Phase Full Functional Replication Pipeline

Reverse-engineer any website into a **pixel-perfect, functionally identical** Next.js 16 + shadcn/ui + Tailwind v4 replica. Görsel değil, **davranışsal birebir klon**.

## Trigger Keywords
```
clone | klonla | klonunu yap | kopyasını çıkar | birebir aynısını yap
reverse engineer et | siteyi analiz et | replika yap | website clone
site kopyala | reverse-engineer site | kopya site | aynısını yap
şu siteyi | bu siteyi
oyun klonla | game clone | oyun bölümü | game section clone
oyun içi bölüm | game level clone | oyun sahnesi | game scene clone
```

## Usage
```
clone https://example.com                    # visual + functional clone (hybrid)
clone https://example.com --live             # CANLI VERI — API proxy + data clone + real-time mirror
clone https://example.com --full             # full backend + real-time + auth (recreated)
clone https://example.com --static           # MSW-mocked, no backend
clone https://example.com --proxy            # proxy original APIs only
clone https://example.com --mcp chrome-devtools  # choose browser MCP
```

---

## Pipeline (8 Aşama)

### PHASE 0: Stack Detection (Stack Tespiti)
Before anything else, identify the target's tech stack:
- **Framework**: React, Vue, Angular, Svelte, Next, Nuxt, Astro, Laravel, Django...
- **State Management**: Redux, Zustand, Pinia, Vuex, Jotai, Recoil
- **API Layer**: REST, GraphQL, tRPC, WebSocket, SSE, gRPC-web
- **Auth**: JWT, OAuth, Session, Firebase Auth, Supabase Auth, Clerk, Auth0
- **Database**: Firebase, Supabase, MongoDB, PostgreSQL, Prisma, Drizzle
- **Styling**: Tailwind, CSS Modules, Styled Components, Material UI, Chakra
- **Animations**: Framer Motion, GSAP, Lottie, CSS transitions
- **Real-time**: WebSocket, Socket.io, Firebase Realtime, Supabase Realtime, Pusher

**Output**: `_recon/STACK.md` with full dependency mapping

---

### PHASE 1: Deep Recon (Derin Keşif)
Uses ALL 3 Browser MCPs in parallel:

**Playwright MCP** — User interaction capture:
- Record all user flows: click → navigation → form fill → submit → response
- Capture cookie/localStorage/sessionStorage state changes
- Record console.log/warn/error outputs during interactions
- Take element-level screenshots (hover, focus, active, disabled states)
- Capture form validation behavior (required fields, patterns, error messages)
- Record scroll behavior (infinite scroll, lazy load, intersection observers)
- Capture WebSocket messages and real-time events

**Chrome DevTools MCP** — Deep code analysis:
- Extract full JavaScript bundle (beautified) via coverage tool
- Map all event listeners per element (click, input, scroll, mouseenter, etc.)
- Extract network waterfalls with timing, headers, payloads
- Identify all API endpoints (REST paths, GraphQL queries, tRPC procedures)
- Map CSS-in-JS runtime styles
- Extract source maps if available
- Document all mutation observers and ResizeObservers
- Capture console errors and unhandled promise rejections

**Puppeteer MCP** — Integration audit:
- Detect all third-party embeds (YouTube, Twitter, Instagram, TikTok, Spotify)
- Identify analytics scripts (GA4, GTM, Mixpanel, Amplitude, Hotjar, FullStory)
- Detect ad networks, cookie consent banners, popups
- Map all iframe embeds and their origins
- Identify payment providers (Stripe, PayPal, LemonSqueezy, Paddle)
- Detect chatbot widgets (Intercom, Crisp, Tidio, Drift)
- Identify A/B testing tools (Optimizely, VWO, LaunchDarkly)
- Map all service workers, workbox configs

**Output**: `_recon/RECON.md` (comprehensive), `_recon/APIS.md` (endpoints), `_recon/EMBEDS.md` (third-party), `_recon/BUNDLE.md` (JS analysis)

---

### PHASE 2: Behavior Map (Davranış Haritası)
Generate a complete interaction → outcome map:

```
User Action               → Trigger            → Network Call           → State Change        → UI Update
──────────────────────────────────────────────────────────────────────────────────────────────────────────
Click "Login"             → onClick            → POST /api/auth/login   → auth.token=xyz      → Redirect /dashboard
Type in search            → onInput (debounce) → GET /api/search?q=     → searchResults=[...] → Results dropdown
Scroll to bottom          → IntersectionObserver→ GET /api/posts?page=2 → posts.concat([...]) → New cards appear
Hover product card        → onMouseEnter       → (none)                → hoveredId=123       → Scale + shadow
Submit contact form       → onSubmit           → POST /api/contact     → formSubmitted=true  → Success toast
WebSocket message         → socket.on('chat')  → wss://example.com/ws  → messages.push({})   → Chat bubble
```

**Output**: `_recon/BEHAVIOR.md` — complete state machine of the app

---

### PHASE 3: Extension & Integration Map (Eklenti Haritası)
Catalog ALL embedded services and decide replacement strategy:

| Third-party | Detect | Replace Strategy |
|-------------|--------|-----------------|
| GA4 / GTM | Head script, dataLayer | Self-hosted Plausible / Umami |
| Intercom / Crisp / Tidio | Chat widget script | Self-hosted Chatwoot |
| Stripe / PayPal / Paddle | Checkout script, iframe | Stripe dev mode / LemonSqueezy test |
| YouTube / Vimeo embed | iframe, lite-youtube | lite-youtube-embed component |
| Google Maps | Maps script, iframe | MapLibre / Leaflet with OSM |
| Social embeds (X/Twitter/IG) | iframe, embed script | Static embed fallback |
| reCAPTCHA / hCaptcha | Script, widget | hCaptcha dev key / placeholder |
| Firebase / Supabase | SDK import, env vars | Firebase test project / Supabase local |
| Auth0 / Clerk / OAuth | SDK, redirect URIs | Clerk dev mode / NextAuth.js |
| Sentry / Datadog / LogRocket | Script, DSN | No-op / self-hosted GlitchTip |
| Cookie consent (Cookiebot) | Banner script | Local cookie consent component |
| OneSignal / Push | Service worker | Self-hosted web push |
| Algolia / Meilisearch | Search widget, API key | Meilisearch local / static search |
| Disqus / Commento | Embed script | Self-hosted Giscus / Cusdis |
| Mapbox / Google Maps | Map script, token | MapLibre + OpenFreeMap |

**Output**: `_recon/INTEGRATIONS.md` with replacement configs for each

---

### PHASE 4: Foundation + Backend (Temel + API Katmanı)
Generate full project scaffold with backend:

```
<output-dir>/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── api/                # Recreated API routes
│   │   │   ├── auth/
│   │   │   ├── search/
│   │   │   ├── contact/
│   │   │   └── [...paths]/
│   │   └── (routes)/
│   ├── components/
│   │   ├── ui/                 # shadcn components
│   │   ├── sections/           # Page sections
│   │   ├── widgets/            # Third-party replacement widgets
│   │   └── functional/         # Interactive behavior components
│   ├── lib/
│   │   ├── api-client.ts       # API client matching original
│   │   ├── state.ts            # State management (zustand/jotai)
│   │   ├── auth.ts             # Auth flow recreation
│   │   ├── analytics.ts        # Analytics proxy layer
│   │   ├── websocket.ts        # WebSocket client
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── use-debounce.ts
│   │   ├── use-intersection.ts
│   │   ├── use-websocket.ts
│   │   └── [...behavior hooks]
│   ├── store/                  # Zustand stores matching app state
│   └── types/                  # Full TypeScript types
├── prisma/                     # Optional: schema recreation
│   └── schema.prisma
├── public/
│   ├── fonts/
│   ├── images/
│   └── sw.js                   # Service worker recreation
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

Backend decision:
- **Static clone**: All API responses mocked with MSW (Mock Service Worker)
- **Proxy clone**: `next.config.ts` rewrites to original API (CORS-safe)
- **Full clone**: Recreate API endpoints in Next.js API routes with local DB
- **Hybrid**: Core APIs recreated, third-party APIs proxied

---

### PHASE 5: Behavior Replication (Davranış Klonlama)
Per BEHAVIOR.md, recreate EVERY interaction:

**Interactive Elements:**
- Click handlers → `onClick` with exact same behavior
- Form validation → Same rules, patterns, error messages, submit flow
- Search → Debounced input → API call → results render (same UI + timing)
- Infinite scroll → IntersectionObserver → pagination → append
- Dropdowns / Selects → Same open/close/select behavior
- Modals / Dialogs → Same open trigger, close behavior, backdrop, animation
- Tabs / Accordions → Same active state, transition, URL hash sync
- Drag & drop → Same DnD behavior with dnd-kit
- Sliders / Carousels → Autoplay, navigation, swipe, infinite loop

**State Management:**
- Recreate all Zustand stores matching original state shape
- Implement all state transitions exactly as original
- Sync state with URL params (if original does)
- Implement optimistic updates (if original does)

**Animations:**
- Match all CSS transitions (duration, easing, delay, stagger)
- Recreate all Framer Motion / GSAP animations
- Implement scroll-triggered animations (AOS, IntersectionObserver)
- Match hover, focus, active transitions exactly
- Recreate loading skeletons and shimmer effects

**Real-time (if applicable):**
- WebSocket client matching original protocol
- Socket.io namespace/room replication
- Polling fallback for unsupported transports
- Reconnection logic matching original
- Message format and handling identical

**Output**: `_recon/BEHAVIOR_DONE.md` — verified behavior checklist

---

### PHASE 6: Integration Replacement (Entegrasyon İkame)
Replace all third-party services with functional equivalents:

```typescript
// Example: Analytics proxy
// Original: window.gtag('event', ...)
// Clone: Plausible proxy
export function trackEvent(name: string, props?: Record<string, string>) {
  if (process.env.NEXT_PUBLIC_ANALYTICS === 'plausible') {
    plausible(name, { props })
  }
}

// Example: Auth flow
// Original: Clerk <SignIn /> + useUser()
// Clone: NextAuth.js with same flow
export { useAuth } from '@/lib/auth' // Same API surface

// Example: Chat widget
// Original: Intercom widget
// Clone: Chatwoot self-hosted widget (same UX)
```

Strategy per service:
- **Analytics**: Replace with Plausible/Umami (self-hosted)
- **Auth**: Replace with NextAuth.js / Clerk dev (same API)
- **Chat**: Replace with Chatwoot (same positioning, behavior)
- **Maps**: Replace with MapLibre + OSM tiles
- **Payments**: Stripe test mode / LemonSqueezy sandbox
- **Search**: Replace with Meilisearch local / Fuse.js static
- **Comments**: Replace with Giscus (GitHub Discussions)
- **Notifications**: Replace with local toast + email
- **Cookie consent**: Build local component (same UX)
- **Social embeds**: Static fallback with link (same visual size)
- **Realtime**: Replace with Socket.io self-hosted / Supabase Realtime
- **CDN images**: Next.js Image optimization (same URLs proxied)

---

### PHASE 7: Assembly + Full Build (Montaj + Derleme)
- Merge all section components, functional components, widget replacements
- Wire up API routes, state stores, auth flow, real-time connections
- Configure `next.config.ts` with rewrites/proxies for external APIs
- Create `.env.local` with all dev keys
- Install all dependencies
- Run `npm run build` and FIX EVERY ERROR until clean build
- Fix TypeScript errors, lint errors, type mismatches
- Optimize bundle with code splitting, lazy loading
- Implement proper error boundaries (matching original behavior)

**Build must pass** — zero tolerance for build errors.

---

### PHASE 8: Full Functional QA (Tam Fonksiyonel Doğrulama)
Automated verification using Playwright MCP:

**Visual:**
- [ ] Full-page screenshot comparison (original vs clone) — 95%+ match
- [ ] Responsive: 375px, 768px, 1440px, 1920px
- [ ] Dark/light mode (if original supports)
- [ ] Font rendering match
- [ ] Spacing/padding exact match
- [ ] Color values exact match

**Functional:**
- [ ] All click handlers produce same UI outcome
- [ ] All form submissions work (mocked or real)
- [ ] Search returns results with same UI
- [ ] Infinite scroll loads next page
- [ ] All modals open/close correctly
- [ ] All dropdowns work
- [ ] All accordions expand/collapse
- [ ] All tabs switch correctly
- [ ] All sliders/carousels navigate
- [ ] All hover states match original
- [ ] All focus states match original
- [ ] All disabled states match original
- [ ] All error states match original

**Network:**
- [ ] No CORS errors in console
- [ ] All API calls return expected format
- [ ] WebSocket connects and receives messages
- [ ] Service worker registered (if original has one)
- [ ] No 404s for assets

**Performance:**
- [ ] Lighthouse score 85+ across all categories
- [ ] Bundle size within 20% of original
- [ ] First Contentful Paint < 2s
- [ ] No render-blocking resources
- [ ] Images properly optimized

**Accessibility:**
- [ ] aXe audit passes (zero violations)
- [ ] Keyboard navigation works
- [ ] Focus order is logical
- [ ] Screen reader announces all dynamic changes
- [ ] Color contrast meets WCAG AA

**Integration Check:**
- [ ] Analytics fires correctly
- [ ] Auth flow complete (login/logout/register)
- [ ] Chat widget opens/closes
- [ ] Maps render correctly
- [ ] Social embeds display
- [ ] Payment flow functional (test mode)
- [ ] Cookie consent works

---

## Browser MCP Selection

| MCP | Primary Use | Secondary Use |
|-----|-------------|---------------|
| **Playwright** | User flow recording, screenshots, QA automation | Multi-page crawling, form filling |
| **Chrome DevTools** | JS bundle analysis, network waterfalls, CSS extraction | Performance traces, coverage analysis |
| **Puppeteer** | Third-party audit, service worker detection, PDF | aXe accessibility, iframe inspection |

Default: **Playwright** (most complete). For full functional clone, all 3 run in parallel.

---

## Backend Clone Modes

| Mode | Flag | What Happens |
|------|------|-------------|
| **Static** | `--static` | All APIs mocked with MSW. No backend needed. Fastest. |
| **Proxy** | `--proxy` | Original APIs proxied via Next.js rewrites. Works if original still up. |
| **Live** | `--live` | **Full live data mirror** — API proxy + data crawl + WS proxy + cron sync. Clone = canlı kopya. |
| **Full** | `--full` | Recreate all API endpoints + local DB (SQLite/Prisma). Most complete. |
| **Hybrid** | (default) | Core APIs recreated, third-party APIs proxied. Best balance. |

---

---

## LIVE DATA MODE (`--live`) — Canlı Veri Klonlama

Full functional clone + **gerçek, canlı veri** — mock değil, orijinal siteyle aynı verileri gösterir.

### Nasıl Çalışır

```
Kullanıcı → Clone Site → [API Proxy Katmanı] → Orijinal API → Gerçek Veri
                          ↓
                    [Local Cache] + [Seed DB] → Sayfa yenilemede hızlı yükleme
```

### Phase X1: Data Crawl & Seed (Veri Çekme)
Playwright ile orijinal siteyi tara, tüm veriyi çek:

| Veri Türü | Nasıl Çekilir | Nereye Kaydedilir |
|-----------|--------------|------------------|
| **Sayfa içerikleri** | DOM extraction, SSR HTML capture | `prisma/seed.ts` → SQLite |
| **API yanıtları** | Network interception, cache all GET responses | `_recon/api-cache/` + MSW handlers |
| **Kullanıcı listesi** | Admin panel crawl (if accessible) | `prisma/seed.ts` (anonymized) |
| **Ürün/envanter** | E-ticaret sayfalarını crawl | `prisma/seed.ts` |
| **Blog/makaleler** | Sitemap.xml → tüm URL'leri crawl | MDX files + `prisma/seed.ts` |
| **Medya dosyaları** | img/srcset, video/src, PDF links | `public/_mirror/` (proxied CDN) |
| **Dosya upload'ları** | Form data intercept | `public/_uploads/` |
| **Search index** | Algolia/Meilisearch API dump | Meilisearch local dump |
| **Auth users** | Test hesabı oluştur + session capture | `.env.local` test credentials |

### Phase X2: Live API Proxy (Canlı API Köprüsü)
next.config.ts ile otomatik proxy — **tek satır kod yazmadan**:

```typescript
// next.config.ts — auto-generated LIVE proxy config
const nextConfig = {
  async rewrites() {
    return [
      // Auto-detected from Recon Phase 1 network log:
      { source: "/api/:path*", destination: "https://original.com/api/:path*" },
      { source: "/graphql", destination: "https://original.com/graphql" },
      { source: "/_next/:path*", destination: "https://original.com/_next/:path*" },
      { source: "/uploads/:path*", destination: "https://original.com/uploads/:path*" },
      // WebSocket proxy via custom server
    ]
  },
  // Image proxy for external CDN
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "original.com" },
      { protocol: "https", hostname: "*.original-cdn.com" },
    ]
  }
}
```

### Phase X3: Data Layer Replication
| Scenario | Live Mode Strategy |
|----------|-------------------|
| **SSR sayfalar** | Next.js server fetch → original API + cache to SQLite |
| **ISR (Incremental Static Regeneration)** | `revalidate: 60` → background sync |
| **Search results** | Meilisearch sync cron job (same schema) |
| **User-specific data** | Auth token forwarding — clone kendi auth'u ile proxy |
| **File uploads** | Multi-part form proxy + local copy |
| **Analytics events** | Dual-send: clone + original (stealth mode) |
| **Realtime (WebSocket)** | Socket.io proxy server — mesajları aynen aktar |

### Phase X4: Auth & Session Mirror
- Auth isteği gelince → clone kendi NextAuth.js'ini kontrol et
- Token varsa → proxied API'ye token'ı forward et
- Token yoksa → login sayfasını göster (clone'un kendi login'ini)
- Social login'ler (Google/GitHub) — clone'un kendi OAuth app'i ile
- Session state: localStorage/sessionStorage → Zustand store'a eşle

### Phase X5: Real-time Sync
```typescript
// Auto-generated WebSocket proxy
// Original: wss://original.com/ws
// Clone: wss://clone.vercel.app/ws → proxy → wss://original.com/ws
//
// If original goes down, clone uses:
// 1. Last known state from cache
// 2. SSE polling fallback
// 3. Static snapshot
```

### Phase X6: Background Sync Jobs
```yaml
# vercel.json cron jobs (auto-generated)
crons:
  - path: /api/cron/sync-content
    schedule: "0 */6 * * *"   # every 6 hours
  - path: /api/cron/sync-search
    schedule: "0 */12 * * *"  # every 12 hours
  - path: /api/cron/sync-assets
    schedule: "0 0 * * *"     # daily
```

### Limitations (Canlı Veri ile):
| Durum | Çalışır mı? |
|-------|------------|
| Orijinal site ayakta, API'ler açık | ✅ **Tam — birebir canlı veri** |
| Orijinal site kapalı, cache var | ✅ Yarı — cache'teki son veriyle |
| Orijinal site kapalı, cache yok | ❌ Çalışmaz — seed data gerek |
| Auth gerektiren sayfalar (login) | ✅ Test hesabı + token forward |
| Orijinal her sayfayı değiştirir | ✅ Cron sync güncel tutar |
| WebSocket gerçek zamanlı | ✅ Proxy üzerinden aktarılır |
| Stripe ödeme işleme | ✅ Test mode'da çalışır |
| 3rd-party API key gerekiyor | ✅ .env.local'e otomatik yazılır |

### Use Case Matrix
| Ne istiyorsun? | Kullan |
|----------------|--------|
| "Görsel olarak aynı dursun, veri önemli değil" | `--static` |
| "API'leri canlı çalışsın, backend yazma" | `--proxy` |
| **"Eklentileri, özellikleri, verisiyle birebir aynı olsun"** | **`--live`** |
| "Backend'i de sıfırdan yaz, bağımsız olsun" | `--full` |
| "Hızlı clone, sonra karar veririm" | (default - hybrid) |

---

## GAME SECTION CLONE (`--game`) — Oyun Bölümü Klonlama

Herhangi bir oyunun belirli bir bölümünün görsel + işleyişini klonla. Web tabanlı oyunlar (Canvas/WebGL/HTML5) için tam destek, standalone oyunlar (UE5/Unity) için görsel + davranış replikasyonu.

### Supported Game Types

| Tip | Yakalama Yöntemi | Klon Çıktısı |
|-----|-----------------|--------------|
| **Web oyunu** (Phaser, Pixi.js, Three.js, Babylon.js, PlayCanvas) | Playwright + Chrome DevTools (Canvas/WebGL capture) | Next.js + Pixi.js/Three.js |
| **HTML5 oyunu** (Construct, GameMaker HTML5) | DOM + Canvas state capture | HTML5 Canvas + aynı mantık |
| **iframe gömülü oyun** (CrazyGames, itch.io) | iframe içine bağlan, full capture | Kendi sunucunda çalışan versiyon |
| **UE5/Unity standalone** (exe) | Screen capture + frame analizi + asset ripping | WebGL port veya video simülasyon |
| **Roblox/Fortnite Creative** | Screen recording + UI capture | Replica build instructions |

### Kullanım
```
clone https://example.com/game --game          # web oyunu bölüm klonla
clone path/to/game.exe --game --standalone     # standalone oyun
clone https://example.com --game --section "level-3"  # belirli bölüm
```

### Phase G1: Game Stack Detection (Oyun Motoru Tespiti)
- **Render engine**: Canvas 2D, WebGL, WebGL2, WebGPU, Three.js, Babylon, Pixi, Phaser, Unity WebGL
- **Physics**: Matter.js, Cannon.js, Ammo.js, Rapier, Havok, Box2D
- **Audio**: WebAudio, Howler.js, FMOD, Wwise
- **Input**: Mouse, keyboard, touch, gamepad (WebGamepad API)
- **Networking**: Socket.io, Colyseus, PeerJS, WebRTC, Nakama
- **State management**: ECS architecture, Redux, custom GameState
- **Asset format**: Spritesheet, glTF, FBX, atlas, audio sprites

### Phase G2: Visual Capture (Görsel Yakalama)
**3 Browser MCP paralel çalışır:**

**Playwright MCP** — Game interaction capture:
- Canvas frame-by-frame screenshot (her 100ms'de bir, 10sn boyunca)
- Record user input sequence (click coordinates, key presses, drag patterns)
- Capture all canvas states (before/after interaction)
- Record animation frame timing and FPS
- Identify interactive regions (hotspots, clickable areas)
- Record UI overlay positions (HUD, menus, buttons, health bars, score)

**Chrome DevTools MCP** — Deep game analysis:
- Capture WebGL calls and shader programs
- Extract all textures, sprites, and rendered assets from GPU memory
- Capture audio buffers and sound files
- Profile draw calls, render passes, and batch counts
- Inspect game state object (window.__game, window.__phaser, etc.)
- Extract animation timelines and tween definitions
- Capture scene graph and object hierarchy

**Puppeteer MCP** — Asset audit:
- List all loaded assets (images, audio, fonts, models, JSON configs)
- Capture network-loaded asset URLs and cache them
- Detect DRM/protection layers
- Map asset size and format (PNG, WebP, MP3, glTF, FBX, atlas)
- Identify CDN/origin for each asset

### Phase G3: Section Isolation (Bölüm İzolasyonu)
Belirli bir bölümü (level, menu, mini-game, UI ekranı) izole et:
- Scene/state transition tracking (oyun hangi state'e geçiyor?)
- Asset dependency mapping (hangi asset'ler bu bölümde kullanılıyor?)
- Code path analysis (hangi JS fonksiyonları bu bölümü yönetiyor?)
- Input binding map (hangi tuşlar/tıklamalar bu bölümü kontrol ediyor?)

### Phase G4: Logic Replication (Mantık Klonlama)
- Recreate game loop (requestAnimationFrame, update/render cycle)
- Implement same physics behavior (gravity, collision, forces) — matching engine
- Recreate input handling (keyboard, mouse, touch, gamepad)
- Match game state machine (menu → play → pause → gameover → score)
- Implement same scoring, health, timer, progression logic
- Recreate particle systems, visual effects, post-processing
- Match audio triggers and sound cues

**Engine-specific recreation:**
| Original | Clone output |
|----------|-------------|
| Phaser 3 | Phaser 3 + same config |
| Pixi.js | Pixi.js + same display tree |
| Three.js | Three.js + same scene |
| HTML5 Canvas | Raw Canvas 2D + same draw calls |
| Unity WebGL | Three.js reimplementation veya iframe embed |
| Construct/GameMaker | Raw HTML5 Canvas + recreated logic |

### Phase G5: Asset Extraction & Replacement (Varlık Çıkarma)
- Download all sprites, textures, audio files from cache/network
- Reconstruct spritesheets from GPU frame captures (if individual files unavailable)
- Extract fonts (WOFF2) and use same font-face
- Create missing assets via AI upscaling/generation (if protected)
- Optimize all assets (compress PNG, convert audio to WebM/MP3)
- Package into `public/assets/` with original folder structure

### Phase G6: UI/HUD Replication (Arayüz Klonlama)
- Match all in-game UI (health bar, score, minimap, inventory, dialog boxes)
- Recreate all menu screens (main menu, settings, pause, inventory)
- Match button styles, font sizes, color palette, animation easing
- Implement same hover/click/disabled states
- Match responsive layout (if game supports multiple resolutions)

### Phase G7: Assembly + Build (Montaj)
```
<output-dir>/
├── src/
│   ├── game/
│   │   ├── engine/         # Game engine recreation (Phaser/Pixi/Three)
│   │   ├── scenes/         # Game scenes (menu, level, gameover)
│   │   ├── entities/       # Game objects, sprites, characters
│   │   ├── systems/        # Physics, input, audio, particle systems
│   │   ├── ui/             # HUD, menus, overlays
│   │   └── config.ts       # Game config matching original
│   ├── app/
│   │   └── page.tsx        # Next.js wrapper with canvas mount
│   └── components/
│       └── GameCanvas.tsx  # Canvas component
├── public/
│   └── assets/             # Extracted game assets
├── next.config.ts
└── package.json
```

### Phase G8: Game QA (Oyun Doğrulama)
- [ ] Canvas renders exactly like original (frame comparison)
- [ ] All interactive regions respond to clicks/touch
- [ ] Game loop runs at same FPS
- [ ] Physics behavior matches (gravity speed, collision response)
- [ ] Audio plays at correct times
- [ ] UI elements positioned correctly over canvas
- [ ] Score/progression logic matches
- [ ] Input handling works (keyboard WASD, mouse click, touch)
- [ ] Scene transitions match (menu→play, play→pause, play→gameover)
- [ ] Performance: 60fps on target device

### Limitations (Oyun Klonlama):
| Durum | Çalışır mı? |
|-------|------------|
| Web tabanlı oyun (Canvas/WebGL) | ✅ Tam klon |
| iframe gömülü oyun | ✅ Tam — iframe içine bağlanır |
| WebGL shader efektleri | ✅ Shader code extraction + recreation |
| Oyun içi satın alma (IAP) | ❌ Ödeme sistemi klonlanamaz |
| Multiplayer/server-side logic | ❌ Sadece local/single-player klon |
| DRM korumalı asset'ler | ⚠️ AI ile yeniden üretilir (birebir değil) |
| UE5/Unity standalone exe | ⚠️ Screen capture bazlı, sınırlı interaktivite |
| Online/real-time multiplayer | ❌ Sadece görsel + local logic |

---

## Quality Gate
Before declaring done:
1. `npm run build` — MUST pass (zero errors)
2. `npm run lint` — MUST pass (zero warnings)
3. Playwright e2e test — ALL assertions pass
4. Visual diff — 95%+ match at all breakpoints
5. Console — zero errors/warnings during interaction test

---

## Skill Reference
Uses `~/.claude/skills/ai-website-cloner-template-master/SKILL.md` for execution logic.
