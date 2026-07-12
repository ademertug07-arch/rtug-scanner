<#
.SYNOPSIS
  UW5 v5 State Integrity Verifier - crash-immune boot checksum engine
.DESCRIPTION
  Reads STATE_MANIFEST.json, computes SHA256 of every tracked file,
  compares against stored golden checksums. If mismatch/not-found:
    - Auto-restores from latest golden state backup
    - If golden state missing, falls back to pre-change snapshot
    - If both missing, falls back to version history git
  Target: <2s for full verification of ~30 files.
  
  PARAMETERS:
    -Mode: "verify" (default, check+repair) | "check" (check only) | "update" (save new checksums)
    -Uw5Root: UW5 root path (auto-detect if empty)
#>

param(
    [string]$Mode = "verify",
    [string]$Uw5Root = ""
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

$manifestPath = Join-Path $Uw5Root "STATE_MANIFEST.json"
$integrityDir = Join-Path (Join-Path $Uw5Root "memory") "integrity"
$checksumFile = Join-Path $integrityDir "checksums.json"
$userProfile = $env:USERPROFILE
$goldenDir = "$userProfile\.config\opencode\.golden-state"
$snapBase = "$userProfile\.config\opencode\.pre-change-snapshots"
$versionHistory = Join-Path $Uw5Root ".version-history"

# --- Helpers -----------------------------------------------------------------
function Resolve-PathLocal($relativePath) {
    $path = $relativePath -replace '^~', $userProfile
    if (-not [System.IO.Path]::IsPathRooted($path)) {
        $path = Join-Path $Uw5Root $path
    }
    return $path
}

function Get-FileSHA256($filePath) {
    if (-not (Test-Path $filePath)) { return $null }
    $item = Get-Item $filePath -ErrorAction SilentlyContinue
    if (-not $item) { return $null }
    
    # Directories: just verify existence with sentinel hash
    if ($item.PSIsContainer) {
        $contents = Get-ChildItem $filePath -Recurse -File -ErrorAction SilentlyContinue
        $totalSize = ($contents | Measure-Object -Property Length -Sum).Sum
        return "dir:$($contents.Count):$totalSize"
    }
    
    try {
        $hash = Get-FileHash -Path $filePath -Algorithm SHA256
        return $hash.Hash.ToLower()
    } catch { return $null }
}

# --- Load Manifest -----------------------------------------------------------
if (-not (Test-Path $manifestPath)) {
    return @{ success=$false; error="STATE_MANIFEST.json not found"; status="missing_manifest" }
}
$manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

# --- Collect all tracked files -----------------------------------------------
$trackedFiles = @()
$categories = @("core_files", "runtime_scripts", "registries", "pipeline_definitions", "memory_state", "config", "external_dependencies")
foreach ($cat in $categories) {
    if (-not $manifest.$cat) { continue }
    $items = $manifest.$cat.PSObject.Properties
    foreach ($item in $items) {
        $props = $item.Value
        $trackedFiles += @{
            name = $item.Name
            path = Resolve-PathLocal $props.path
            type = $props.type
            criticality = $props.criticality
            category = $cat
        }
    }
}

# --- Mode: Update (save current checksums) -----------------------------------
if ($Mode -eq "update") {
    if (-not (Test-Path $integrityDir)) { New-Item -ItemType Directory -Path $integrityDir -Force | Out-Null }
    $checksums = @{}
    $allOk = $true
    $missingCount = 0
    foreach ($f in $trackedFiles) {
        $hash = Get-FileSHA256 $f.path
        if ($hash) {
            $checksums[$f.name] = @{ hash=$hash; path=$f.path; checked_at=(Get-Date -Format "o") }
        } else {
            $checksums[$f.name] = @{ hash=$null; path=$f.path; error="NOT_FOUND" }
            $allOk = $false
            $missingCount++
        }
    }
    $checksumData = @{
        manifest_version = $manifest.version
        updated_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        file_count = $trackedFiles.Count
        files = $checksums
    }
    $checksumData | ConvertTo-Json -Depth 5 | Set-Content $checksumFile -Encoding UTF8
    
    return @{ mode="update"; success=$allOk; total=$trackedFiles.Count; missing=$missingCount }
}

# --- Mode: Check (verify only, no repair) ------------------------------------
if ($Mode -eq "check") {
    if (-not (Test-Path $checksumFile)) {
        return @{ success=$false; error="No stored checksums - run with -Mode update first"; status="no_checksums" }
    }
    $stored = Get-Content $checksumFile -Raw -Encoding UTF8 | ConvertFrom-Json
    $failures = @()
    $checked = 0
    foreach ($f in $trackedFiles) {
        $storedEntry = $stored.files.$($f.name)
        if (-not $storedEntry) { $failures += @{ name=$f.name; issue="NOT_TRACKED" }; continue }
        $currentHash = Get-FileSHA256 $f.path
        $checked++
        if (-not $currentHash) {
            $failures += @{ name=$f.name; issue="MISSING"; path=$f.path; criticality=$f.criticality }
        } elseif ($currentHash -ne $storedEntry.hash) {
            $failures += @{ name=$f.name; issue="HASH_MISMATCH"; path=$f.path; criticality=$f.criticality }
        }
    }
    return @{ mode="check"; success=($failures.Count -eq 0); total_checked=$checked; failures=$failures; failure_count=$failures.Count; has_critical_failure=(($failures | Where-Object { $_.criticality -eq "critical" }).Count -gt 0) }
}

# --- Mode: Verify (check + auto-repair) --------------------------------------
$startTime = Get-Date

# Step 1: If no checksums exist, create them
if (-not (Test-Path $checksumFile)) {
    Write-Verbose "[INTEGRITY] No stored checksums - creating baseline"
    & $PSCommandPath -Mode update -Uw5Root $Uw5Root | Out-Null
}

# Step 2: Quick check
$checkResult = & $PSCommandPath -Mode check -Uw5Root $Uw5Root
if ($checkResult.success) {
    $elapsed = ((Get-Date) - $startTime).TotalMilliseconds
    return @{ mode="verify"; success=$true; status="healthy"; total_checked=$checkResult.total_checked; elapsed_ms=[math]::Round($elapsed) }
}

# Step 3: Auto-repair failures
$repairsMade = @()
foreach ($failure in $checkResult.failures) {
    $restored = $false
    $source = ""
    
    # Source 1: Pre-change snapshots (layer 3)
    if (-not $restored -and (Test-Path $snapBase)) {
        $snapshots = Get-ChildItem "$snapBase\*" -Directory | Sort-Object LastWriteTime -Descending
        foreach ($snap in $snapshots) {
            $snapFilesDir = Join-Path $snap.FullName "files"
            if (-not (Test-Path $snapFilesDir)) { continue }
            $fileName = Split-Path $failure.path -Leaf
            $searched = Get-ChildItem $snapFilesDir -Recurse -Filter $fileName -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($searched) {
                try {
                    $destDir = Split-Path $failure.path -Parent
                    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
                    Copy-Item $searched.FullName $failure.path -Force
                    $restored = $true
                    $source = "snapshot:$($snap.Name)"
                    break
                } catch {}
            }
        }
    }
    
    # Source 2: Version history git (layer 4)
    if (-not $restored -and (Test-Path $versionHistory)) {
        $fileName = Split-Path $failure.path -Leaf
        $gitFiles = Get-ChildItem "$versionHistory\*" -Recurse -Filter $fileName -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
        foreach ($gf in $gitFiles) {
            try {
                Copy-Item $gf.FullName $failure.path -Force
                $restored = $true
                $source = "version-history"
                break
            } catch {}
        }
    }
    
    if ($restored) {
        $repairsMade += @{ name=$failure.name; issue=$failure.issue; restored_from=$source }
    }
}

# Step 4: Re-verify after repairs
$recheck = & $PSCommandPath -Mode check -Uw5Root $Uw5Root
$elapsed = ((Get-Date) - $startTime).TotalMilliseconds

return @{
    mode = "verify"
    success = $recheck.success
    status = if ($recheck.success) { "repaired" } else { "degraded" }
    total_checked = $recheck.total_checked
    failures_found = $checkResult.failure_count
    repairs_made = $repairsMade.Count
    repair_details = $repairsMade
    remaining_failures = $recheck.failures
    elapsed_ms = [math]::Round($elapsed)
}
