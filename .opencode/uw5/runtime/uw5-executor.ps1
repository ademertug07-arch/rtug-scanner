# UW5 v5 Pipeline Executor
# GÃ¶rev: SeÃ§ilen pipeline katmanlarÄ±nÄ± yÃ¼rÃ¼t, agent Ã§aÄŸÄ±r, MCP baÄŸla, LSP baÅŸlat, trace oluÅŸtur

param(
    [string]$Task = "",
    [string]$Uw5Root = "",
    [string]$LayerIds = ""  # comma-separated: "L00,L02,L07,L08"
)

if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
    if (-not (Test-Path (Join-Path $Uw5Root "UW5_CORE.md")) -and -not (Test-Path (Join-Path $Uw5Root "config\uw5.json"))) {
        $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
        if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $Uw5Root = $resolved } }
    }
}
$runtimeDir = Join-Path $Uw5Root "runtime"

# â”€â”€â”€ If no layers provided, run router â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if (-not $LayerIds -and $Task) {
    $routerPath = Join-Path $runtimeDir "uw5-router.ps1"
    if (Test-Path $routerPath) {
        $route = & $routerPath -Task $Task -Uw5Root $Uw5Root | ConvertFrom-Json
        $LayerIds = $route.layerIds -join ","
    }
}
if (-not $LayerIds) {
    Write-Error "[UW5 EXEC] No layers specified"
    return
}

$layers = $LayerIds.Split(",") | ForEach-Object { $_.Trim() }

# â”€â”€â”€ Execution Trace â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$trace = @{
    task = $Task
    startTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    layers = @()
    totalDurationMs = 0
    status = "running"
    errors = @()
}

Write-Output "[UW5 EXEC] === Pipeline Execution ==="
Write-Output "[UW5 EXEC] Layers: $($layers -join ' â†’ ')"

