param(
    [string]$BackupDir = "C:\Users\cagda\.opencode-backups",
    [switch]$Restore,
    [switch]$Quick,
    [switch]$Full,
    [string]$From = "",
    [string]$Name = ""
)

$ErrorActionPreference = "Continue"
$dateStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$scriptRoot = Split-Path -Parent $PSScriptRoot
$host.UI.RawUI.WindowTitle = "SNA Backup/Restore — Singularity Engine"
$wsRoot = $scriptRoot

$CLAUDEDIR = "$env:USERPROFILE\.claude"
$CONFIGDIR = "$env:USERPROFILE\.config\opencode"
$OPENCODEDIR = "$env:USERPROFILE\.opencode"
$LOCALSHARE = "$env:USERPROFILE\.local\share\opencode"
$CACHE = "$env:USERPROFILE\.cache\opencode"
$STARTUP = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

function Write-Status { param([string]$Msg, [string]$Color = "Gray") Write-Host ("[SNA][{0}] $Msg" -f (Get-Date -Format "HH:mm:ss")) -ForegroundColor $Color }

# ============================================
#  TANILAMA
# ============================================
function Get-SNADiagnostics {
    $report = @()

    $report += "=== SNA TANI RAPORU ==="
    $report += ""

    $checks = @(
        @{Path="$wsRoot\opencode.jsonc"; Label="Workspace config (opencode.jsonc)"},
        @{Path="$CONFIGDIR\opencode.jsonc"; Label="Global config"},
        @{Path="$CLAUDEDIR\CLAUDE.md"; Label="CLAUDE.md"},
        @{Path="$CLAUDEDIR\settings.json"; Label="Settings"},
        @{Path="$CLAUDEDIR\.credentials.json"; Label="Credentials"},
        @{Path="$wsRoot\scripts"; Label="Scripts dizini"},
        @{Path="$wsRoot\.opencode\commands"; Label="Custom commands"},
        @{Path="$CLAUDEDIR\skills"; Label="Skills dizini"},
        @{Path="$OPENCODEDIR\plugins"; Label="OpenCode plugins"},
        @{Path="$LOCALSHARE\opencode.db"; Label="OpenCode DB"},
        @{Path="$LOCALSHARE\auth.json"; Label="Auth JSON"},
        @{Path="$LOCALSHARE\mcp-auth.json"; Label="MCP Auth"}
    )

    foreach ($c in $checks) {
        $exists = Test-Path $c.Path
        $icon = if ($exists) { "OK" } else { "YOK" }
        $report += "[$icon] $($c.Label)"
    }

    $report += ""
    $report += "--- Ortam Degiskenleri ---"
    $report += "GITHUB_TOKEN: $(if ([Environment]::GetEnvironmentVariable('GITHUB_TOKEN','User')) {'SET'} else {'NOT SET'})"
    $report += "BRAVE_API_KEY: $(if ([Environment]::GetEnvironmentVariable('BRAVE_API_KEY','User')) {'SET'} else {'NOT SET'})"
    $report += "OBSIDIAN_API_KEY: $(if ([Environment]::GetEnvironmentVariable('OBSIDIAN_API_KEY','User')) {'SET'} else {'NOT SET'})"

    $report += ""
    $report += "--- Skills ---"
    $skillDir = "$CLAUDEDIR\skills"
    if (Test-Path $skillDir) {
        $skills = Get-ChildItem $skillDir -Directory | Sort-Object Name
        foreach ($s in $skills) { $report += "  $($s.Name)" }
        $report += "Toplam: $($skills.Count) skill"
    } else {
        $report += "  (skills dizini yok)"
    }

    $report += ""
    $report += "--- Yedekler ---"
    $backups = Get-ChildItem "$BackupDir\sna-*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if ($backups) {
        foreach ($b in $backups) {
            $size = (Get-ChildItem $b.FullName -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer } | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
            $sizeMB = [math]::Round(($size/1MB), 2)
            $report += "  $($b.Name) — $sizeMB MB"
        }
    } else {
        $report += "  (yedek yok)"
    }

    return $report -join "`n"
}

