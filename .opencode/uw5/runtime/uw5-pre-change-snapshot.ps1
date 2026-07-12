<#
.SYNOPSIS
  UW5 v5 Pre-Change Snapshot - 4th resilience layer
.DESCRIPTION
  Automatic "before major change" snapshot.
  Triggers: RAG integration, new SKILL.md, opencode.jsonc change,
  OpenCode update, UW5_CORE.md change, STATE_MANIFEST update.
  
  Snapshots stored at ~/.config/opencode/.pre-change-snapshots/ with timestamped dirs.
  Independent of Golden State (layer 1, max 10) - keeps last 20 snapshots.
  
  Parameters:
    -Trigger: event name (e.g. "before:opencode-update-v1.4.2", "before:rag-layer-install")
    -Uw5Root: UW5 root path (auto-detect if empty)
    -SkipRotate: skip rotation (for testing)
#>

param(
    [string]$Trigger = "manual",
    [string]$Uw5Root = "",
    [switch]$SkipRotate = $false
)

# --- Path Resolution ---------------------------------------------------------
if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
    if (-not (Test-Path (Join-Path $Uw5Root "UW5_CORE.md"))) {
        $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
        if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $Uw5Root = $resolved } }
    }
}

$userProfile = $env:USERPROFILE
$snapBase = "$userProfile\.config\opencode\.pre-change-snapshots"
if (-not (Test-Path $snapBase)) { New-Item -ItemType Directory -Path $snapBase -Force | Out-Null }

# --- Timestamped Snapshot Directory ------------------------------------------
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$snapDir = "$snapBase\$ts"
New-Item -ItemType Directory -Path $snapDir -Force | Out-Null
$filesDir = Join-Path $snapDir "files"
New-Item -ItemType Directory -Path $filesDir -Force | Out-Null

# --- What to back up ---------------------------------------------------------
$items = @(
    @{src=Join-Path $Uw5Root "UW5_CORE.md"; rel="UW5_CORE.md"}
    @{src=Join-Path $Uw5Root "STATE_MANIFEST.json"; rel="STATE_MANIFEST.json"}
    @{src=Join-Path $Uw5Root "config\uw5.json"; rel="config\uw5.json"}
    @{src=Join-Path $Uw5Root "runtime\uw5-boot.ps1"; rel="runtime/uw5-boot.ps1"}
    @{src=Join-Path $Uw5Root "runtime\uw5-resolver.ps1"; rel="runtime/uw5-resolver.ps1"}
    @{src=Join-Path $Uw5Root "runtime\uw5-state-integrity.ps1"; rel="runtime/uw5-state-integrity.ps1"}
    @{src=Join-Path $Uw5Root "runtime\uw5-retrieval.ps1"; rel="runtime/uw5-retrieval.ps1"}
    @{src=Join-Path $Uw5Root "runtime\uw5-retrieval.py"; rel="runtime/uw5-retrieval.py"}
    @{src=Join-Path $Uw5Root "runtime\uw5-retrieval-indexer.py"; rel="runtime/uw5-retrieval-indexer.py"}
    @{src=Join-Path $Uw5Root "runtime\uw5-visual.ps1"; rel="runtime/uw5-visual.ps1"}
    @{src=Join-Path $Uw5Root "runtime\uw5-root-resolver.ps1"; rel="runtime/uw5-root-resolver.ps1"}
    @{src=Join-Path $Uw5Root "runtime\uw5-memory.ps1"; rel="runtime/uw5-memory.ps1"}
    @{src=Join-Path $Uw5Root "runtime\uw5-restore.ps1"; rel="runtime/uw5-restore.ps1"}
    @{src=Join-Path $Uw5Root "runtime\uw5-version-history.ps1"; rel="runtime/uw5-version-history.ps1"}
    @{src=Join-Path $Uw5Root "registry\skills.json"; rel="registry/skills.json"}
    @{src=Join-Path $Uw5Root "registry\mcp.json"; rel="registry/mcp.json"}
    @{src=Join-Path $Uw5Root "registry\agents.json"; rel="registry/agents.json"}
    @{src=Join-Path $Uw5Root "registry\models.json"; rel="registry/models.json"}
    @{src=Join-Path $Uw5Root "registry\capabilities.json"; rel="registry/capabilities.json"}
    @{src=Join-Path $Uw5Root "pipeline\fast.json"; rel="pipeline/fast.json"}
    @{src=Join-Path $Uw5Root "pipeline\full.json"; rel="pipeline/full.json"}
    @{src=Join-Path $Uw5Root "pipeline\deep.json"; rel="pipeline/deep.json"}
    @{src=Join-Path $Uw5Root "memory\kairos.json"; rel="memory/kairos.json"}
    @{src=Join-Path $Uw5Root "memory\golden.json"; rel="memory/golden.json"}
    @{src=Join-Path $Uw5Root "memory\visual-state.json"; rel="memory/visual-state.json"}
    @{src=Join-Path $Uw5Root "memory\integrity\checksums.json"; rel="memory/integrity/checksums.json"}
)