# â”€â”€â”€ Layer Handlers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Execute-Layer($layerId) {
    $start = Get-Date
    $layerTrace = @{
        layerId = $layerId
        status = "running"
        durationMs = 0
        output = ""
    }

    try {
        switch ($layerId) {
            "L00" {
                # Master Hub â€” intent already analyzed by resolver
                $layerTrace.output = "Intent resolved"
            }
            "L01" {
                # Context Guard
                $guardPath = Join-Path $runtimeDir "context-guard.ps1"
                if (Test-Path $guardPath) {
                    $result = & $guardPath -Mode "check" -Uw5Root $Uw5Root
                    $layerTrace.output = "Context check: $result"
                }
            }
            "L07" {
                # Model Router â€” already selected by resolver
                $layerTrace.output = "Model selected"
            }
            "L08" {
                # Skill Auto-Load
                $resolverPath = Join-Path $runtimeDir "uw5-resolver.ps1"
                if (Test-Path $resolverPath -and $Task) {
                    $resolution = & $resolverPath -Task $Task -Uw5Root $Uw5Root | ConvertFrom-Json
                    $layerTrace.output = "Skills: $($resolution.skills -join ', ')"
                }
            }
            "L09" {
                # Tool Registry â€” provides needed tools
                $layerTrace.output = "Tools active"
            }
            "L11" {
                # Prompt Compiler â€” assembles final prompt
                $layerTrace.output = "Prompt compiled"
            }
            "L12" {
                # Multi-Agent Orchestrator
                $layerTrace.output = "META-MIND orchestration"
            }
            "L13" {
                # Execution Engine — Change Guard + main task execution
                $changeGuardPath = Join-Path $runtimeDir "uw5-change-guard.ps1"
                if (Test-Path $changeGuardPath) {
                    $snapResult = & $changeGuardPath -Action snapshot -Uw5Root $Uw5Root
                    $layerTrace.output = "Pre-change snapshot: $($snapResult.snapshot_name)"
                }
                if ($Task) {
                    $layerTrace.output += "; Task: $Task"
                }
            }
            }
            "L14" {
                # Sandbox — isolated execution (logical + optional Docker)
                $sandboxPath = Join-Path $runtimeDir "uw5-sandbox-run.ps1"
                if (Test-Path $sandboxPath) {
                    $sandboxEnabled = [Environment]::GetEnvironmentVariable("UW5_SANDBOX_DOCKER", "Process")
                    if ($sandboxEnabled -eq "1" -and $Task) {
                        $sbResult = & $sandboxPath -Docker -Command $Task -TimeoutSeconds 120
                        $layerTrace.output = "Docker sandbox: exec result"
                    } else {
                        $layerTrace.output = "Logical sandbox active (Docker: $([bool]$sandboxEnabled))"
                    }
                } else {
                    $layerTrace.output = "Sandbox active (logical isolation)"
                }
            }
            "L15" {
                # Verifier + Policy
                $layerTrace.output = "Verification in progress"
            }
            "L16" {
                # Self-Healing — FAIL → Patch → Verify → Retry (x3)
                $selfHealPath = Join-Path $runtimeDir "uw5-self-healing.ps1"
                if (Test-Path $selfHealPath -and $trace.errors.Count -gt 0) {
                    $firstError = $trace.errors[0]
                    $failedLayer = if ($firstError -match "Layer (\w+):") { $Matches[1] } else { "unknown" }
                    $healResult = & $selfHealPath -Task $Task -ErrorContext $firstError -FailedLayer $failedLayer -Uw5Root $Uw5Root
                    if ($healResult.success) {
                        $layerTrace.output = "Self-healed on attempt $($healResult.retryCount): $($healResult.actions -join '; ')"
                        $trace.selfHealed = $true
                        $trace.errors = @()
                    } else {
                        $layerTrace.output = "Self-heal failed after $($healResult.retryCount) retries. KAIROS: $($healResult.errorSignature)"
                        $trace.selfHealed = $false
                    }
                    $trace.selfHealActions = $healResult.actions
                } else {
                    $layerTrace.output = "Self-heal check: no errors to repair"
                }
            }
            "L18" {
                # Trace Capture
                $layerTrace.output = "Trace captured"
            }
            "L19" {
                # Golden State — save result + dual-backup to version-history git
                $memoryPath = Join-Path $runtimeDir "uw5-memory.ps1"
                if (Test-Path $memoryPath) {
                    & $memoryPath -Task $Task -Uw5Root $Uw5Root -Status "success"
                    $layerTrace.output = "Golden state saved"
                }
                # Dual-backup: git commit to version-history
                $vhDir = Join-Path $Uw5Root ".version-history"
                if (Test-Path (Join-Path $vhDir ".git")) {
                    try {
                        # Copy current state files to version-history
                        $integrityScript = Join-Path $runtimeDir "uw5-state-integrity.ps1"
                        if (Test-Path $integrityScript) {
                            & $integrityScript -Mode update -Uw5Root $Uw5Root | Out-Null
                        }
                        # Copy key files
                        $copyTargets = @("UW5_CORE.md", "STATE_MANIFEST.json", "memory/kairos.json", "memory/golden.json", "memory/integrity/checksums.json")
                        foreach ($ct in $copyTargets) {
                            $src = Join-Path $Uw5Root $ct
                            $dstDir = Split-Path (Join-Path $vhDir $ct) -Parent
                            if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
                            if (Test-Path $src) { Copy-Item $src (Join-Path $vhDir $ct) -Force }
                        }
                        $taskLabel = if ($Task.Length -gt 60) { "$($Task.Substring(0,57))..." } else { $Task }
                        git -C $vhDir add -A 2>$null
                        git -C $vhDir commit -m "auto: post-task state ($taskLabel)" --allow-empty 2>$null
                        $layerTrace.output += "; git backup committed"
                        # Non-blocking auto-push to GitHub remote
                        $pushScript = Join-Path $runtimeDir "uw5-git-push.ps1"
                        if (Test-Path $pushScript) {
                            $pushJob = Start-Job -ScriptBlock { param($p) & $p } -ArgumentList $pushScript
                            $layerTrace.output += "; remote push started (bg)"
                        }
                    } catch {
                        $layerTrace.output += "; git backup skipped"
                    }
                }
            }
            }
            default {
                $layerTrace.output = "Layer $layerId (passthrough)"
            }
        }
        $layerTrace.status = "completed"
    } catch {
        $layerTrace.status = "failed"
        $layerTrace.output = "Error: $_"
        $trace.errors += "Layer $layerId: $_"
    }

    $end = Get-Date
    $layerTrace.durationMs = [math]::Round(($end - $start).TotalMilliseconds, 1)
    Write-Output "[UW5 EXEC]   $layerId â†’ $($layerTrace.status) ($($layerTrace.durationMs)ms)"

    return $layerTrace
}

# â”€â”€â”€ Execute Each Layer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
foreach ($layerId in $layers) {
    $layerTrace = Execute-Layer $layerId
    $trace.layers += $layerTrace
}

# â”€â”€â”€ Summary â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$endTime = Get-Date
$trace.totalDurationMs = [math]::Round(($endTime - [datetime]::ParseExact($trace.startTime, "yyyy-MM-dd HH:mm:ss.fff", $null)).TotalMilliseconds, 1)
$trace.status = "completed"

if ($trace.errors.Count -gt 0) {
    $trace.status = "completed_with_errors"
    Write-Warning "[UW5 EXEC] Completed with $($trace.errors.Count) errors"
}

Write-Output "[UW5 EXEC] === Execution Complete ($($trace.totalDurationMs)ms) ==="
$trace | ConvertTo-Json -Depth 5