# ============================================
#  BACKUP
# ============================================
function Do-Backup {
    param([bool]$IncludeSkills = $true, [bool]$IncludeCache = $false)

    $suffix = if ($Name) { $Name } else { "full" }
    $bakDir = "$BackupDir\sna-$suffix-$dateStamp"
    New-Item -ItemType Directory -Path $bakDir -Force | Out-Null
    Write-Status "Yedek: $bakDir" -Color Cyan

    # --- 1. KONFIG DOSYALARI ---
    Write-Status "[1/8] Konfig dosyalari..." -Color Yellow
    $configs = @(
        @{src="$wsRoot\opencode.jsonc"; dst="config-workspace.jsonc"}
        @{src="$CONFIGDIR\opencode.jsonc"; dst="config-global.jsonc"}
        @{src="$CONFIGDIR\AGENTS.md"; dst="config-agents-md.md"}
        @{src="$CONFIGDIR\opencode.acp-addon.json"; dst="config-acp-addon.json"}
        @{src="$CLAUDEDIR\CLAUDE.md"; dst="claude-md.md"}
        @{src="$CLAUDEDIR\settings.json"; dst="claude-settings.json"}
        @{src="$CLAUDEDIR\.credentials.json"; dst="claude-credentials.json"}
        @{src="$wsRoot\AGENTS.md"; dst="agents-md.md"}
        @{src="$STARTUP\SingularityBoot.ps1"; dst="boot-singularity.ps1"}
        @{src="$STARTUP\SingularityBoot.launch.vbs"; dst="boot-singularity.vbs"}
    )
    $cfgDir = "$bakDir\config"
    New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null
    foreach ($c in $configs) {
        if (Test-Path $c.src) { Copy-Item -Path $c.src -Destination "$cfgDir\$($c.dst)" -Force; Write-Status "  OK $($c.dst)" -Color Green }
        else { Write-Status "  YOK $($c.src)" -Color DarkYellow }
    }

    # --- 2. OPENCODE PLUGIN'LERI ---
    Write-Status "[2/8] OpenCode plugin'leri..." -Color Yellow
    if (Test-Path "$OPENCODEDIR\plugins") {
        $pDir = "$bakDir\opencode-plugins"
        New-Item -ItemType Directory -Path $pDir -Force | Out-Null
        Copy-Item -Path "$OPENCODEDIR\plugins\*.ts" -Destination $pDir -Force -ErrorAction SilentlyContinue
        $count = @(Get-ChildItem "$OPENCODEDIR\plugins" -Filter *.ts -ErrorAction SilentlyContinue).Count
        Write-Status "  $count plugin yedeklendi" -Color Green
    } else { Write-Status "  YOK" -Color DarkYellow }

    # --- 3. DOMAIN AGENT'LERI ---
    Write-Status "[3/8] Domain agent'lari..." -Color Yellow
    if (Test-Path "$OPENCODEDIR\agents") {
        $aDir = "$bakDir\opencode-agents"
        New-Item -ItemType Directory -Path $aDir -Force | Out-Null
        Copy-Item -Path "$OPENCODEDIR\agents\*.md" -Destination $aDir -Force -ErrorAction SilentlyContinue
        $count = @(Get-ChildItem "$OPENCODEDIR\agents" -Filter *.md -ErrorAction SilentlyContinue).Count
        Write-Status "  $count agent yedeklendi" -Color Green
    } else { Write-Status "  YOK" -Color DarkYellow }

    # --- 4. BRIDGE DOSYALARI ---
    Write-Status "[4/8] Bridge dosyalari..." -Color Yellow
    if (Test-Path "$OPENCODEDIR\bridge") {
        $bDir = "$bakDir\opencode-bridge"
        New-Item -ItemType Directory -Path $bDir -Force | Out-Null
        Copy-Item -Path "$OPENCODEDIR\bridge\*" -Destination $bDir -Force -ErrorAction SilentlyContinue
        $count = @(Get-ChildItem "$OPENCODEDIR\bridge" -File -ErrorAction SilentlyContinue).Count
        Write-Status "  $count bridge dosyasi yedeklendi" -Color Green
    } else { Write-Status "  YOK" -Color DarkYellow }

    # --- 5. CUSTOM COMMANDS ---
    Write-Status "[5/8] Custom commands..." -Color Yellow
    if (Test-Path "$wsRoot\scripts") {
        $sDir = "$bakDir\scripts"
        New-Item -ItemType Directory -Path $sDir -Force | Out-Null
        Copy-Item -Path "$wsRoot\scripts\*.ps1" -Destination $sDir -Force -ErrorAction SilentlyContinue
        $count = @(Get-ChildItem "$wsRoot\scripts" -Filter *.ps1 -ErrorAction SilentlyContinue).Count
        Write-Status "  $count script yedeklendi" -Color Green
    } else { Write-Status "  YOK" -Color DarkYellow }

    # --- 4. CUSTOM COMMANDS ---
    Write-Status "[4/6] Custom commands..." -Color Yellow
    if (Test-Path "$OPENCODEDIR\commands") {
        $cDir = "$bakDir\opencode-commands"
        New-Item -ItemType Directory -Path $cDir -Force | Out-Null
        Copy-Item -Path "$OPENCODEDIR\commands\*" -Destination $cDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Status "  OK" -Color Green
    } else { Write-Status "  YOK" -Color DarkYellow }

    # --- 6. SKILL'LER ---
    Write-Status "[6/8] Skill'ler..." -Color Yellow
    if ($IncludeSkills -and (Test-Path "$CLAUDEDIR\skills")) {
        $skillCount = @(Get-ChildItem "$CLAUDEDIR\skills" -Directory).Count
        $sDir = "$bakDir\skills"
        New-Item -ItemType Directory -Path $sDir -Force | Out-Null
        foreach ($skill in (Get-ChildItem "$CLAUDEDIR\skills" -Directory)) {
            $skillParent = "$bakDir\skills\$($skill.Name)"
            New-Item -ItemType Directory -Path $skillParent -Force | Out-Null
            Copy-Item -Path "$($skill.FullName)\*" -Destination "$skillParent\" -Recurse -Force -ErrorAction SilentlyContinue
        }
        Write-Status "  $skillCount skill yedeklendi" -Color Green
    } else { Write-Status "  ATLANDI" -Color DarkYellow }

    # --- 7. SNAPSHOT'LAR ---
    Write-Status "[7/8] Snapshot'lar..." -Color Yellow
    $snapDir = "C:\Users\cagda\.uw5-snapshots"
    if (Test-Path $snapDir) {
        $snapBak = "$bakDir\uw5-snapshots"
        New-Item -ItemType Directory -Path $snapBak -Force | Out-Null
        Copy-Item -Path "$snapDir\*" -Destination $snapBak -Recurse -Force -ErrorAction SilentlyContinue
        $count = @(Get-ChildItem $snapBak -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Status "  $count snapshot dosyasi yedeklendi" -Color Green
    } else { Write-Status "  YOK" -Color DarkYellow }

    # --- 8. CACHE / CORE DB ---
    Write-Status "[8/8] Core veritabani..." -Color Yellow
    $dbFiles = @(
        "$LOCALSHARE\opencode.db",
        "$LOCALSHARE\auth.json",
        "$LOCALSHARE\mcp-auth.json"
    )
    $cDir = "$bakDir\cache-core"
    New-Item -ItemType Directory -Path $cDir -Force | Out-Null
    foreach ($db in $dbFiles) {
        if (Test-Path $db) { Copy-Item -Path $db -Destination "$cDir\" -Force; Write-Status "  OK $(Split-Path $db -Leaf)" -Color Green }
    }
    if ($IncludeCache) {
        Write-Status "  Cache (tam) yedekleniyor..." -Color Yellow
        foreach ($cd in @("$LOCALSHARE", "$CACHE")) {
            if (Test-Path $cd) {
                $name = Split-Path $cd -Leaf
                Copy-Item -Path "$cd\*" -Destination "$cDir\$name\" -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }

    # --- ORTAM DEGISKEN DURUMU ---
    $envFile = "$bakDir\config\env-vars.txt"
@"
GITHUB_TOKEN: $(if ([Environment]::GetEnvironmentVariable("GITHUB_TOKEN","User")) {"SET"} else {"NOT SET"})
BRAVE_API_KEY: $(if ([Environment]::GetEnvironmentVariable("BRAVE_API_KEY","User")) {"SET"} else {"NOT SET"})
OBSIDIAN_API_KEY: $(if ([Environment]::GetEnvironmentVariable("OBSIDIAN_API_KEY","User")) {"SET"} else {"NOT SET"})
OPENCODE_API_KEY: $(if ([Environment]::GetEnvironmentVariable("OPENCODE_API_KEY","User")) {"SET"} else {"NOT SET"})
SENTRY_AUTH_TOKEN: $(if ([Environment]::GetEnvironmentVariable("SENTRY_AUTH_TOKEN","User")) {"SET"} else {"NOT SET"})
"@ | Set-Content -Path $envFile -Force

    # --- OZET ---
    $totalSize = (Get-ChildItem $bakDir -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer } | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
    $totalFiles = @(Get-ChildItem $bakDir -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer }).Count
    $sizeMB = [math]::Round(($totalSize/1MB), 2)

    $summary = @"
========================================
  SNA YEDEK OZETI
========================================
  Tarih: $dateStamp
  Hedef: $bakDir
  Boyut: $sizeMB MB ($totalFiles dosya)
  Isim:  $suffix
  Skill'ler: $(if ($IncludeSkills){"DAHIL"}else{"HARIC"})
  Cache:  $(if ($IncludeCache){"TAM"}else{"SADECE DB"})
========================================
"@
    Write-Host $summary -ForegroundColor Cyan

    # --- RESTORE SCRIPTI GENERATE ET ---
    Generate-RestoreScript -BackupDir $bakDir

    Write-Status "YEDEK TAMAM" -Color Green
    return $bakDir
}

# ============================================
#  RESTORE SCRIPT GENERATOR
# ============================================
function Generate-RestoreScript {
    param([string]$BackupDir)

    $restoreContent = @'
param([switch]$Full)
$ErrorActionPreference = "Continue"
$bakDir = $PSScriptRoot
$wsRoot = "C:\Users\cagda\OneDrive\Masa$([char]0x00FC)st$([char]0x00FC)\open code mode"
$CLAUDEDIR = "$env:USERPROFILE\.claude"
$CONFIGDIR = "$env:USERPROFILE\.config\opencode"
$OPENCODEDIR = "$env:USERPROFILE\.opencode"
$LOCALSHARE = "$env:USERPROFILE\.local\share\opencode"
$STARTUP = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

$host.UI.RawUI.WindowTitle = "SNA Restore — Singularity Engine"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SNA GERI YUKLEME" -ForegroundColor Cyan
Write-Host "  Kaynak: $bakDir" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "UYARI: Mevcut ayarlar SILEBILIR!" -ForegroundColor Red
Write-Host "Devam icin ENTER, iptal icin CTRL+C" -ForegroundColor Yellow
$null = Read-Host

function Write-Step {
    param([string]$Text) Write-Host $Text -NoNewline -ForegroundColor Yellow
}
function Write-OK { Write-Host " OK" -ForegroundColor Green }
function Write-Skip { Write-Host " ATLANDI" -ForegroundColor DarkGray }

    # 1. Konfig dosyalari
Write-Step "[1/8] Konfig dosyalari..."
$cfgDir = "$bakDir\config"
if (Test-Path $cfgDir) {
    $map = @{
        "config-workspace.jsonc" = "$wsRoot\opencode.jsonc"
        "config-global.jsonc"   = "$CONFIGDIR\opencode.jsonc"
        "config-agents-md.md"   = "$CONFIGDIR\AGENTS.md"
        "config-acp-addon.json" = "$CONFIGDIR\opencode.acp-addon.json"
        "claude-md.md"          = "$CLAUDEDIR\CLAUDE.md"
        "claude-settings.json"  = "$CLAUDEDIR\settings.json"
        "claude-credentials.json" = "$CLAUDEDIR\.credentials.json"
        "agents-md.md"          = "$wsRoot\AGENTS.md"
        "boot-singularity.ps1"  = "$STARTUP\SingularityBoot.ps1"
        "boot-singularity.vbs"  = "$STARTUP\SingularityBoot.launch.vbs"
    }
    foreach ($src in $map.Keys) {
        $sp = "$cfgDir\$src"
        if (Test-Path $sp) {
            $dp = $map[$src]
            $dDir = Split-Path $dp -Parent
            if (-not (Test-Path $dDir)) { New-Item -ItemType Directory -Path $dDir -Force | Out-Null }
            Copy-Item -Path $sp -Destination $dp -Force
        }
    }
    Write-OK
} else { Write-Skip }

# 2. OpenCode plugin'leri
Write-Step "[2/8] OpenCode plugin'leri..."
$pluginDir = "$bakDir\opencode-plugins"
if (Test-Path $pluginDir) {
    if (-not (Test-Path $OPENCODEDIR\plugins)) { New-Item -ItemType Directory -Path "$OPENCODEDIR\plugins" -Force | Out-Null }
    Copy-Item -Path "$pluginDir\*.ts" -Destination "$OPENCODEDIR\plugins\" -Force -ErrorAction SilentlyContinue
    Write-OK
} else { Write-Skip }

# 3. Domain agent'lari
Write-Step "[3/8] Domain agent'lari..."
$agentDir = "$bakDir\opencode-agents"
if (Test-Path $agentDir) {
    if (-not (Test-Path $OPENCODEDIR\agents)) { New-Item -ItemType Directory -Path "$OPENCODEDIR\agents" -Force | Out-Null }
    Copy-Item -Path "$agentDir\*.md" -Destination "$OPENCODEDIR\agents\" -Force -ErrorAction SilentlyContinue
    Write-OK
} else { Write-Skip }

# 4. Bridge dosyalari
Write-Step "[4/8] Bridge dosyalari..."
$bridgeDir = "$bakDir\opencode-bridge"
if (Test-Path $bridgeDir) {
    if (-not (Test-Path $OPENCODEDIR\bridge)) { New-Item -ItemType Directory -Path "$OPENCODEDIR\bridge" -Force | Out-Null }
    Copy-Item -Path "$bridgeDir\*" -Destination "$OPENCODEDIR\bridge\" -Force -ErrorAction SilentlyContinue
    Write-OK
} else { Write-Skip }

# 5. Script'ler
Write-Step "[5/8] Script'ler..."
$scriptsDir = "$bakDir\scripts"
if (Test-Path $scriptsDir) {
    if (-not (Test-Path "$wsRoot\scripts")) { New-Item -ItemType Directory -Path "$wsRoot\scripts" -Force | Out-Null }
    Copy-Item -Path "$scriptsDir\*.ps1" -Destination "$wsRoot\scripts\" -Force
    Write-OK
} else { Write-Skip }

# 6. Custom commands
Write-Step "[6/8] Custom commands..."
$cmdDir = "$bakDir\opencode-commands"
if (Test-Path $cmdDir) {
    if (-not (Test-Path $OPENCODEDIR\commands)) { New-Item -ItemType Directory -Path "$OPENCODEDIR\commands" -Force | Out-Null }
    Copy-Item -Path "$cmdDir\*" -Destination "$OPENCODEDIR\commands\" -Recurse -Force
    Write-OK
} else { Write-Skip }

# 7. Skill'ler
Write-Step "[7/8] Skill'ler..."
$skillDir = "$bakDir\skills"
if (Test-Path $skillDir -and $Full) {
    $target = "$CLAUDEDIR\skills"
    Get-ChildItem $skillDir -Directory | ForEach-Object {
        $dest = "$target\$($_.Name)"
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
        Copy-Item -Path "$($_.FullName)\*" -Destination "$dest\" -Recurse -Force
    }
    Write-OK
} else { Write-Skip }

# 8. Core DB
Write-Step "[8/8] Core veritabani..."
$dbDir = "$bakDir\cache-core"
if (Test-Path $dbDir) {
    Copy-Item -Path "$dbDir\*" -Destination "$LOCALSHARE\" -Force -ErrorAction SilentlyContinue
    Write-OK
} else { Write-Skip }

# 9. Snapshot'lar
Write-Step "[9/8] Snapshot'lar..."
$snapDir = "$bakDir\uw5-snapshots"
if (Test-Path $snapDir) {
    $snapTarget = "C:\Users\cagda\.uw5-snapshots"
    if (-not (Test-Path $snapTarget)) { New-Item -ItemType Directory -Path $snapTarget -Force | Out-Null }
    Copy-Item -Path "$snapDir\*" -Destination $snapTarget -Recurse -Force -ErrorAction SilentlyContinue
    Write-OK
} else { Write-Skip }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SNA GERI YUKLEME TAMAMLANDI!" -ForegroundColor Green
Write-Host "  OpenCode'u yeniden baslatabilirsin" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cikmak icin ENTER'a bas..." -ForegroundColor DarkGray
$null = Read-Host
'@

    Set-Content -Path "$BackupDir\restore.ps1" -Value $restoreContent -Force
    Write-Status "Restore scripti olusturuldu: $BackupDir\restore.ps1" -Color Green
}

# ============================================
#  RESTORE
# ============================================
function Do-Restore {
    param([string]$SourceDir)

    if (-not (Test-Path $SourceDir)) {
        Write-Host "[SNA][HATA] Kaynak dizin bulunamadi: $SourceDir" -ForegroundColor Red
        return
    }

    $restoreScript = "$SourceDir\restore.ps1"
    if (Test-Path $restoreScript) {
        Write-Host "[SNA] $SourceDir'den geri yukleniyor..." -ForegroundColor Cyan
        & $restoreScript -Full:$Full.IsPresent
    } else {
        Write-Host "[SNA][HATA] restore.ps1 bulunamadi" -ForegroundColor Red
    }
}

# ============================================
#  LIST BACKUPS
# ============================================
function Show-Backups {
    $backups = Get-ChildItem "$BackupDir\sna-*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if (-not $backups) {
        Write-Host "[SNA] Yedek bulunamadi: $BackupDir" -ForegroundColor Yellow
        return
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  SNA YEDEK LISTESI" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    foreach ($b in $backups) {
        $size = (Get-ChildItem $b.FullName -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer } | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        $sizeMB = [math]::Round(($size/1MB), 2)
        $files = @(Get-ChildItem $b.FullName -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer }).Count
        $hasRestore = Test-Path "$($b.FullName)\restore.ps1"
        $restoreIcon = if ($hasRestore) { "R" } else { "-" }
        Write-Host "  [$restoreIcon] $($b.Name)" -ForegroundColor White
        Write-Host "         Boyut: $sizeMB MB | Dosya: $files" -ForegroundColor DarkGray
        Write-Host "         Tarih: $($b.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor DarkGray
        Write-Host ""
    }
}

# ============================================
#  MAIN
# ============================================
if ($Restore) {
    if ($From) {
        Do-Restore -SourceDir $From
    } else {
        $backups = Get-ChildItem "$BackupDir\sna-*" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
        if (-not $backups) {
            Write-Host "[SNA] Yedek bulunamadi: $BackupDir" -ForegroundColor Red
            exit 1
        }
        $latest = $backups[0].FullName
        Write-Host "Son yedek: $latest" -ForegroundColor Cyan
        Do-Restore -SourceDir $latest
    }
} else {
    $quick = $Quick.IsPresent -or (-not $Full.IsPresent)
    Do-Backup -IncludeSkills (-not $quick) -IncludeCache $Full.IsPresent
}
