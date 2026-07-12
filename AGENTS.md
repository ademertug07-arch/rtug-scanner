# AGENTS.md — UW5 Singularity Engine v5 Hızlı Referans

> **UW5 v5** aktif — Ana kaynak: `.opencode/uw5/UW5_CORE.md` (kalıcı anayasa).
> Global AGENTS.md (`~/.config/opencode/AGENTS.md`) routing referansıdır.
> **UW5 = AI Operating System + AI Company Structure + Multi-Agent Society + Self-Evolving Organization.**
> **UW5 = AI Operating System + AI Company Structure + Multi-Agent Society + Self-Evolving Organization.**
> Her mesaj **21 katmanlı pipeline**'dan geçer: L00 Master Hub (Intent/Route/Path/Guard) → L01 Context Guard → L02 Task Planner → L03 KAIROS Recall + Semantic Search → L04 Workspace Knowledge Graph → L05 Capability Matrix → L06 Cost Optimizer (weighted) → L07 Model Router → L08 Skill Auto-Load → L08B Skill Generator (non-blocking) → L09 Tool Registry → L10 Plugin Manager → L11 Prompt Compiler → L12 Multi-Agent Orchestrator (META-MIND 8 motor) → L13 Execution Engine → L14 Sandbox (izole) → L15 Verifier + Policy Engine → L16 Self-Healing Loop → L17 Learning Engine → L18 Trace Capture (dual-mode) → L19 Golden State + Rollback.
> **🏛️ 18 AI CIVILIZATION LAYER**: 1.Human Control → 2.AI Kernel → 3.Memory/Evolution → 4.Governance → 5.Self-Aware Monitor → 6.Executive Council → 7.Multi-Agent Society → 8.Communication Fabric → 9.Autonomous Work → 10.Observability → 11.R&D Lab → 12.Business Engine → 13.Deployment System → 14.Self-Optimization → 15.Artifact Civilization → 16.SDK Universe → 17.External Connectors → 18.Infrastructure.
> **🟢 INIT-SESSION**: Her oturumda config doğrulama + crash kurtarma + golden state yükleme otomatik.
> **🟡 GOLDEN STATE**: Her görev sonrası state back-up, son 10 korunur.
> **🔄 SELF-HEALING**: Hata durumunda 3 kez patch → retry → verify, başarısız çözüm KAIROS'a kaydedilir.
> **🔵 CONTEXT GUARD**: 10+ turda 15K+ token → sessiz compact.
> **⚡ FAST LANE** (Route 1/3/6) vs **🔵 FULL PATH** (Route 2/4/5/7/8).
> **🧠 META-MIND 8 MOTOR**: Utility Command / Vibe Methodology / Agent Subtype / Reflection Engine / Direct Engine / Ultrawork Loop / Oracle Triad / Hyperplan / Parallel Agents / Sequential Chain.
> **🏛️ EXECUTIVE COUNCIL**: CEO (Strateji) / CTO (Mimari) / CFO (Maliyet) / COO (Operasyon) / CMO (Dokümantasyon) / CISO (Güvenlik).
> **📡 EVENT BUS**: 10 lifecycle event (on_session_start → on_shutdown).
> **🔄 EVOLUTION LOOP**: Goal → Kernel → Organize → Build → Deploy → Measure → Evolve.

## Ana Komutlar
| Komut | Ne Yapar |
|---|---|
| `/uw5 <task>` | **UW5 v5 KERNEL BOOT — Capability OS Runtime**. Her /uw5 çağrısı: 1.BOOT Kernel (Intent+Capability Resolver) → 2.SCAN Environment (Skills/MCP/LSP/Plugins/Agents/Models/Tools) → 3.ANALYZE Intent (Domain+Complexity+Files+Dependencies) → 4.RESOLVE Capabilities (Sadece gereken skill/MCP/LSP/agent/model/tool'u seç) → 5.BUILD Dynamic Pipeline (Göreve göre L00-L19'den sadece gerekli katmanları seç) → 6.EXECUTE → 7.VALIDATE (Self-heal×3+Policy) → 8.SAVE Memory (KAIROS+Golden) → 9.RELEASE Resources (Boşalt+kes+temizle) → 10.RETURN Result. **Yükleme politikası**: Her şeyi her zaman yükleme, sadece ihtiyaç duyulanı yükle, iş bitince serbest bırak. **18 LAYER**: 1.Human→2.AI Kernel→3.Memory→4.Govern→5.Self→6.Council→7.Agents→8.Comm→9.Work→10.Observe→11.R&D→12.Business→13.Deploy→14.Optimize→15.Artifact→16.SDK→17.External→18.Infra. **21 KATMAN**: L00→...→L19. **2 PATH**: ⚡Fast(1/3/6) | 🔵Full(2/4/5/7/8). **EVOLUTION**: Goal→Kernel→Organize→Build→Deploy→Measure→Evolve. |
| `/uw5flash <task>` | UW5 Flash — Groq Llama 3.3 70B (320 tok/s) |
| `/uw5deep <task>` | UW5 Deep — OpenRouter GPT-4o — frontier seviye |
| `/uw5local <task>` | UW5 Local — Ollama Qwen 2.5 Coder |
| `/uw5offline <task>` | UW5 Offline — Ollama Llama 3.2 3B |
| `/uw5ultra <task>` | UW5 Ultra — Claude Sonnet 4.6 (max zeka) |
| `/uw5 swarm <task>` | Multi-Agent Swarm — paralel task dağıt |
| `/uw5 ooda <task>` | OODA Loop — Observe→Orient→Decide→Act |
| `/uw5 test` | Test Pipeline — lint + typecheck + test |
| `/uw5 quality` | Quality Gates — güvenlik/perf/edge-case |
| `/uw5 doctor` | Diagnostics — sistem sağlık raporu |
| `/uw5 health` | Health check — API/model/tool/context durumu |
| `/uw5 memory` | Session geçmişi + bellek dump |
| `/uw5 compact` | Context window sıkıştır |
| `/uw5 dream` | KAIROS Dream — hafıza konsolidasyonu |
| `/uw5 evolve` | Self-Evolution — öğrenme + skill geliştirme |
| `/uw5 index` | Project Indexer — repo/dependency/symbol scan |
| `/uw5 graph` | Dependency/Call/Import graph görselleştir |
| `/uw5 cache` | Cache temizleme |
| `/uw5 audit` | Tam sistem denetimi |
| `/uw5 cost` | Token ve maliyet raporu |
| `/uw5 backup` | Golden state + snapshot yedekle |
| `/uw5 restore` | Golden state'den geri yükle |
| `/uw5 clean` | Geçici dosyaları temizle |
| `/uw5 knowledge add <cat> <konu> <içerik>` | Knowledge Base'e ekle |
| `/uw5 knowledge search <sorgu>` | Knowledge Base'de ara |
| `/uw5 vault read <path>` | Obsidian vault oku |
| `/uw5 vault search <sorgu>` | Obsidian vault'ta ara |
| `/uw5 trace <task-id>` | Pipeline execution raporu — katman katman süre+token+model |
| `/uw5 approve-skill <name>` | _pending/ skill'i production'a al |
| `/uw5 lock-status` | Concurrency queue — aktif/kuyruktaki task'lar |
| `/uw5 rollback <golden\|snapshot>` | Açık rollback tipi seçimi |

