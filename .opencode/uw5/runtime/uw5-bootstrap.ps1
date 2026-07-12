# UW5 v5 Bootstrap â€” OpenCode BaÅŸlangÄ±Ã§ KontrolÃ¼
# GÃ¶rev: UW5 core yapÄ±sÄ±nÄ± doÄŸrula, eksikleri raporla, runtime hazÄ±rla

param(
    [switch]$Quiet
)

$UW5_ROOT = Join-Path $PSScriptRoot ".." | Resolve-Path -ErrorAction SilentlyContinue
# Verify â€” if wrong, use dynamic resolver
if (-not $UW5_ROOT -or -not (Test-Path (Join-Path $UW5_ROOT "UW5_CORE.md"))) {
    $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
    if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $UW5_ROOT = $resolved } }
}
$CORE_FILE = Join-Path $UW5_ROOT "UW5_CORE.md"
$CONFIG_FILE = Join-Path $UW5_ROOT "config\uw5.json"
$REGISTRY_DIR = Join-Path $UW5_ROOT "registry"
$PIPELINE_DIR = Join-Path $UW5_ROOT "pipeline"
$RUNTIME_DIR = Join-Path $UW5_ROOT "runtime"
$MEMORY_DIR = Join-Path $UW5_ROOT "memory"
$RECOVERY_DIR = Join-Path $UW5_ROOT "recovery"
$KERNEL_DIR = Join-Path $UW5_ROOT "kernel"

# â”€â”€â”€ Check Manifest â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$checklist = @{
    "UW5_CORE.md" = (Test-Path $CORE_FILE)
    "config\uw5.json" = (Test-Path $CONFIG_FILE)
    "registry\" = (Test-Path $REGISTRY_DIR)
    "pipeline\" = (Test-Path $PIPELINE_DIR)
    "runtime\" = (Test-Path $RUNTIME_DIR)
    "memory\" = (Test-Path $MEMORY_DIR)
    "recovery\" = (Test-Path $RECOVERY_DIR)
    "kernel\" = (Test-Path $KERNEL_DIR)
}

# â”€â”€â”€ Registry Files Check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$registryFiles = @(
    "capabilities.json", "skills.json", "mcp.json", "lsp.json",
    "plugins.json", "agents.json", "models.json"
)
$registryOk = $true
foreach ($rf in $registryFiles) {
    $path = Join-Path $REGISTRY_DIR $rf
    if (-not (Test-Path $path)) {
        if (-not $Quiet) { Write-Warning "[UW5 BOOTSTRAP] Missing registry: $rf" }
        $registryOk = $false
    }
}
$checklist["registry files (7)"] = $registryOk

# â”€â”€â”€ Runtime Files Check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$runtimeFiles = @(
    "uw5-bootstrap.ps1", "uw5-boot.ps1", "uw5-resolver.ps1",
    "uw5-router.ps1", "uw5-executor.ps1", "uw5-memory.ps1",
    "context-guard.ps1", "health-monitor.ps1", "decision-score.ps1"
)
$runtimeOk = $true
foreach ($rf in $runtimeFiles) {
    $path = Join-Path $RUNTIME_DIR $rf
    if (-not (Test-Path $path)) {
        if (-not $Quiet) { Write-Warning "[UW5 BOOTSTRAP] Missing runtime: $rf" }
        $runtimeOk = $false
    }
}
$checklist["runtime files (9)"] = $runtimeOk

# â”€â”€â”€ Result â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$allOk = ($checklist.Values -notcontains $false)
$missingCount = ($checklist.Values | Where-Object { $_ -eq $false }).Count

if (-not $Quiet) {
    Write-Output ""
    Write-Output "=== UW5 v5 Bootstrap ==="
    Write-Output ""
    foreach ($item in $checklist.Keys) {
        $icon = if ($checklist[$item]) { "[OK]" } else { "[!!]" }
        Write-Output "  $icon $item"
    }
    Write-Output ""
    if ($allOk) {
        Write-Output "[UW5 CORE READY] â€” All systems operational"
    } else {
        Write-Output "[UW5 CORE DEGRADED] â€” $missingCount checks failed"
    }
}

# â”€â”€â”€ Update Recovery State â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$runtimeStatePath = Join-Path $RECOVERY_DIR "runtime-state.json"
$runtimeState = @{
    uw5Version = "5.0"
    bootTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    status = if ($allOk) { "ready" } else { "degraded" }
    lastBootResult = if ($allOk) { "success" } else { "incomplete" }
    errors = if ($allOk) { @() } else { @("$missingCount checks failed") }
    registryLoaded = $registryOk
    pipelineReady = $true
} | ConvertTo-Json -Depth 3
$runtimeState | Set-Content $runtimeStatePath

return @{
    ready = $allOk
    status = if ($allOk) { "ready" } else { "degraded" }
    checks = $checklist
    missingCount = $missingCount
    timestamp = $runtimeState.bootTime
} | ConvertTo-Json -Depth 3