$externalItems = @(
    @{src="$userProfile\.config\opencode\config\opencode.jsonc"; rel="external/opencode.jsonc"}
    @{src="$userProfile\.config\opencode\AGENTS.md"; rel="external/AGENTS.md"}
    @{src="$userProfile\.config\opencode\scripts\init-session.ps1"; rel="external/init-session.ps1"}
    @{src="$userProfile\.config\opencode\scripts\golden-state.ps1"; rel="external/golden-state.ps1"}
    @{src="$userProfile\.config\opencode\scripts\rollback-manager.ps1"; rel="external/rollback-manager.ps1"}
)

# --- Copy files ---------------------------------------------------------------
$copied = 0
$failed = @()
foreach ($item in $items + $externalItems) {
    if (Test-Path $item.src) {
        $destPath = Join-Path $filesDir $item.rel
        $destDir = Split-Path $destPath -Parent
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        try {
            Copy-Item $item.src $destPath -Force
            $copied++
        } catch { $failed += $item.rel }
    } else { $failed += "$($item.rel)" }
}

# --- Copy vector index (if exists) ------------------------------------------
$vecIndexDir = Join-Path $Uw5Root "memory\vector-index"
if (Test-Path $vecIndexDir) {
    $vecDest = Join-Path $filesDir "memory/vector-index"
    New-Item -ItemType Directory -Path $vecDest -Force | Out-Null
    Get-ChildItem "$vecIndexDir\*" -File -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $vecDest $_.Name) -Force
    }
}

# --- Copy golden state refs -------------------------------------------------
$goldenDir = "$userProfile\.config\opencode\.golden-state"
if (Test-Path $goldenDir) {
    $goldenDest = Join-Path $filesDir "golden-state"
    New-Item -ItemType Directory -Path $goldenDest -Force | Out-Null
    Get-ChildItem "$goldenDir\*" -File -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $goldenDest $_.Name) -Force
    }
}

# --- Snapshot metadata -------------------------------------------------------
$meta = @{
    name = $ts
    trigger = $Trigger
    timestamp = (Get-Date -Format "o")
    created_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    uw5_version = "5.0"
    files_copied = $copied
    files_failed = $failed.Count
    failed_items = $failed
}
$meta | ConvertTo-Json -Depth 3 | Set-Content (Join-Path $snapDir "snapshot.json") -Encoding UTF8

# --- Rotation: keep last 20 --------------------------------------------------
if (-not $SkipRotate) {
    try {
        $allSnaps = Get-ChildItem "$snapBase\*" -Directory | Sort-Object Name -Descending
        if ($allSnaps.Count -gt 20) {
            $allSnaps | Select-Object -Skip 20 | ForEach-Object {
                Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {}
}

Write-Host "[SNAPSHOT] Pre-change snapshot saved: $ts ($copied files, $($failed.Count) failures)"

return @{
    success = ($failed.Count -eq 0)
    snapshot_name = $ts
    snapshot_path = $snapDir
    trigger = $Trigger
    files_copied = $copied
    files_failed = $failed.Count
    created_at = $meta.created_at
}
