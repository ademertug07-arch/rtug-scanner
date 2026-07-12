# UW5 v5 CORE — AI Operating System Constitution

## AMAÇ
UW5 = OpenCode Native AI Orchestration Layer.
Statik prompt değildir. Kalıcı çalışan Core Runtime Profile'dir.
OpenCode kapansa, session değişse, bilgisayar yeniden başlasa — UW5 kaybolmaz.

---

## 1. AI CIVILIZATION — 18 Layer

```
01. Human Control Layer     → CLI, Web, Mobile, Voice, API
02. AI Kernel               → Reasoning, Planning, Decision, Goal, Tool, Context, Orchestrator
03. Memory & Evolution      → Short/Long/Episodic/Semantic/Artifact + KAIROS + Vector + KG
04. Governance & Control    → L15 Policy Engine, Compliance, Security, Erişim
05. Self-Aware Monitor      → L18 Trace Capture, Diagnostics, Anomaly Detector, Health
06. Executive Council       → AI CEO/CTO/CFO/COO/CMO/CISO
07. Multi-Agent Society     → Executive → Departments → Agents → Worker Pool
08. Communication Fabric    → Event Bus, Message Queue, Pub/Sub, RPC, Streaming, State Sync
09. Autonomous Work System  → Mission Planner → Task Queue → Scheduler → Workers → Aggregator
10. Observability           → Logs, Metrics, Distributed Tracing, Performance, Alerting
11. R&D Lab                 → Experiments, Prototypes, New Models, Algorithms
12. Business Engine         → Product Factory, Revenue Engine, Growth Engine
13. Autonomous Deployment   → Build → Test → Sandbox → Canary → Production → Rollback
14. Self-Optimization       → Speed AI, Accuracy AI, Cost AI
15. Artifact Civilization   → Code, Models, Docs, Apps, Agents, Plugins
16. SDK Universe            → Agent SDK, Plugin SDK, Tool SDK, Marketplace
17. External Connectors     → GitHub, Slack, Discord, Telegram, DB, Browser, REST, MCP, Webhook
18. Infrastructure          → Compute (Local/Cloud/GPU), Storage (PG/Redis/Vec)
```

---

## 2. CAPABILITY OS RUNTIME — 10 Adım

Her `/uw5 <task>` çağrısı:

```
1. BOOT KERNEL         → Intent Analyzer + Capability Resolver
2. SCAN ENVIRONMENT    → Skills, MCP, LSP, Plugins, Agents, Models, Tools
3. ANALYZE INTENT      → Domain, Complexity, Files, Dependencies
4. RESOLVE CAPABILITIES → Sadece ihtiyaç duyulan kaynakları seç
5. BUILD DYNAMIC PIPELINE → Göreve göre L00-L19 katmanlarını seç
6. EXECUTE TASK        → Pipeline'ı yürüt
7. VALIDATE            → Self-Healing (×3), Verifier, Policy
8. SAVE MEMORY         → KAIROS + Golden State
9. RELEASE RESOURCES   → Unload skill, Disconnect MCP, Stop LSP, Clear cache
10. RETURN RESULT
```

---

## 3. CAPABILITY RESOLVER — Karar Kuralları

### Domain → Kaynak Eşleme

Resolver 7 registry'yi tara:
- `registry/capabilities.json` — 15 domain tanımı
- `registry/skills.json` — 130+ skill, 12 kategori
- `registry/mcp.json` — 30+ server, domain load rules
- `registry/lsp.json` — 7 dil
- `registry/plugins.json` — 3 plugin
- `registry/agents.json` — 13 NEXUS + 6 Executive Council
- `registry/models.json` — 6 tier (flash→offline)

### Yükleme Politikası (DEĞİŞTİRİLEMEZ)
- KESİNLİKLE tüm skill/MCP/LSP/agent/model'i başlangıçta yükleme
- Sadece görevin ihtiyaç duyduğu kaynakları yükle
- İş bitince: unload skill, disconnect MCP, stop LSP, clear temporary context
- RAM tüketimini azaltır, çökme olasılığını düşürür

