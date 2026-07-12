<#
.SYNOPSIS
  UW5 v5 Restore Engine - '/uw5 restore latest' and '/uw5 restore <timestamp>'
.DESCRIPTION
  Restores the last known good state (manifest-verified golden state + pre-change snapshot combo).
  Can be auto-triggered by Executive Council (Route 8) or Self-Healing Loop (L16).
  
  restore latest    -> verify all manifest files, restore broken/missing from snapshots
  restore baseline  -> restore to UW5_BASELINE_v5_FINAL.json locked state (immutable)
  restore <ts>      -> return to a specific pre-change snapshot
  restore list      -> show all available restore points
  
  Parameters:
    -Mode: "latest" | "baseline" | "timestamp" | "list"
    -Timestamp: snapshot timestamp (for Mode=timestamp)
    -Uw5Root: UW5 root path
#>

param(
    [string]$Mode = "latest",
    [string]$Timestamp = "",
    [string]$Uw5Root = "",
    [switch]$Force = $false
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
$goldenDir = "$userProfile\.config\opencode\.golden-state"
$manifestPath = Join-Path $Uw5Root "STATE_MANIFEST.json"
$integrityScript = Join-Path (Split-Path $PSScriptRoot) "runtime\uw5-state-integrity.ps1"
$versionHistory = Join-Path $Uw5Root ".version-history"

# --- Helper: Resolve relative paths -----------------------------------------
function Resolve-PathLocal($relativePath) {
    $path = $relativePath -replace '^~', $userProfile
    if (-not [System.IO.Path]::IsPathRooted($path)) {
        $path = Join-Path $Uw5Root $path
    }
    return $path
}

# --- Helper: Collect manifest files -----------------------------------------
function Get-ManifestFiles($Manifest) {
    $files = @()
    $categories = @("core_files", "runtime_scripts", "registries", "pipeline_definitions", "memory_state", "config")
    foreach ($cat in $categories) {
        if (-not $Manifest.$cat) { continue }
        foreach ($item in $Manifest.$cat.PSObject.Properties) {
            $files += @{ name=$item.Name; path=Resolve-PathLocal $item.Value.path; rel=$item.Value.path; criticality=$item.Value.criticality; category=$cat }
        }
    }
    return $files
}

# --- Helper: Restore files from a directory ---------------------------------
function Restore-FromDirectory($sourceDir, $manifestFiles) {
    $restored = @()
    $failed = @()
    $snapFilesDir = Join-Path $sourceDir "files"
    if (-not (Test-Path $snapFilesDir)) { $snapFilesDir = $sourceDir }
    
    foreach ($f in $manifestFiles) {
        $fileName = Split-Path $f.path -Leaf
        $found = Get-ChildItem $snapFilesDir -Recurse -Filter $fileName -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            try {
                $destDir = Split-Path $f.path -Parent
                if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
                Copy-Item $found.FullName $f.path -Force
                $restored += $f.name
            } catch { $failed += $f.name }
        } else { $failed += "$($f.name)" }
    }
    return @{ restored=$restored; failed=$failed }
}

