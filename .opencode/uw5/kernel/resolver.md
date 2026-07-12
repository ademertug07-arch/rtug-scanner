# UW5 Capability Resolver
## Görevi: Kullanıcı isteğini analiz eder, gerekli kaynakları belirler.

### Analiz Çıktısı
- Domain: coding/trading/research/web/ai/devops/...
- Complexity: simple/medium/complex/critical
- Required Skills: hangi skill'ler yüklenecek
- Required MCP: hangi MCP sunucuları bağlanacak
- Required LSP: hangi LSP başlatılacak
- Required Plugins: hangi plugin'ler aktifleştirilecek
- Required Agent: hangi domain agent'ı seçilecek
- Required Model: flash/balanced/deep/ultra/local/offline
- Required Pipeline: hangi L00-L19 katmanları

### Örnekler

| Input | Domain | Skills | MCP | LSP | Agent | Model | Pipeline |
|-------|--------|--------|-----|-----|-------|-------|----------|
| TradingView düzelt | pine+trading | pine-architect | - | pine-lsp | pine-architect | flash | L00→L02→L08→L12→L13→L15→L18→L19 |
| Web sitesi yap | web | cinematic-web, gsap-motion, shadcn | browser-use | typescript | web-artifact-forge | balanced | L00→L02→L07→L08→L11→L12→L13→L14→L15→L18→L19 |
| Python API yaz | coding | python-backend | - | pyright | ai-systems-architect | balanced | L00→L02→L07→L08→L11→L12→L13→L18→L19 |
| Araştırma yap | research | yt-pipeline, notebooklm | brave-search | - | universal-orchestrator | flash | L00→L03→L05→L09→L18→L19 |
| Güvenlik tara | security | - | - | - | security-scanner | deep | L00→L02→L05→L11→L13→L15→L16→L18→L19 |
| iOS uygulama | ios | ios-swift-architect | - | swift | ios-swift-architect | balanced | L00→L02→L07→L08→L11→L12→L13→L14→L15→L18→L19 |
| Kritik karar | strategy | meta-mind | sequential-thinking | - | deep-thinker | ultra | L00→L01→L02→L03→L04→L05→L06→L07→L08→L09→L10→L11→L12→L13→L14→L15→L16→L17→L18→L19 |

### Domain → Skill Kısayolları

| Domain | Default Skill | Agent |
|--------|--------------|-------|
| pine/tradingview | pine-architect | pine-architect |
| web/frontend | cinematic-web + frontend-design | web-artifact-forge |
| ai/npc/backend | ai-systems-architect | ai-systems-architect |
| ios/swift | ios-swift-architect | ios-swift-architect |
| visual/comfy | visual-pipeline-ops | visual-pipeline-ops |
| research | yt-pipeline + notebooklm | universal-orchestrator |
| trading/bot | trading-bot + data-analysis | ai-systems-architect |
| azure/cloud | azure-prepare | universal-orchestrator |
| laravel/php | laravel-best-practices | universal-orchestrator |
| n8n/workflow | workflow-builder | universal-orchestrator |
| gamedev/ue5 | aaa-studio | universal-orchestrator |
| general | - | universal-orchestrator |

### Model Seçim Matrisi

| Complexity | Risk | Token | Model |
|-----------|------|-------|-------|
| simple | low | <500 | flash (Groq Llama 3.3 70B) |
| medium | low | 500-2K | balanced (Gemini 2.5 Flash) |
| complex | medium | 2K-5K | deep (GPT-4o) |
| critical | high | >5K | ultra (Claude Sonnet 4.6) |
| privacy | any | any | local (Qwen 2.5 7B) |
| offline | any | any | offline (Llama 3.2 3B) |