---

## 4. PIPELINE SİSTEMİ — 3 Path

| Pipeline | Route | Katman | Kullanım |
|----------|-------|--------|----------|
| FAST | 1/3/6 | L00→L07→...→L19 (L01-L06 atlanır) | Utility, system, basit sorgu |
| FULL | 2/4/5/7/8 | L00→L01→...→L19 (tümü) | Kod yazma, analiz, review, genel |
| DEEP | 4/5 | L00→L01→...→L19 (deep model override) | Güvenlik, derin analiz |

---

## 5. META-MIND — 8 Motor

| Sinyal | Seçilecek Motor |
|--------|----------------|
| Route 1/3/6 (deterministik) | Utility Command |
| Route 2/7 (kod üretimi) | Vibe Methodology |
| Route 4 (agent) | Agent Subtype |
| Route 5 (review) | Reflection Engine |
| Tek dosya, düşük risk | Direct Engine |
| Orta karmaşıklık | Ultrawork Loop |
| Yüksek belirsizlik | Oracle Triad |
| Kritik sistem / production | Reflection Engine |
| Planlama | Hyperplan Engine |
| Bağımsız paralel işler | Parallel Agents |
| Bağımlı zincir | Sequential Chain |

---

## 6. MEMORY & EVOLUTION — 3 Katman

### KAIROS (Hata Hafızası)
Her başarısızlık kaydedilir: error_signature, domain, solution_diff, success_rate.
Sonraki benzer hatalarda KAIROS taranır, önceki çözüm uygulanır.

### Golden State (State Backup)
Her başarılı task sonrası alınır. Son 10 korunur.
Crash durumunda otomatik restore edilir.

### Active Context (Session Memory)
Her task sonrası güncellenir. 24 saat geçmişse sıfırlanır.

---

## 7. SELF-HEALING — Hata Kurtarma

- Her hata için 3 otomatik deneme (patch → retry → verify)
- 3 deneme başarısız → fallback strateji uygula
- Tüm hatalar error_signature ile KAIROS'a kaydedilir
- Self-Healing başarısız olursa → Golden State restore

---

## 7b. IDENTITY ASSERTION — Sistem Kendini Tanıma (DEĞİŞTİRİLEMEZ)

Bu bölüm UW5'in kendi kimliğini tanımlar. Her boot'ta bu sayılar gerçek registry/pipeline dosyalarıyla karşılaştırılır.
Sapma tespit edilirse alarm verilir. Bu değerler UW5_BASELINE_v5_FINAL.json ile dondurulmuştur.

