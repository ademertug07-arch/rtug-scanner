# UW5 v5 Pipeline Router
# GÃ¶rev: Resolver Ã§Ä±ktÄ±sÄ±na gÃ¶re pipeline/*.json'dan katman listesini seÃ§

param(
    [string]$PipelineName = "",
    [string]$Uw5Root = "",
    [string]$Task = ""
)

if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
    if (-not (Test-Path (Join-Path $Uw5Root "UW5_CORE.md")) -and -not (Test-Path (Join-Path $Uw5Root "config\uw5.json"))) {
        $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
        if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $Uw5Root = $resolved } }
    }
}
$pipelineDir = Join-Path $Uw5Root "pipeline"

# â”€â”€â”€ Auto-detect pipeline from task if not specified â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if ((-not $PipelineName) -and $Task) {
    $resolverPath = Join-Path $Uw5Root "runtime\uw5-resolver.ps1"
    if (Test-Path $resolverPath) {
        $resolution = & $resolverPath -Task $Task -Uw5Root $Uw5Root | ConvertFrom-Json
        $PipelineName = $resolution.pipeline
    }
}

if (-not $PipelineName) { $PipelineName = "full" }
if ($PipelineName -notin @("fast","full","deep")) { $PipelineName = "full" }

$pipelineFile = Join-Path $pipelineDir "$PipelineName.json"

# â”€â”€â”€ Load Pipeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if (Test-Path $pipelineFile) {
    $pipeline = Get-Content $pipelineFile -Raw | ConvertFrom-Json
    $layers = @()
    foreach ($layer in $pipeline.layers) {
        $layers += @{
            id = $layer.id
            name = $layer.name
            description = if ($layer.description) { $layer.description } else { "" }
        }
    }

    $result = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        pipelineName = $PipelineName
        file = $pipelineFile
        description = $pipeline.description
        route = $pipeline.routes
        layerCount = $layers.Count
        layers = $layers
        layerIds = $layers.id
    }

    Write-Output "[UW5 ROUTER] Pipeline: $PipelineName ($($layers.Count) layers)"
    Write-Output "[UW5 ROUTER] Layers: $($layers.id -join ' â†’ ')"

    $result | ConvertTo-Json -Depth 5
} else {
    Write-Error "[UW5 ROUTER] Pipeline file not found: $pipelineFile"
    return @{
        error = "Pipeline not found: $PipelineName"
        pipelineName = $PipelineName
        layers = @()
        layerIds = @()
    } | ConvertTo-Json -Depth 3
}
