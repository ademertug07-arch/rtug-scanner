# UW5 Intent Router
## Görevi: Intent'i tespit et, doğru Route'a yönlendir.

### 8 Route

| # | Route | Path | Motor | Anahtar Kelimeler |
|---|-------|------|-------|-------------------|
| 1 | System State | ⚡Fast | Utility Command | backup, restore, snap, yedek, diagnose, health |
| 2 | Vibe Coding | 🔵Full | Vibe Methodology | vibe, yaz, oluştur, build, yap, kod, develop |
| 3 | Claude Ecosystem | ⚡Fast | Utility Command | skill, mcp, lsp, plugin, claude, ralph, awesome |
| 4 | Agent Types | 🔵Full | Agent Subtype | analyze, plan, think, email, ara, bul, kesif |
| 5 | Review/Scan | 🔵Full | Reflection Engine | review, scan, incele, check, kalite, audit |
| 6 | Utility | ⚡Fast | Utility Command | compact, share, sessions, history, export, trace |
| 7 | General | 🔵Full | Vibe Methodology | (fallback - hiçbiri eşleşmezse) |
| 8 | Executive Council | 🔵Full | Parallel Agents | strateji, vizyon, karar, mimari, roadmap |

### Intent Detection Sırası
1. Deterministic keyword match (yukarıdaki tablo)
2. Context analysis (önceki mesajlar)
3. Pattern recognition (önceki task pattern'ları)
4. Fallback → Route 7 General

### Route Seçim Sonrası
- Route 1/3/6 → ⚡Fast Lane: L00 → L07 → L09 → ... → L19 (L01-L06 atlanır)
- Route 2/4/5/7/8 → 🔵Full Path: L00 → L01 → ... → L19 (tüm katmanlar)
