---
description: Launch or interact with Zed Editor (D:\Zed\Zed.exe). Use when opening files, navigating code, or launching the editor.
---

# Zed Editor Integration

Launch: `/uw5 zed`
Open file: `/uw5 zed file <path>` (relative to workspace or absolute)
Show tasks: `/uw5 zed tasks`

**Entegrasyon:**
- `/uw5 zed` → Zed başlatır, workspace açar
- `/uw5 zed file opencode.jsonc` → config dosyasını açar
- `/uw5 zed file CLAUDE.md` → master routing dosyasını açar

**Zed'den OpenCode:**
- `Ctrl+Shift+B` → OpenCode (bu workspace)
- `Ctrl+Shift+S` → Snapshot al
- `Ctrl+Shift+O` → Task spawn paneli

**LSP:** TypeScript, Python (pyright), Go, Rust — otomatik
**Terminal:** PowerShell (built-in)

**Config dosyaları:**
- Global: `%APPDATA%\Zed\settings.json`
- Global keymap: `%APPDATA%\Zed\keymap.json`  
- Workspace: `.zed/settings.json`
- Workspace tasks: `.zed/tasks.json`
