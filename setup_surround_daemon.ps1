<#
.SYNOPSIS
    RTUG Color Surround Daemon - Tek Tıkla Kurulum
.DESCRIPTION
    1. Pip bağımlılıklarını kontrol eder/yükler
    2. Telegram bağlantısını test eder
    3. Windows Task Scheduler görevi oluşturur (her açılışta çalışır)
    4. Daemon'u başlatır
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = (Get-Command python).Source
$DaemonScript = Join-Path $ScriptDir "rtug_surround_daemon.py"
$EnvFile = Join-Path $ScriptDir ".env"
$LogFile = Join-Path $ScriptDir "logs\setup_log.txt"

# Log dosyası
if (-not (Test-Path (Join-Path $ScriptDir "logs"))) {
    New-Item -ItemType Directory -Path (Join-Path $ScriptDir "logs") -Force | Out-Null
}

Start-Transcript -Path $LogFile -Append

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RTUG SURROUND DAEMON - KURULUM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ─── 1. Pip bağımlılıkları ──────────────────────────
Write-Host "[1/5] Pip bagimliliklari kontrol ediliyor..." -ForegroundColor Yellow

$packages = @("yfinance", "ccxt", "requests", "python-dotenv", "numpy", "pandas")
foreach ($pkg in $packages) {
    try {
        python -c "import $pkg" -ErrorAction Stop
        Write-Host "  [OK] $pkg" -ForegroundColor Green
    } catch {
        Write-Host "  [KURULUYOR] $pkg..." -ForegroundColor Yellow
        pip install $pkg -q
        Write-Host "  [OK] $pkg yuklendi" -ForegroundColor Green
    }
}

# ─── 2. .env dosyası ────────────────────────────────
Write-Host ""
Write-Host "[2/5] Telegram .env kontrol ediliyor..." -ForegroundColor Yellow

if (-not (Test-Path $EnvFile)) {
    Write-Host "  [HATA] .env dosyasi bulunamadi!" -ForegroundColor Red
    Write-Host "  Lutfen .env.rtug.example dosyasini .env olarak kopyalayin"
    Write-Host "  ve Telegram bot token'inizi girin."
    Write-Host ""
    Write-Host "  copy .env.rtug.example .env" -ForegroundColor Gray
    Write-Host "  (sonra editorle duzenleyin)"
    Stop-Transcript
    exit 1
}

# Token'ı kontrol et
$envContent = Get-Content $EnvFile -Raw
if ($envContent -match "TELEGRAM_BOT_TOKEN=(.+)") {
    $token = $matches[1].Trim()
    if ($token -eq "" -or $token -like "YOUR*") {
        Write-Host "  [HATA] Gecersiz Telegram token!" -ForegroundColor Red
        Write-Host "  Lutfen .env dosyasina gecerli bir Telegram Bot Token girin."
        Stop-Transcript
        exit 1
    }
    Write-Host "  [OK] Token bulundu: $($token.Substring(0, 10))..." -ForegroundColor Green
} else {
    Write-Host "  [HATA] TELEGRAM_BOT_TOKEN bulunamadi!" -ForegroundColor Red
    Stop-Transcript
    exit 1
}

# ─── 3. Telegram test ────────────────────────────────
Write-Host ""
Write-Host "[3/5] Telegram baglantisi test ediliyor..." -ForegroundColor Yellow

# .env'den chat_id'yi oku
$chatId = "6988108865"
if ($envContent -match "TELEGRAM_CHAT_ID=(.+)") {
    $chatId = $matches[1].Trim()
}

$testResult = python -c "
import requests, os
from dotenv import load_dotenv
load_dotenv('$EnvFile'.Replace('\\', '/'))
token = os.getenv('TELEGRAM_BOT_TOKEN', '')
chat_id = os.getenv('TELEGRAM_CHAT_ID', '$chatId')
if token:
    r = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', 
        json={'chat_id': chat_id, 'text': '<b>RTUG SURROUND DAEMON</b>\nKurulum test mesaji basarili! ✅', 'parse_mode': 'HTML'}, timeout=10)
    print(f'OK:{r.status_code}')
else:
    print('NO_TOKEN')
" 2>&1

if ($testResult -match "OK:200") {
    Write-Host "  [OK] Telegram baglantisi basarili! Test mesaji gonderildi." -ForegroundColor Green
} elseif ($testResult -match "OK:") {
    Write-Host "  [UYARI] Telegram baglantisi kuruldu ama HTTP: $($testResult)" -ForegroundColor Yellow
} else {
    Write-Host "  [HATA] Telegram baglantisi basarisiz: $testResult" -ForegroundColor Red
    Write-Host "  Devam ediliyor (manuel duzeltebilirsiniz)..."
}

# ─── 4. Daemon'u test et ─────────────────────────────
Write-Host ""
Write-Host "[4/5] Daemon test ediliyor (tek seferlik tarama)..." -ForegroundColor Yellow

$testScan = python "$DaemonScript" --once --no-telegram --no-crypto 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Daemon calisiyor!" -ForegroundColor Green
} else {
    Write-Host "  [UYARI] Daemon testi sorunlu:" -ForegroundColor Yellow
    Write-Host "  $testScan" -ForegroundColor Gray
}

# ─── 5. Windows Task Scheduler ───────────────────────
Write-Host ""
Write-Host "[5/5] Windows Task Scheduler kurulumu..." -ForegroundColor Yellow

# Kullaniciya interval sor
$interval = Read-Host "Tarama araligi (dakika, varsayilan: 15)"
if ($interval -eq "" -or $interval -lt 1) { $interval = 15 }

python "$DaemonScript" --install --interval $interval

# ─── BITIS ───────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  KURULUM TAMAMLANDI!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Daemon her acilista otomatik baslayacak." -ForegroundColor White
Write-Host "  Manuel baslatmak icin:" -ForegroundColor Gray
Write-Host "    python rtug_surround_daemon.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  Task Scheduler'dan kaldirmak icin:" -ForegroundColor Gray
Write-Host "    python rtug_surround_daemon.py --uninstall" -ForegroundColor Gray
Write-Host ""
Write-Host "  Loglar: logs\surround_daemon.log" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

Stop-Transcript