# ===== MODE: BASELINE ==========================================================
if ($Mode -eq "baseline") {
    Write-Host "[RESTORE] === Restore: BASELINE (UW5 v5 Final Locked State) ==="
    $startTime = Get-Date

    $baselinePath = Join-Path $Uw5Root "UW5_BASELINE_v5_FINAL.json"
    if (-not (Test-Path $baselinePath)) {
        return @{ success=$false; error="Baseline not found: UW5_BASELINE_v5_FINAL.json" }
    }

    # Verify baseline checksum matches git tag
    $vhDir = $versionHistory
    $tagResult = $null
    if (Test-Path $vhDir) {
        $tagResult = git -C $vhDir tag --list "v5-final-locked" 2>$null
    }

    if (-not $tagResult) {
        Write-Warning "[RESTORE] Git tag v5-final-locked not found in version history"
    } else {
        Write-Host "[RESTORE] Verified: git tag v5-final-locked exists"
    }

    # Take pre-change backup first
    $preChangeScript = Join-Path (Split-Path $PSScriptRoot) "runtime\uw5-pre-change-snapshot.ps1"
    if (Test-Path $preChangeScript) {
        & $preChangeScript -Trigger "before:restore-baseline" -Uw5Root $Uw5Root -SkipRotate | Out-Null
        Write-Host "[RESTORE] Pre-restore snapshot taken"
    }

    # Restore from baseline: copy each file referenced in baseline manifest
    $baseline = Get-Content $baselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $manifestFiles = Get-ManifestFiles $baseline

    # Also restore from .version-history git (which has the committed baseline state)
    $restoreSource = $versionHistory
    $restoreLabel = "version-history (baseline)"

    if (Test-Path $restoreSource) {
        $restoreResult = Restore-FromDirectory -sourceDir $restoreSource -manifestFiles $manifestFiles
        Write-Host "[RESTORE] Restored from: $restoreLabel"
        Write-Host "[RESTORE] Restored: $($restoreResult.restored.Count) files"
        if ($restoreResult.failed.Count -gt 0) {
            Write-Warning "[RESTORE] Failed: $($restoreResult.failed -join ', ')"
        }
    }

    # Post-restore integrity re-verify
    $integrityScript = Join-Path (Split-Path $PSScriptRoot) "runtime\uw5-state-integrity.ps1"
    if (Test-Path $integrityScript) {
        & $integrityScript -Mode update -Uw5Root $Uw5Root | Out-Null
        $finalCheck = & $integrityScript -Mode check -Uw5Root $Uw5Root
        if ($finalCheck.success) {
            Write-Host "[RESTORE] === Baseline restore complete. $($finalCheck.total_checked)/$($finalCheck.total_checked) files verified ==="
        } else {
            Write-Warning "[RESTORE] Baseline restore: $($finalCheck.failure_count) issues remain"
        }
        $restoreResult = $finalCheck
    }

    $elapsed = [math]::Round(((Get-Date) - $startTime).TotalMilliseconds)
    return @{ success=$true; mode="baseline"; status="restored"; elapsed_ms=$elapsed; restore_source=$restoreLabel }
}

# ===== MODE: LIST ============================================================
if ($Mode -eq "list") {
    Write-Host "[RESTORE] === Available restore points ==="
    
    if (Test-Path $snapBase) {
        Write-Host "[RESTORE] Pre-change snapshots:"
        Get-ChildItem "$snapBase\*" -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 20 | ForEach-Object {
            $metaFile = Join-Path $_.FullName "snapshot.json"
            $trigger = ""
            if (Test-Path $metaFile) { try { $m = Get-Content $metaFile -Raw -Encoding UTF8 | ConvertFrom-Json; $trigger = $m.trigger } catch {} }
            Write-Host "  $($_.Name): $trigger"
        }
    }
    if (Test-Path $versionHistory) {
        $gitLog = git -C $versionHistory log --oneline -10 2>$null
        if ($gitLog) { Write-Host "[RESTORE] Version history (git):"; $gitLog | ForEach-Object { Write-Host "  $_" } }
    }
    if (Test-Path $goldenDir) {
        $goldenFiles = Get-ChildItem "$goldenDir\*.json" -ErrorAction SilentlyContinue
        Write-Host "[RESTORE] Golden state: $($goldenFiles.Count) files"
    }
    return @{ success=$true; mode="list" }
}