| Tanımlayıcı | Değer | Doğrulama Kaynağı |
|------------|-------|-------------------|
| Pipeline katman sayısı | 21 (L00-L19) | pipeline/full.json |
| Route sayısı | 8 (1-8) | pipeline/full.json.routes |
| Model tier sayısı | 6 (flash/balanced/deep/ultra/local/offline) | registry/models.json.tiers |
| Registry sayısı | 7 (skills/mcp/lsp/plugins/agents/models/capabilities) | registry/*.json |
| Resilience katmanı | 4 (Golden State/Snapshot/KAIROS/Git) | STATE_MANIFEST.backup_locations |
| RAG enrichment | Aktif (TF-IDF, 950+ doküman) | memory/vector-index/index.json |
| Self-Healing | L16 bağlı, 3 retry, KAIROS fallback | runtime/uw5-self-healing.ps1 |
| Baseline | UW5_BASELINE_v5_FINAL.json (dondurulmuş, salt-okunur) | UW5_BASELINE_v5_FINAL.json |
| Change Guard | Aktif (pre-change snapshot + yapısal küçülme reddi) | runtime/uw5-change-guard.ps1 |

**Doğrulama kuralı**: Identity Assertion'daki sayılar ile registry/pipeline dosyalarından okunan gerçek sayılar
eşleşmezse boot sırasında WARNING loglanır. Eğer bir sayı azalmışsa (yapısal küçülme), değişiklik otomatik reddedilir.

---

## 8. GOVERNANCE — Değiştirilemez Kurallar

1. **Güvenlik > Performans > Özellikler** — Production-first
2. **Her değişiklik /undo ile geri alınabilir olmalı**
3. **Bilmiyorsan söyle** — Uydurma, direkt "bilmiyorum" de
4. **Her şeyi her zaman yükleme** — On-demand loading
5. **Registry'ler tek kaynak** — capabilities.json ana karar kaynağıdır
6. **UW5 Core dosyası değiştirilmez** — Bu dosya UW5 anayasasıdır

---

## 9. DOSYA MİMARİSİ (Kalıcı)

```
.opencode/uw5/
├── UW5_CORE.md          ← ANAYASA (bu dosya)
├── config/
│   └── uw5.json         ← Versiyon, politikalar, path'ler
├── kernel/              ← Referans dokümantasyon
│   ├── resolver.md
│   ├── planner.md
│   ├── router.md
│   └── executor.md
├── registry/            ← 7 capability kaynağı
│   ├── capabilities.json
│   ├── skills.json
│   ├── mcp.json
│   ├── lsp.json
│   ├── plugins.json
│   ├── agents.json
│   └── models.json
├── pipeline/            ← Dinamik katman tanımları
│   ├── fast.json
│   ├── full.json
│   └── deep.json
├── runtime/             ← Çalışan kod
│   ├── uw5-bootstrap.ps1      ← OpenCode başlangıç kontrolü
│   ├── uw5-boot.ps1           ← Boot motoru
│   ├── uw5-resolver.ps1       ← Capability Resolver
│   ├── uw5-router.ps1         ← Pipeline seçici
│   ├── uw5-executor.ps1       ← Pipeline yürütücü
│   ├── uw5-memory.ps1         ← KAIROS + Golden kaydedici
│   ├── context-guard.ps1      ← Context takip
│   ├── health-monitor.ps1     ← Sistem takibi
│   └── decision-score.ps1     ← Seçim puanlama
├── memory/              ← Hafıza şemaları
│   ├── kairos.json
│   └── golden.json
└── recovery/            ← Çökme kurtarma
    ├── session-state.json
    ├── runtime-state.json
    └── last-task.json
```

---

## 10. ENTEGRASYON NOKTALARI

| Yükleme Noktası | Ne Yükler | Ne Zaman |
|----------------|-----------|----------|
| opencode.jsonc instructions | UW5_CORE.md | Her session başında |
| opencode.jsonc command.uw5 | Runtime boot tetikleme | /uw5 çağrısında |
| init-session.ps1 | uw5-bootstrap.ps1 | OpenCode her açılışında |
| AGENTS.md | UW5 routing yönlendirme | Her mesajda |

---

## 11. KURTARMA SÖZLERİ (Recovery Promises)

| Senaryo | Tepki |
|---------|-------|
| Crash / session kaybı | Auto-restore from Golden State (init-session step 7) |
| Dosya bozulması / checksum hatası | Auto-repair from pre-change snapshot → golden → git |
| Yapısal küçülme/bozulma girişimi | Otomatik reddedilir, baseline korunur, kullanıcı uyarılır |
| Self-Healing 3 retry başarısız | KAIROS kaydı + Golden State restore (L16) |
| /uw5 restore baseline | UW5_BASELINE_v5_FINAL.json locked state'e dönüş |
| Golden State rotasyonu kaybı | Snapshot layer 2 + Version History layer 4 bağımsız korur |
| 2 yedek aynı anda kaybı | Kalan 2 yedekten (snapshot veya git) onarım (4-layer resilience) |

---

*UW5 v5 — Persistent Core. AI Operating System. Immutable Constitution.*
