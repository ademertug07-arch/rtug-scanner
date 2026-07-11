#!/usr/bin/env pwsh
<#
.SYNOPSIS
    RTUG Surround Scanner — GitHub'a yükleme scripti
.DESCRIPTION
    Bu script tüm RTUG scanner dosyalarını GitHub repo'suna push eder.
    Kullanım: .\setup_github.ps1 -RepoUrl "https://github.com/KULLANICI/rtug-scanner.git"
.EXAMPLE
    .\setup_github.ps1 -RepoUrl "https://github.com/cagdas/rtug-scanner.git"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl
)

$ErrorActionPreference = "Stop"
$PROJECT_DIR = Get-Location

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  RTUG SURROUND — GitHub Upload              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Git kontrol
$gitExists = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitExists) {
    Write-Host "[HATA] Git bulunamadi. Yükle: https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# 2. .gitignore kontrol
if (-not (Test-Path ".gitignore")) {
    Write-Host "[!] .gitignore bulunamadi, oluşturuluyor..." -ForegroundColor Yellow
    @"
__pycache__/
.env
.env.*
.surround_status.json
.restore-needed
logs/
*.log
.idea/
.vscode/
Thumbs.db
.DS_Store
opencode
NUL
obsidian/
imported/
"@ | Out-File -FilePath ".gitignore" -Encoding utf8
    Write-Host "[OK] .gitignore oluşturuldu" -ForegroundColor Green
}

# 3. Git init
if (-not (Test-Path ".git")) {
    Write-Host "[*] Git reposu başlatılıyor..." -ForegroundColor Yellow
    git init | Out-Null
    git branch -M main
    Write-Host "[OK] Git reposu başlatıldı" -ForegroundColor Green
} else {
    Write-Host "[*] Git reposu zaten var" -ForegroundColor Green
}

# 4. Dosyaları stage et
Write-Host "[*] Dosyalar ekleniyor..." -ForegroundColor Yellow

# Sadece RTUG ile ilgili dosyaları ekle (diğer projeleri karıştırma)
$rtugFiles = @(
    ".github/workflows/rtug-surround.yml",
    "rtug_surround_daemon.py",
    "rtug_scanner_core.py",
    "rtug_multi_symbol_scanner.py",
    "rtug_color_surround.pine",
    "rtug_breakout_alert.pine",
    "rtug_obv_combo.pine",
    "rtug_obv_merged.pine",
    "rtug_obv_neon.pine",
    "rtug_triple_obv.pine",
    "rtug_ultimate_scanner.pine",
    "rtug_symbols.py",
    "rtug_telegram_bot.py",
    "neon_obv_core.pine",
    "neon.pine",
    "SURROUND_7x7_SETUP.md",
    "RTUG_SETUP.md",
    "RTUG_CLOUD_SETUP.md",
    "setup_surround_daemon.ps1",
    "setup_github.ps1",
    "requirements.txt",
    ".gitignore"
)

foreach ($file in $rtugFiles) {
    if (Test-Path $file) {
        git add $file 2>$null
        Write-Host "  + $file" -ForegroundColor Gray
    }
}

# 5. Commit
Write-Host "[*] Commit yapılıyor..." -ForegroundColor Yellow
git commit -m "RTUG Color Surround Scanner - 7/24 Cloud Ready

- GitHub Actions workflow (30dk interval)
- Color surround pattern detection (8 pattern)
- Telegram notification daemon
- Multi-market support (BIST + US + Crypto)"
Write-Host "[OK] Commit yapildi" -ForegroundColor Green

# 6. Remote ekle
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    if ($existingRemote -ne $RepoUrl) {
        git remote set-url origin $RepoUrl
        Write-Host "[OK] Remote güncellendi: $RepoUrl" -ForegroundColor Green
    } else {
        Write-Host "[OK] Remote zaten ayarlı: $RepoUrl" -ForegroundColor Green
    }
} else {
    git remote add origin $RepoUrl
    Write-Host "[OK] Remote eklendi: $RepoUrl" -ForegroundColor Green
}

# 7. Push
Write-Host ""
Write-Host "[*] GitHub'a push yapılıyor..." -ForegroundColor Yellow
Write-Host "[!] GitHub kullanıcı adı ve PAT (Personal Access Token) isteyecek" -ForegroundColor Cyan
Write-Host "[!] Şifre yerine PAT kullan: https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host ""

try {
    git push -u origin main
    Write-Host ""
    Write-Host "[OK] Push başarılı!" -ForegroundColor Green
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  SONRAKİ ADIMLAR:                            ║" -ForegroundColor Cyan
    Write-Host "║                                              ║" -ForegroundColor Cyan
    Write-Host "║  1. GitHub'da repo sayfasına git             ║" -ForegroundColor Cyan
    Write-Host "║  2. Settings → Secrets → Actions             ║" -ForegroundColor Cyan
    Write-Host "║  3. İki secret ekle:                         ║" -ForegroundColor Cyan
    Write-Host "║     TELEGRAM_BOT_TOKEN = 888284...           ║" -ForegroundColor Cyan
    Write-Host "║     TELEGRAM_CHAT_ID   = 6988108865          ║" -ForegroundColor Cyan
    Write-Host "║  4. Actions → RTUG Surround → çalışıyor mu? ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
}
catch {
    Write-Host ""
    Write-Host "[HATA] Push başarısız: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Olası nedenler:" -ForegroundColor Yellow
    Write-Host "  - GitHub reposu oluşturulmamış (https://github.com/new)" -ForegroundColor Yellow
    Write-Host "  - Geçersiz URL: $RepoUrl" -ForegroundColor Yellow
    Write-Host "  - PAT (token) geçersiz veya yetkisiz" -ForegroundColor Yellow
    Write-Host "  - İnternet bağlantısı yok" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manuel push dene:" -ForegroundColor Cyan
    Write-Host "  git remote add origin $RepoUrl" -ForegroundColor Cyan
    Write-Host "  git push -u origin main" -ForegroundColor Cyan
}