## Kısayol Komutlar
| Komut | Ne Yapar |
|---|---|
| `/compact` | Context window temizle |
| `/review` | Kod inceleme |
| `/scan` | Güvenlik taraması |
| `/build` | Projeyi derle |
| `/sessions` | Session geçmişi |
| `/share` | Session linki paylaş |
| `/snap` | Snapshot al (sna-backup.ps1) |
| `/snap-list` | Snapshot'ları listele |
| `/snap-restore` | Son snapshot'ı geri yükle |
| `/snap-diagnose` | Sistem durumu kontrolü |
| `/pine-check` | Pine Script plot sayısı + 64-limit raporu |
| `/prod-audit` | Production-first kalite denetimi |
| `/continue` | Sessiz devam |

## AAA Rolleri
| Komut | Rol |
|---|---|
| `/architect` | Sistem mimarisi |
| `/gamedev` | Oyun direktörü |
| `/unreal` | UE5 framework |
| `/worldbuilder` | Lore + dünya |
| `/ai-npc` | NPC AI |
| `/combat` | Combat sistem |
| `/uiux` | UI/UX tasarım |
| `/debug` | Hata ayıklama |
| `/deploy` | CI/CD |
| `/perf` | Performans |
| `/qa` | Test/QE |
| `/aaa-studio` | TÜM roller paralel |

## NEXUS Domain Agent'lar
| Komut | Agent |
|---|---|
| Pine Script / TradingView → | pine-architect |
| AI/Backend/Agent → | ai-systems-architect |
| Web/Cinematic UI → | web-artifact-forge |
| iOS/Swift → | ios-swift-architect |
| Görsel/Video → | visual-pipeline-ops |
| Kod keşfi / ara / bul → | explore |
| Risk/Review → | plan-reviewer |
| Diğer → | universal-architect (varsayılan) |

## Reasoning Tiers
| Tier | Model | Ne Zaman |
|---|---|---|
| `flash` | `groq/llama-3.3-70b-versatile` | Basit task, hızlı arama, düzeltme |
| `balanced` | `openrouter/anthropic/claude-sonnet-4.6` | Normal işler, reasoning, refactor |
| `deep` | `openrouter/openai/gpt-4o` | Karmaşık analiz, strateji |
| `ultra` | `openrouter/anthropic/claude-sonnet-4.6` | Maksimum zeka, kritik kararlar |
| `local` | `ollama/qwen2.5-coder:7b` | Local, offline, ücretsiz |
| `offline` | `ollama/llama3.2:3b` | Tamamen offline |

## Araçlar & Konfigürasyon
| Araç | Yol |
|---|---|
| **OpenCode** | Bu session |
| **Config** | `~/.config/opencode/config/opencode.jsonc` |
| **Global AGENTS.md** | `~/.config/opencode/AGENTS.md` |
| **Scripts** | `~/.config/opencode/scripts/` (init-session, context-guard, golden-state, self-healing, diagnostics, project-indexer, event-bus, concurrency-guard, trace-capture, rollback-manager, skill-approver) |
| **Snapshot** | `.uw5-snapshots\` |
| **Golden State** | `~/.config/opencode/.golden-state/` |
| **Crash Recovery** | Otomatik (crash flag + golden state restore) |
| **Obsidian Vault** | `C:\Users\cagda\Obsidian Vault\` |
| **Knowledge Base** | `~/.claude/knowledge/` |
| **Projeler** | `C:\Users\cagda\Projects\` |
| **UW5 Kernel** | `.opencode/uw5/kernel/` — resolver, planner, router, executor |
| **UW5 Registry** | `.opencode/uw5/registry/` — skills.json, mcp.json, lsp.json, plugins.json, agents.json, models.json |
| **UW5 Pipeline** | `.opencode/uw5/pipeline/` — fast.json (route 1/3/6), full.json (route 2/4/5/7/8), deep.json (route 4/5) |
| **UW5 Memory** | `.opencode/uw5/memory/` — kairos.json (hata hafızası), golden.json (state backup) |
| **UW5 Config** | `.opencode/uw5/config/` — uw5.json (versiyon, politikalar, path'ler) |
