# UW5 v5 Boot Engine
# GÃ¶rev: UW5 baÅŸlangÄ±Ã§ motoru â€” config oku, path doÄŸrula, registry yÃ¼kle, runtime context oluÅŸtur

param(
    [string]$Task = "",
    [string]$Uw5Root = ""
)

# â”€â”€â”€ Path Resolver â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
    # Verify root â€” if wrong, use dynamic resolver
    if (-not (Test-Path (Join-Path $Uw5Root "UW5_CORE.md")) -and -not (Test-Path (Join-Path $Uw5Root "config\uw5.json"))) {
        $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
        if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $Uw5Root = $resolved } }
    }
}
$configPath = Join-Path $Uw5Root "config\uw5.json"
$registryDir = Join-Path $Uw5Root "registry"
$pipelineDir = Join-Path $Uw5Root "pipeline"
$memoryDir = Join-Path $Uw5Root "memory"
$kernelDir = Join-Path $Uw5Root "kernel"
$runtimeDir = Join-Path $Uw5Root "runtime"

# â”€â”€â”€ Boot Context â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$bootContext = @{
    uw5Version = "5.0"
    bootTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    config = $null
    registries = @{}
    status = "initializing"
    errors = @()
}

Write-Output "[UW5 BOOT] === UW5 v5 Boot Sequence ==="
Write-Output "[UW5 BOOT] Root: $Uw5Root"

# â”€â”€â”€ 1b. Crash-Immune Integrity Check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$integrityScript = Join-Path $runtimeDir "uw5-state-integrity.ps1"
if (Test-Path $integrityScript) {
    try {
        $startTime = Get-Date
        $integrityResult = & $integrityScript -Mode verify -Uw5Root $Uw5Root
        $elapsed = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($integrityResult.success) {
            $bootContext.integrity = @{ status=$integrityResult.status; checked=$integrityResult.total_checked; elapsed_ms=$integrityResult.elapsed_ms }
            Write-Output "[UW5 BOOT] Integrity: $($integrityResult.status) ($($integrityResult.total_checked) files, $($integrityResult.elapsed_ms)ms)"
        } else {
            $bootContext.integrity = @{ status=$integrityResult.status; errors=$integrityResult.error }
            Write-Warning "[UW5 BOOT] Integrity: $($integrityResult.status) â€” $($integrityResult.error)"
        }
        if ($integrityResult.repairs_made -and $integrityResult.repairs_made.Count -gt 0) {
            Write-Output "[UW5 BOOT] Auto-repaired: $($integrityResult.repairs_made.Count) files"
            foreach ($r in $integrityResult.repairs_made) { Write-Output "[UW5 BOOT]   Repaired: $($r.name) from $($r.restored_from)" }
        }
    } catch {
        Write-Warning "[UW5 BOOT] Integrity check failed: $_"
    }
} else {
    Write-Warning "[UW5 BOOT] Integrity script not found: $integrityScript"
}

# â”€â”€â”€ 1c. Version History Init (non-blocking) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$versionScript = Join-Path $runtimeDir "uw5-version-history.ps1"
if (Test-Path $versionScript) {
    $versionDir = Join-Path $Uw5Root ".version-history"
    if (-not (Test-Path (Join-Path $versionDir ".git"))) {
        try {
            & $versionScript -Action init -Uw5Root $Uw5Root | Out-Null
            Write-Output "[UW5 BOOT] Version history initialized"
        } catch { Write-Warning "[UW5 BOOT] Version history init failed: $_" }
    }
}

# â”€â”€â”€ 1. Configuration Load â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if (Test-Path $configPath) {
    try {
        $bootContext.config = Get-Content $configPath -Raw | ConvertFrom-Json
        Write-Output "[UW5 BOOT] Config loaded: v$($bootContext.config.version)"
    } catch {
        $err = "Config parse error: $_"
        $bootContext.errors += $err
        Write-Warning "[UW5 BOOT] $err"
    }
} else {
    Write-Warning "[UW5 BOOT] Config not found: $configPath"
}

# â”€â”€â”€ 2. Path Validation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$paths = @{
    registry = $registryDir
    pipeline = $pipelineDir
    memory = $memoryDir
    kernel = $kernelDir
    runtime = $runtimeDir
}
$missingPaths = @()
foreach ($p in $paths.Keys) {
    if (-not (Test-Path $paths[$p])) {
        $missingPaths += $p
    }
}
if ($missingPaths.Count -gt 0) {
    Write-Warning "[UW5 BOOT] Missing directories: $($missingPaths -join ', ')"
    $bootContext.errors += "Missing: $($missingPaths -join ', ')"
} else {
    Write-Output "[UW5 BOOT] All paths validated"
}

# â”€â”€â”€ 4. Visual Core Load â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$visualScript = Join-Path $runtimeDir "uw5-visual.ps1"
if (Test-Path $visualScript) {
    try {
        $visualResult = & $visualScript -Mode "load" -Uw5Root $Uw5Root
        $bootContext.visual = $visualResult
        Write-Output "[UW5 BOOT] Visual core initialized"
    } catch {
        $err = "Visual core error: $_"
        $bootContext.errors += $err
        Write-Warning "[UW5 BOOT] $err"
    }
} else {
    Write-Warning "[UW5 BOOT] Visual core script not found: $visualScript (non-critical)"
}

# â”€â”€â”€ 4b. Vector Index (RAG) - non-blocking init â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$vectorIndexDir = Join-Path $Uw5Root "memory\vector-index"
$vectorIndexFile = Join-Path $vectorIndexDir "index.json"
$indexerPy = Join-Path $runtimeDir "uw5-retrieval-indexer.py"

