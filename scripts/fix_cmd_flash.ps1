<#
.SYNOPSIS
    CMD Flash Fix Script - SecHealthUI fix + Startup cleanup + DISM/SFC
    Yönetici PowerShell'de çalıştır (sağ tık > PowerShell ile Çalıştır)
#>

$ErrorActionPreference = "Stop"
$host.UI.RawUI.WindowTitle = "CMD FLASH FIX — Çalışıyor..."

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   CMD FLASH KESIN COZUM SCRIPTI" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# === ADIM 1: Windows Security (SecHealthUI) sıfırlama ===
Write-Host "[1/5] Windows Security sıfırlanıyor..." -ForegroundColor Yellow
try {
    Get-AppxPackage *Microsoft.SecHealthUI* | Reset-AppxPackage
    Write-Host "  ✓ SecHealthUI resetlendi" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Hata: $($_.Exception.Message)" -ForegroundColor Red
}

# === ADIM 2: Defender platform sıfırlama ===
Write-Host "[2/5] Windows Defender sıfırlanıyor..." -ForegroundColor Yellow
try {
    $mpCmd = "${env:ProgramFiles}\Windows Defender\MpCmdRun.exe"
    if (Test-Path $mpCmd) {
        & $mpCmd -ResetPlatform
        Write-Host "  ✓ Defender resetlendi" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Hata: $($_.Exception.Message)" -ForegroundColor Red
}

# === ADIM 3: Startup VBS/PS1 scriptlerini temizleme ===
Write-Host "[3/5] Startup scriptleri temizleniyor..." -ForegroundColor Yellow
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$quarantinePath = "$env:USERPROFILE\Desktop\STARTUP_QUARANTINE"

if (-not (Test-Path $quarantinePath)) {
    New-Item -ItemType Directory -Path $quarantinePath -Force | Out-Null
}

$suspiciousFiles = @(
    "OMEGA_Engine.vbs",
    "SingularityBoot.launch.vbs",
    "SingularityBoot.ps1",
    "QuantOmegaServices.lnk",
    "GameModeDaemon.lnk"
)

foreach ($file in $suspiciousFiles) {
    $fullPath = Join-Path $startupPath $file
    if (Test-Path $fullPath) {
        Move-Item -Path $fullPath -Destination $quarantinePath -Force
        Write-Host "  → $file karantinaya alindi → $quarantinePath" -ForegroundColor Green
    }
}

# Ollama (isteğe bağlı - sorun çıkarmaz ama cmd açarsa karantina)
$ollamaPath = Join-Path $startupPath "Ollama.lnk"
if (Test-Path $ollamaPath) {
    Write-Host "  ! Ollama.lnk mevcut (genelde sorunsuz, dokunulmadi)" -ForegroundColor DarkYellow
}

# Snipping hotkey'ler (sorun çıkarmaz)
Write-Host "  - Snipping Hotkey, Win-Shift-S Hotkey → dokunulmadi" -ForegroundColor DarkGray

# === ADIM 4: DISM + SFC ===
Write-Host "[4/5] DISM + SFC taramasi basliyor (5-10 dk sürebilir)..." -ForegroundColor Yellow
try {
    Write-Host "  DISM checkhealth..." -ForegroundColor Gray
    dism /online /cleanup-image /checkhealth
    Write-Host "  DISM restorehealth..." -ForegroundColor Gray
    dism /online /cleanup-image /restorehealth
    Write-Host "  ✓ DISM tamam" -ForegroundColor Green
} catch {
    Write-Host "  ✗ DISM hatasi: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    Write-Host "  SFC /scannow..." -ForegroundColor Gray
    sfc /scannow
    Write-Host "  ✓ SFC tamam" -ForegroundColor Green
} catch {
    Write-Host "  ✗ SFC hatasi: $($_.Exception.Message)" -ForegroundColor Red
}

# === ADIM 5: FragPunk webview fix ===
Write-Host "[5/5] FragPunk WebView fix..." -ForegroundColor Yellow
$fragPunkWebView = "C:\Program Files (x86)\Steam\steamapps\common\FragPunk\FragPunk\Binaries\Win64\webviewsupport.cef904430\webview_support_browser.EXE"
if (Test-Path $fragPunkWebView) {
    Write-Host "  FragPunk webview destegi mevcut" -ForegroundColor DarkYellow
    Write-Host "  Öneri: FragPunk ayarlarindan 'WebView destegi' kapatilabilir" -ForegroundColor DarkYellow
    Write-Host "  veya Steam > FragPunk > Properties > Launch Options'a eklenti:" -ForegroundColor DarkYellow
    Write-Host "  -nocef -notexturestreaming" -ForegroundColor White
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   ISLEM TAMAMLANDI" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SIRADAKI ADIMLAR:" -ForegroundColor Yellow
Write-Host "  1. Bilgisayari YENIDEN BASLAT"
Write-Host "  2. CMD flash kesildiyse → sorun cozuldu"
Write-Host "  3. Hala oluyorsa bana bildir"
Write-Host ""
Write-Host "KARANTINA ALINAN DOSYALAR:" -ForegroundColor Cyan
Write-Host "  Masaustu > STARTUP_QUARANTINE klasorunde"
Write-Host "  Geri almak icin dosyalari geri tasi"
Write-Host "============================================" -ForegroundColor Cyan
Read-Host "ENTER'a basarak kapat"