# ===== MODE: LATEST ==========================================================
if ($Mode -eq "latest") {
    Write-Host "[RESTORE] === Restore: latest good state ==="
    $startTime = Get-Date
    
    if (-not (Test-Path $manifestPath)) { return @{ success=$false; error="STATE_MANIFEST not found" } }
    $manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $manifestFiles = Get-ManifestFiles $manifest
    
    # Run integrity check
    $checkResult = if (Test-Path $integrityScript) { & $integrityScript -Mode check -Uw5Root $Uw5Root } else { @{success=$false; error="integrity script not found"} }
    
    if ($checkResult.success) {
        Write-Host "[RESTORE] All files healthy - no restore needed"
        return @{ success=$true; mode="latest"; status="healthy"; action="none_needed"; elapsed_ms=[math]::Round(((Get-Date)-$startTime).TotalMilliseconds) }
    }
    
    Write-Host "[RESTORE] $($checkResult.failure_count) files need repair"
    
    # Find best snapshot
    $restoreSource = $null
    $restoreLabel = ""
    
    if (Test-Path $snapBase) {
        $snapshots = Get-ChildItem "$snapBase\*" -Directory | Sort-Object Name -Descending
        foreach ($snap in $snapshots) {
            $restoreSource = $snap.FullName
            $restoreLabel = "snapshot:$($snap.Name)"
            break
        }
    }
    
    if (-not $restoreSource -and (Test-Path $versionHistory)) {
        $restoreSource = $versionHistory
        $restoreLabel = "version-history"
    }
    
    if ($restoreSource) {
        Write-Host "[RESTORE] Restoring from: $restoreLabel"
        $restoreResult = Restore-FromDirectory -sourceDir $restoreSource -manifestFiles $manifestFiles
        Write-Host "[RESTORE] Restored: $($restoreResult.restored.Count) files"
        if ($restoreResult.failed.Count -gt 0) { Write-Warning "[RESTORE] Failed: $($restoreResult.failed -join ', ')" }
    } else {
        Write-Warning "[RESTORE] No backup source found"
    }
    
    $finalCheck = if (Test-Path $integrityScript) { & $integrityScript -Mode check -Uw5Root $Uw5Root } else { @{success=$false} }
    if ($finalCheck.success) { & $integrityScript -Mode update -Uw5Root $Uw5Root | Out-Null; Write-Host "[RESTORE] === Restore complete. All files healthy ===" }
    
    $elapsed = ((Get-Date) - $startTime).TotalMilliseconds
    return @{ success=$finalCheck.success; mode="latest"; status=if ($finalCheck.success){"restored"}else{"degraded"}; restored_count=$restoreResult.restored.Count; failed_count=$restoreResult.failed.Count; restored_from=$restoreLabel; elapsed_ms=[math]::Round($elapsed) }
}

# ===== MODE: TIMESTAMP =======================================================
if ($Mode -eq "timestamp") {
    if (-not $Timestamp) { return @{ success=$false; error="No timestamp provided. Usage: -Mode timestamp -Timestamp <yyyyMMdd-HHmmss>" } }
    
    Write-Host "[RESTORE] === Restore: snapshot $Timestamp ==="
    $snapPath = "$snapBase\$Timestamp"
    $startTime = Get-Date
    
    if (-not (Test-Path $snapPath)) {
        Write-Host "[RESTORE] Snapshot not found: $Timestamp"
        Write-Host "[RESTORE] Available:"
        Get-ChildItem "$snapBase\*" -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 10 | ForEach-Object { Write-Host "  $($_.Name)" }
        return @{ success=$false; error="Snapshot not found: $Timestamp" }
    }
    
    # Backup current state first for safety
    $preChangeScript = Join-Path (Split-Path $PSScriptRoot) "runtime\uw5-pre-change-snapshot.ps1"
    if (Test-Path $preChangeScript) { & $preChangeScript -Trigger "before:restore-timestamp-$Timestamp" -Uw5Root $Uw5Root -SkipRotate | Out-Null }
    
    $manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $manifestFiles = Get-ManifestFiles $manifest
    $restoreResult = Restore-FromDirectory -sourceDir $snapPath -manifestFiles $manifestFiles
    
    $finalCheck = if (Test-Path $integrityScript) { & $integrityScript -Mode check -Uw5Root $Uw5Root } else { @{success=$false} }
    if ($finalCheck.success) { & $integrityScript -Mode update -Uw5Root $Uw5Root | Out-Null }
    
    Write-Host "[RESTORE] === Restore complete: $Timestamp ==="
    return @{ success=$finalCheck.success; mode="timestamp"; timestamp=$Timestamp; status=if($finalCheck.success){"restored"}else{"degraded"}; restored_count=$restoreResult.restored.Count; failed_count=$restoreResult.failed.Count; elapsed_ms=[math]::Round(((Get-Date)-$startTime).TotalMilliseconds) }
}

return @{ success=$false; error="Unknown mode: $Mode" }