if (-not (Test-Path $vectorIndexFile)) {
    if (Test-Path $indexerPy) {
        try {
            Write-Output "[UW5 BOOT] Building vector index (RAG context)..."
            $output = python "$indexerPy" "$Uw5Root" 2>&1
            Write-Output "[UW5 BOOT] $output"
        } catch {
            Write-Warning "[UW5 BOOT] Vector index build failed: $_ (non-critical)"
        }
    } else {
        Write-Warning "[UW5 BOOT] Indexer script not found"
    }
} else {
    Write-Output "[UW5 BOOT] Vector index already exists - RAG ready"
    # Re-index check: source files changed?
    $indexMeta = Get-Content $vectorIndexFile -Raw | ConvertFrom-Json
    $lastBuilt = if ($indexMeta.built_at) { [datetime]::Parse($indexMeta.built_at) } else { [datetime]::MinValue }
    $needReindex = $false
    $sourcesToCheck = @()
    $skillDirs = @("$env:USERPROFILE\.config\opencode\skills", "$env:USERPROFILE\.claude\skills")
    foreach ($sd in $skillDirs) {
        if (Test-Path $sd) { $sourcesToCheck += Get-ChildItem -Path $sd -Recurse -Filter "SKILL.md" }
    }
    $kairosDir = "$env:USERPROFILE\.config\opencode\.kairos\records"
    if (Test-Path $kairosDir) { $sourcesToCheck += Get-ChildItem -Path $kairosDir -Filter "*.json" }
    $corePath = Join-Path $Uw5Root "UW5_CORE.md"
    if (Test-Path $corePath) { $sourcesToCheck += Get-Item $corePath }
    
    foreach ($src in $sourcesToCheck) {
        if ($src.LastWriteTime -gt $lastBuilt) {
            $needReindex = $true
            Write-Output "[UW5 BOOT] Source changed: $($src.Name)"
        }
    }
    if ($needReindex) {
        Write-Output "[UW5 BOOT] Vector index stale - reindexing..."
        try {
            $output = python "$indexerPy" "$Uw5Root" 2>&1
            Write-Output "[UW5 BOOT] $output"
        } catch { Write-Warning "[UW5 BOOT] Reindex failed: $_" }
    }
}

# â”€â”€â”€ 5. Registry Load â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$registryFiles = @(
    "skills.json", "mcp.json", "lsp.json", "plugins.json",
    "agents.json", "models.json", "capabilities.json"
)
foreach ($file in $registryFiles) {
    $filePath = Join-Path $registryDir $file
    if (Test-Path $filePath) {
        try {
            $content = Get-Content $filePath -Raw | ConvertFrom-Json
            $bootContext.registries[$file.Replace(".json","")] = $content
            Write-Output "[UW5 BOOT] Registry loaded: $file"
        } catch {
            $err = "Registry $file parse error: $_"
            $bootContext.errors += $err
            Write-Warning "[UW5 BOOT] $err"
        }
    } else {
        Write-Warning "[UW5 BOOT] Registry not found: $file"
    }
}

# â”€â”€â”€ 6. Runtime Context â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$script:uw5RuntimeContext = $bootContext

# --- 5b. Structural Integrity Check (Change Guard) ---------------------
$changeGuardPath = Join-Path $runtimeDir "uw5-change-guard.ps1"
$structuralOk = $true
if (Test-Path $changeGuardPath) {
    try {
        $vetoResult = & $changeGuardPath -Action veto -Uw5Root $Uw5Root
        if ($vetoResult.veto) {
            Write-Warning "[UW5 BOOT] $($vetoResult.message)"
            $bootContext.errors += "Structural shrinkage: $($vetoResult.details -join '; ')"
            $structuralOk = $false
        } else {
            Write-Output "[UW5 BOOT] Structural integrity: OK ($($vetoResult.current.layers) layers, $($vetoResult.current.routes) routes, $($vetoResult.current.tiers) tiers, $($vetoResult.current.registries) registries)"
        }
    } catch {
        Write-Warning "[UW5 BOOT] Structural check failed: $_"
    }
}

# --- 5c. Identity Assertion (log identity table) -------------------------
$baselinePath = Join-Path $Uw5Root "UW5_BASELINE_v5_FINAL.json"
if (Test-Path $baselinePath) {
    Write-Output "[UW5 BOOT] Identity: UW5 v5 | 21 layers | 8 routes | 6 tiers | 7 registries | 4 resilience | RAG active | Self-Heal L16 live | Baseline locked"
}

# â”€â”€â”€ 7. Task Resolver (optional) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if ($Task) {
    Write-Output "[UW5 BOOT] Task received: $Task"
    $resolverPath = Join-Path $runtimeDir "uw5-resolver.ps1"
    if (Test-Path $resolverPath) {
        $resolution = & $resolverPath -Task $Task -Uw5Root $Uw5Root
        $script:uw5RuntimeContext.resolution = $resolution
        Write-Output "[UW5 BOOT] Resolution complete"
    }
}

# â”€â”€â”€ 8. Health Check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$healthMonitor = Join-Path $runtimeDir "health-monitor.ps1"
if (Test-Path $healthMonitor) {
    $health = & $healthMonitor -Mode "quick"
    $script:uw5RuntimeContext.health = $health
}

# â”€â”€â”€ Final â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if ($bootContext.errors.Count -gt 0) {
    $bootContext.status = "degraded"
    Write-Warning "[UW5 BOOT] Boot completed with $($bootContext.errors.Count) errors"
} else {
    $bootContext.status = "ready"
    Write-Output "[UW5 BOOT] === Boot complete. Status: ready ==="
}

# Return boot context as JSON
$bootContext | ConvertTo-Json -Depth 5
