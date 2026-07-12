param(
    [string]$BackupDir = "C:\Users\cagda\.opencode-backups",
    [string]$From = "",
    [switch]$Latest,
    [switch]$Full,
    [switch]$List
)

$ErrorActionPreference = "Continue"
$wsRoot = Split-Path -Parent $PSScriptRoot
$host.UI.RawUI.WindowTitle = "SNA Restore — Singularity Engine"

$DATE = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Step {
    param([string]$Text) Write-Host $Text -NoNewline -ForegroundColor Yellow
}
function Write-OK { Write-Host " OK" -ForegroundColor Green }
function Write-Skip { Write-Host " ATLANDI" -ForegroundColor DarkGray }
function Write-Error { param([string]$Text) Write-Host "[HATA] $Text" -ForegroundColor Red }

# ============================================
#  LIST BACKUPS
# ============================================
function Show-Backups {
    $backups = Get-ChildItem "$BackupDir\sna-*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if (-not $backups) {
        Write-Host "Yedek bulunamadi: $BackupDir" -ForegroundColor Yellow
        return
    }
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  SNA YEDEK LISTESI" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    foreach ($b in $backups) {
        $size = (Get-ChildItem $b.FullName -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer } | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        $sizeMB = [math]::Round(($size/1MB), 2)
        $files = @(Get-ChildItem $b.FullName -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer }).Count
        $hasRestore = Test-Path "$($b.FullName)\restore.ps1"
        $restoreIcon = if ($hasRestore) { "R" } else { "-" }
        Write-Host "  [$restoreIcon] $($b.Name)" -ForegroundColor White
        Write-Host "         $sizeMB MB | $files dosya | $($b.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor DarkGray
    }
    Write-Host ""
}

# ============================================
#  RESTORE FROM DIR
# ============================================
function Do-RestoreFromDir {
    param([string]$SourceDir)

    if (-not (Test-Path $SourceDir)) {
        Write-Error "Kaynak dizin bulunamadi: $SourceDir"
        return
    }

    $restoreScript = "$SourceDir\restore.ps1"
    if (-not (Test-Path $restoreScript)) {
        Write-Error "restore.ps1 bulunamadi: $restoreScript"
        return
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  SNA — SINGULARITY ENGINE" -ForegroundColor Cyan
    Write-Host "  GERI YUKLEME" -ForegroundColor Cyan
    Write-Host "  Baslangic: $DATE" -ForegroundColor Cyan
    Write-Host "  Kaynak: $SourceDir" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "UYARI: Bu islem mevcut ayarlari SILEBILIR!" -ForegroundColor Red
    Write-Host "Devam etmek icin ENTER'a bas, iptal icin CTRL+C" -ForegroundColor Yellow
    $null = Read-Host

    & $restoreScript -Full:$Full.IsPresent
}

# ============================================
#  MAIN
# ============================================
if ($List) {
    Show-Backups
    exit 0
}

if ($From) {
    Do-RestoreFromDir -SourceDir $From
    exit 0
}

if ($Latest -or (-not $From)) {
    $backups = Get-ChildItem "$BackupDir\sna-*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if (-not $backups) {
        Show-Backups
        Write-Error "Hic yedek bulunamadi. Once yedek almalisin: .\scripts\sna-backup.ps1"
        exit 1
    }
    $latest = $backups[0].FullName
    Write-Host "Son yedek: $latest" -ForegroundColor Cyan
    Do-RestoreFromDir -SourceDir $latest
}
