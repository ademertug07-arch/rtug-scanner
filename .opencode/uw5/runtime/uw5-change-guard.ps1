<#
.SYNOPSIS
  UW5 v5 Change Guard -- pre-change snapshot + structural shrinkage detection
.DESCRIPTION
  Two-phase guard:
    Phase 1 (snapshot): Auto-take pre-change snapshot of critical files
    Phase 2 (veto):    Compare proposed change against baseline structural counts
                         If pipeline layers (21), routes (8), tiers (6), registries (7)
                         would decrease → REJECT + warn user
  
  Parameters:
    -Action: "snapshot" (take pre-change snapshot) | "veto" (check structural counts)
    -TargetFiles: comma-separated file paths to check (for veto)
    -Uw5Root: UW5 root path
#>

param(
    [string]$Action = "snapshot",
    [string]$TargetFiles = "",
    [string]$Uw5Root = ""
)

if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
    if (-not (Test-Path (Join-Path $Uw5Root "UW5_CORE.md"))) {
        $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
        if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $Uw5Root = $resolved } }
    }
}

$pipelineDir = Join-Path $Uw5Root "pipeline"
$registryDir = Join-Path $Uw5Root "registry"
$baselinePath = Join-Path $Uw5Root "UW5_BASELINE_v5_FINAL.json"

function Get-StructuralCounts {
    $counts = @{ layers=0; routes=0; tiers=0; registries=0 }

    # Pipeline layers
    $fullPath = Join-Path $pipelineDir "full.json"
    if (Test-Path $fullPath) {
        $full = Get-Content $fullPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $counts.layers = $full.layers.Count
        $counts.routes = $full.routes.Count
    }

    # Model tiers
    $modelsPath = Join-Path $registryDir "models.json"
    if (Test-Path $modelsPath) {
        $models = Get-Content $modelsPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $counts.tiers = @($models.tiers.PSObject.Properties).Count
    }

    # Registry count
    $registryFiles = @("skills.json", "mcp.json", "lsp.json", "plugins.json", "agents.json", "models.json", "capabilities.json")
    $counts.registries = @($registryFiles | Where-Object { Test-Path (Join-Path $registryDir $_) }).Count

    return $counts
}

function Get-BaselineCounts {
    if (-not (Test-Path $baselinePath)) { return $null }
    try {
        $baseline = Get-Content $baselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
        # Read from embedded structural_counts (immutable - set at lock time)
        if ($baseline.structural_counts) {
            return @{
                layers = $baseline.structural_counts.layers
                routes = $baseline.structural_counts.routes
                tiers = $baseline.structural_counts.tiers
                registries = $baseline.structural_counts.registries
            }
        }
        # Fallback: parse from manifest paths (less reliable)
        $regCount = @($baseline.registries.PSObject.Properties).Count
        return @{ layers=21; routes=5; tiers=6; registries=$regCount }
    } catch { return $null }
}

# ===== PHASE 1: SNAPSHOT ==================================================
if ($Action -eq "snapshot") {
    $snapScript = Join-Path (Split-Path $PSScriptRoot) "runtime\uw5-pre-change-snapshot.ps1"
    if (Test-Path $snapScript) {
        $result = & $snapScript -Trigger "change-guard:auto" -Uw5Root $Uw5Root
        Write-Output "[CHANGE-GUARD] Pre-change snapshot: $($result.snapshot_name) ($($result.files_copied) files)"
        return $result
    }
    return @{ success=$false; error="pre-change-snapshot.ps1 not found" }
}

# ===== PHASE 2: VETO (structural shrinkage detection) =====================
if ($Action -eq "veto") {
    $isCriticalChange = $false
    $criticalPatterns = @("capabilities.json", "models.json", "pipeline\full.json", "pipeline\fast.json", "pipeline\deep.json", "resolver.ps1", "executor.ps1")

    if ($TargetFiles) {
        $targets = $TargetFiles -split "," | ForEach-Object { $_.Trim() }
        $isCriticalChange = ($targets | Where-Object {
            $criticalPatterns | Where-Object { $_ -like "*$($_.Replace('\','/').Replace('/','*'))*" -or $_ -like "*$($_)*" }
        }).Count -gt 0
    }

    $current = Get-StructuralCounts
    $baseline = Get-BaselineCounts

    if (-not $baseline) {
        Write-Warning "[CHANGE-GUARD] Baseline not found -- cannot check structural shrinkage"
        return @{ action="veto"; veto=$false; reason="no_baseline"; warning="UW5_BASELINE_v5_FINAL.json not found" }
    }

    $shrinkage = @()
    if ($current.layers -lt $baseline.layers) { $shrinkage += "pipeline_layers: $($baseline.layers) -> $($current.layers)" }
    if ($current.routes -lt $baseline.routes) { $shrinkage += "routes: $($baseline.routes) -> $($current.routes)" }
    if ($current.tiers -lt $baseline.tiers) { $shrinkage += "model_tiers: $($baseline.tiers) -> $($current.tiers)" }
    if ($current.registries -lt $baseline.registries) { $shrinkage += "registries: $($baseline.registries) -> $($current.registries)" }

    if ($shrinkage.Count -gt 0) {
        $message = "[CHANGE-GUARD] STRUCTURAL SHRINKAGE DETECTED! Change AUTO-REJECTED:`n"
        $message += ($shrinkage -join "`n")
        $message += "`nBaseline preserved. User must be warned."

        Write-Warning $message
        return @{
            action="veto"; veto=$true;
            reason="structural_shrinkage"
            details = $shrinkage
            current = $current
            baseline = $baseline
            message = $message
        }
    }

    return @{ action="veto"; veto=$false; reason="ok"; current=$current; baseline=$baseline }
}

return @{ success=$false; error="Unknown action: $Action" }

