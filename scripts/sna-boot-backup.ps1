param(
    [int]$KeepLast = 5,
    [switch]$Silent
)

$ErrorActionPreference = "SilentlyContinue"
$BackupDir = "C:\Users\cagda\.opencode-backups"
$dateStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$wsRoot = "C:\Users\cagda\OneDrive\Masaüstü\open code mode"
$CLAUDEDIR = "$env:USERPROFILE\.claude"
$CONFIGDIR = "$env:USERPROFILE\.config\opencode"
$OPENCODEDIR = "$env:USERPROFILE\.opencode"
$LOCALSHARE = "$env:USERPROFILE\.local\share\opencode"

# Quick backup — configs + DB only, no skills (hızlı, ~saniyeler)
$bakDir = "$BackupDir\sna-boot-$dateStamp"
New-Item -ItemType Directory -Path $bakDir -Force | Out-Null

# Configs
$cfgDir = "$bakDir\config"
New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null
@(
    @{src="$wsRoot\opencode.jsonc"; dst="config-workspace.jsonc"}
    @{src="$CONFIGDIR\opencode.jsonc"; dst="config-global.jsonc"}
    @{src="$CLAUDEDIR\CLAUDE.md"; dst="claude-md.md"}
    @{src="$CLAUDEDIR\settings.json"; dst="claude-settings.json"}
    @{src="$CLAUDEDIR\.credentials.json"; dst="claude-credentials.json"}
) | ForEach-Object { if (Test-Path $_.src) { Copy-Item $_.src "$cfgDir\$($_.dst)" -Force } }

# Custom commands
if (Test-Path "$wsRoot\.opencode\commands") {
    $cDir = "$bakDir\custom-commands"
    New-Item -ItemType Directory -Path $cDir -Force | Out-Null
    Copy-Item "$wsRoot\.opencode\commands\*" $cDir -Recurse -Force
}

# Scripts
if (Test-Path "$wsRoot\scripts") {
    $sDir = "$bakDir\scripts"
    New-Item -ItemType Directory -Path $sDir -Force | Out-Null
    Copy-Item "$wsRoot\scripts\*.ps1" $sDir -Force
}

# Core DB
$dbDir = "$bakDir\cache-core"
New-Item -ItemType Directory -Path $dbDir -Force | Out-Null
@(
    "$LOCALSHARE\opencode.db",
    "$LOCALSHARE\auth.json",
    "$LOCALSHARE\mcp-auth.json"
) | ForEach-Object { if (Test-Path $_) { Copy-Item $_ $dbDir\ -Force } }

# Env durumu
@" 
BOOT: $dateStamp
GITHUB_TOKEN: $(if ([Environment]::GetEnvironmentVariable("GITHUB_TOKEN","User")) {"SET"} else {"NOT SET"})
BRAVE_API_KEY: $(if ([Environment]::GetEnvironmentVariable("BRAVE_API_KEY","User")) {"SET"} else {"NOT SET"})
OBSIDIAN_API_KEY: $(if ([Environment]::GetEnvironmentVariable("OBSIDIAN_API_KEY","User")) {"SET"} else {"NOT SET"})
"@ | Set-Content "$bakDir\env-vars.txt" -Force

# Auto-generate restore script (minimal)
@"
param([switch]`$Full)
`$ErrorActionPreference = "Continue"
`$bakDir = `$PSScriptRoot
`$wsRoot = "C:\Users\cagda\OneDrive\Masa$([char]0x00FC)st$([char]0x00FC)\open code mode"
`$CLAUDEDIR = "`$env:USERPROFILE\.claude"
`$CONFIGDIR = "`$env:USERPROFILE\.config\opencode"
`$LOCALSHARE = "`$env:USERPROFILE\.local\share\opencode"
Write-Host "[SNA BOOT RESTORE] Geri yukleniyor..." -ForegroundColor Cyan
`$cfg = "`$bakDir\config"
if (Test-Path `$cfg) {
    @{src="config-workspace.jsonc";dst="`$wsRoot\opencode.jsonc"},
    @{src="config-global.jsonc";dst="`$CONFIGDIR\opencode.jsonc"},
    @{src="claude-md.md";dst="`$CLAUDEDIR\CLAUDE.md"},
    @{src="claude-settings.json";dst="`$CLAUDEDIR\settings.json"},
    @{src="claude-credentials.json";dst="`$CLAUDEDIR\.credentials.json"}
} | ForEach-Object { `$sp="`$cfg\`$_.src"; if (Test-Path `$sp) { `$dp=Split-Path `$_.dst -Parent; if (-not (Test-Path `$dp)){New-Item-ItemType Directory-Path `$dp-Force|Out-Null}; Copy-Item `$sp `$_.dst -Force } }
if (Test-Path "`$bakDir\cache-core") { Copy-Item "`$bakDir\cache-core\*" "`$LOCALSHARE\" -Force -ErrorAction SilentlyContinue }
Write-Host "[SNA BOOT RESTORE] Tamam" -ForegroundColor Green
"@ | Set-Content "$bakDir\restore.ps1" -Force

# Cleanup: eski boot yedeklerini temizle (keep last N)
$allBoot = Get-ChildItem "$BackupDir\sna-boot-*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($allBoot.Count -gt $KeepLast) {
    $allBoot | Select-Object -Skip $KeepLast | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    }
}

if (-not $Silent) {
    $totalSize = (Get-ChildItem $bakDir -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer } | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
    $totalFiles = @(Get-ChildItem $bakDir -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer }).Count
    Write-Host "[SNA BOOT] Yedek: $bakDir ($([math]::Round($totalSize/1MB,2)) MB, $totalFiles dosya)" -ForegroundColor Cyan
}
