# SNA Backup/Restore — Singularity Engine

## `/sna-backup`
Tüm SNA yapılandırmasını yedekler: CLAUDE.md, skills, custom commands, config, scripts, core DB.

```powershell
.\scripts\sna-backup.ps1                    # Normal yedek (config + skills + DB)
.\scripts\sna-backup.ps1 -Quick             # Sadece config (skills hariç)
.\scripts\sna-backup.ps1 -Full              # Her şey + cache
.\scripts\sna-backup.ps1 -Name "pre-update" # İsimli yedek
```

## `/sna-restore`
Son yedekten veya belirtilen yedekten geri yükler.

```powershell
.\scripts\sna-backup.ps1 -Restore           # Son yedekten geri yükle
.\scripts\sna-backup.ps1 -Restore -From "C:\Users\cagda\.opencode-backups\sna-full-20260627_154019"
```

## `/sna-list`
Tüm yedekleri listeler.

```powershell
.\scripts\sna-restore.ps1 -List         # Yedek listesi
```

## `/sna-diagnose`
Sistem durumunu kontrol eder.

```powershell
powershell -Command "& { . .\scripts\sna-backup.ps1; Get-SNADiagnostics }"
```

## Alınan Öğeler (6/6)
| # | Öğe | Açıklama |
|---|------|----------|
| 1 | Konfig dosyaları | opencode.jsonc, CLAUDE.md, AGENTS.md, boot scripts |
| 2 | OpenCode plugin'leri | .ts dosyaları |
| 3 | Script'ler | .ps1 dosyaları |
| 4 | Custom commands | .opencode/commands/*.md |
| 5 | Skill'ler | ~/.claude/skills/*/SKILL.md |
| 6 | Core DB | opencode.db, auth.json, mcp-auth.json |
| + | Ortam değişkenleri | Token durumu logu |
| + | Cache (isteğe bağlı) | Full cache backup |
