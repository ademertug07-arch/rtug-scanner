# UW5 v5 Visual Core â€” Status API & HUD Engine
# GÃ¶rev: UW5 gÃ¶rsel durumunu oku, JSON Ã§Ä±ktÄ± Ã¼ret, boot'a entegre ol

param(
    [string]$Mode = "status",
    [string]$Uw5Root = ""
)

# â”€â”€â”€ Path Resolver â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
    if (-not (Test-Path (Join-Path $Uw5Root "UW5_CORE.md")) -and -not (Test-Path (Join-Path $Uw5Root "config\uw5.json"))) {
        $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
        if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $Uw5Root = $resolved } }
    }
}

$visualDir = Join-Path $Uw5Root "visual"
$memoryDir = Join-Path $Uw5Root "memory"
$visualStatePath = Join-Path $memoryDir "visual-state.json"

# â”€â”€â”€ Config Load â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Load-VisualConfig {
    param([string]$Name)
    $path = Join-Path $visualDir "$Name.json"
    if (Test-Path $path) {
        try { return Get-Content $path -Raw | ConvertFrom-Json } catch { return $null }
    }
    return $null
}

# â”€â”€â”€ Mode: load (boot entegrasyonu) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Invoke-VisualLoad {
    $theme = Load-VisualConfig "theme"
    $colors = Load-VisualConfig "colors"
    $hud = Load-VisualConfig "hud"
    $overlay = Load-VisualConfig "overlay"

    $result = @{
        visual = @{
            theme_loaded = ($theme -ne $null)
            colors_loaded = ($colors -ne $null)
            hud_loaded = ($hud -ne $null)
            overlay_loaded = ($overlay -ne $null)
        }
        status = "initialized"
    }

    # Save visual state to memory
    $visualState = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        theme = if ($theme) { $theme.theme } else { "unknown" }
        hud_enabled = if ($hud) { $hud.hud.enabled } else { $false }
        overlay_enabled = if ($overlay) { $overlay.overlay.enabled } else { $false }
        boot_screen = if ($overlay) { $overlay.boot_screen.enabled } else { $false }
        status = "active"
    }
    $visualState | ConvertTo-Json | Set-Content $visualStatePath

    # Output boot messages
    Write-Output "[UW5 VISUAL] â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"
    Write-Output "[UW5 VISUAL]  Theme loaded: $($result.visual.theme_loaded)"
    Write-Output "[UW5 VISUAL]  Colors loaded: $($result.visual.colors_loaded)"
    Write-Output "[UW5 VISUAL]  HUD loaded: $($result.visual.hud_loaded)"
    Write-Output "[UW5 VISUAL]  Overlay loaded: $($result.visual.overlay_loaded)"
    Write-Output "[UW5 VISUAL]  Status monitor active"
    Write-Output "[UW5 VISUAL] â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"

    return $result
}

# â”€â”€â”€ Mode: status (runtime API) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Invoke-VisualStatus {
    # Read current visual state
    $visualState = @{}
    if (Test-Path $visualStatePath) {
        try { $visualState = Get-Content $visualStatePath -Raw | ConvertFrom-Json } catch {}
    }

    # Read pipeline/memory state from runtime context if available
    $pipelineState = "idle"
    $activeLayer = "L00"
    try {
        $runtimeStatePath = Join-Path $Uw5Root "recovery\runtime-state.json"
        if (Test-Path $runtimeStatePath) {
            $runtime = Get-Content $runtimeStatePath -Raw | ConvertFrom-Json
            $pipelineState = if ($runtime.pipeline) { $runtime.pipeline } else { "idle" }
            $activeLayer = if ($runtime.currentLayer) { $runtime.currentLayer } else { "L00" }
        }
    } catch {}

    # Read memory status
    $memoryStatus = "HEALTHY"
    $kairosPath = Join-Path $Uw5Root "memory\kairos.json"
    if (-not (Test-Path $kairosPath)) { $memoryStatus = "INITIALIZING" }

    # Build status JSON
    $status = @{
        uw5 = if ($visualState.status) { $visualState.status } else { "initializing" }
        pipeline = $pipelineState
        layer = $activeLayer
        agent = "universal-architect"
        model = "balanced"
        memory = $memoryStatus
        exec_time = "0.0s"
        tokens = 0
        self_heal = "STANDBY"
        optimization = "IDLE"
        route = 0
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }

    return $status
}

# â”€â”€â”€ Mode: display (HUD string) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Invoke-VisualDisplay {
    $status = Invoke-VisualStatus
    $hud = Load-VisualConfig "hud"

    $output = @"
 â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•-
 â•‘     â¬¡ UW5 v5 â€” AI CIVILIZATION OS      â•‘
 â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
 â•‘  ROUTE     $($status.route.ToString().PadRight(5))  LAYER  $($status.layer.PadRight(6))    â•‘
 â•‘  PIPELINE  $($status.pipeline.PadRight(5))  AGENT  $($status.agent.PadRight(12)) â•‘
 â•‘  MODEL     $($status.model.PadRight(5))  MEM    $($status.memory.PadRight(6))    â•‘
 â•‘  TIME      $($status.exec_time.PadRight(5))  TOKENS $($status.tokens.ToString().PadRight(6)) â•‘
 â•‘  SELF HEAL $($status.self_heal.PadRight(5))  OPT    $($status.optimization.PadRight(6))     â•‘
 â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"@
    return $output
}

# â”€â”€â”€ Router â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
switch ($Mode.ToLower()) {
    "load" {
        $result = Invoke-VisualLoad
        return $result
    }
    "status" {
        return Invoke-VisualStatus
    }
    "display" {
        return Invoke-VisualDisplay
    }
    default {
        Write-Error "[UW5 VISUAL] Unknown mode: $Mode"
        Write-Error "[UW5 VISUAL] Modes: load, status, display"
        exit 1
    }
}
