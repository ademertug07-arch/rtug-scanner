# UW5 Visual Core — Cyber AI Core Theme

OpenCode görünümünü hackleme. UW5 kendi görsel işletim katmanına sahip olsun.

## Philosophy

"OpenCode üzerinde çalışan bağımsız AI Civilization Interface."

Bu katman OpenCode'un Electron/Chromium çekirdeğine dokunmaz. 
Tamamen yapılandırma dosyaları ve runtime script'leri ile çalışır.

## Update Protection

- OpenCode installation dosyalarına dokunulmaz
- `node_modules` veya binary dosyalar değişmez
- Tüm dosyalar `~/.opencode/uw5/visual/` altında saklanır
- Güncellemelerde silinmez — bağımsız manifest ile korunur

## File Structure

| File | Purpose |
|------|---------|
| `theme.json` | Cyber AI Core theme engine — layout, typography, animation |
| `colors.json` | Full color palette — bg, text, accent, semantic, status, HUD, pipeline |
| `hud.json` | HUD system — panels, pipeline visual, status displays |
| `overlay.json` | Boot screen, pipeline display, status bar, notifications |
| `README.md` | This file |

## Integration

Boot sırasında `uw5-boot.ps1` visual core'u yükler:

1. Visual config (theme, hud, overlay, colors) yüklenir
2. HUD sistemi başlatılır
3. Status tracking aktif edilir
4. Görsel durum `memory/visual-state.json`'a kaydedilir

## Color System

- **Primary**: Cyan — aksiyon, vurgu, aktif
- **Secondary**: Green — başarı, onay, hazır
- **Warning**: Yellow — uyarı, degrade
- **Error**: Red — hata, kritik
- **Background**: Deep black/dark blue — terminal hissi

## HUD Panels

| Panel | Source | Description |
|-------|--------|-------------|
| UW5 VERSION | static | v5.0 |
| ROUTE | runtime | Current route (1-8) |
| PIPELINE | runtime | fast/full/deep |
| LAYER | runtime | Active pipeline layer |
| AGENT | runtime | Active NEXUS agent |
| MODEL | runtime | flash/balanced/deep/ultra |
| MEMORY | runtime | KAIROS health status |
| EXEC TIME | runtime | Execution timer |
| TOKENS | runtime | Token counter |
| SELF HEAL | runtime | Self-healing status |
| OPTIMIZE | runtime | Learning engine status |

## Pipeline Visual

21 layer visual flow display:
- `●` Done / `▸` Active / `○` Pending / `✕` Failed
- Color-coded by status
- Arrow connector visualization
