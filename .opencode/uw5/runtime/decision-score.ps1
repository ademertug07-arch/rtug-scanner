# UW5 v5 Decision Score Engine
# GÃ¶rev: SeÃ§imleri puanla, en yÃ¼ksek skoru seÃ§

param(
    [string]$Task = "",
    [string]$Uw5Root = ""
)

if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
    if (-not (Test-Path (Join-Path $Uw5Root "UW5_CORE.md")) -and -not (Test-Path (Join-Path $Uw5Root "config\uw5.json"))) {
        $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
        if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $Uw5Root = $resolved } }
    }
}

# â”€â”€â”€ Resolve task to get options â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$resolverPath = Join-Path $Uw5Root "runtime\uw5-resolver.ps1"
if (Test-Path $resolverPath) {
    $resolution = & $resolverPath -Task $Task -Uw5Root $Uw5Root | ConvertFrom-Json
}

# â”€â”€â”€ Scoring Weights â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$weights = @{
    skillMatch = 0.30
    agentMatch = 0.25
    modelMatch = 0.20
    pipelineMatch = 0.15
    domainScore = 0.10
}

# â”€â”€â”€ Calculate Scores â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$scores = @{}

# Domain match score
$scores.domainScore = [math]::Min($resolution.score / 100, 1.0)

# Skill count score (more specific skills = better match)
$skillCount = @($resolution.skills).Count
$scores.skillMatch = [math]::Min($skillCount * 0.2, 1.0)

# Agent match score
if ($resolution.agent) {
    $scores.agentMatch = 1.0  # resolver already picked best agent
} else {
    $scores.agentMatch = 0.5
}

# Model appropriateness
$modelQuality = @{
    "flash" = 0.6
    "balanced" = 0.8
    "deep" = 0.9
    "ultra" = 1.0
    "local" = 0.5
    "offline" = 0.3
}
$scores.modelMatch = $modelQuality[$resolution.model]

# Pipeline appropriateness
$pipelineQuality = @{
    "fast" = 0.6
    "full" = 0.9
    "deep" = 1.0
}
$scores.pipelineMatch = $pipelineQuality[$resolution.pipeline]

# â”€â”€â”€ Total Score â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$totalScore = 0
foreach ($key in $weights.Keys) {
    if ($scores.ContainsKey($key)) {
        $totalScore += $scores[$key] * $weights[$key]
    }
}
$totalScore = [math]::Round($totalScore * 100, 1)

# â”€â”€â”€ Output â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$result = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    task = $Task
    totalScore = $totalScore
    components = $scores
    weights = $weights
    selection = @{
        domain = $resolution.domain
        complexity = $resolution.complexity
        agent = $resolution.agent
        model = $resolution.model
        pipeline = $resolution.pipeline
        skills = $resolution.skills
    }
    threshold = 70.0
    passed = $totalScore -ge 70.0
}

Write-Output "[DECISION] Score: $totalScore% | Model: $($resolution.model) | Agent: $($resolution.agent) | Pipeline: $($resolution.pipeline)"
if ($result.passed) {
    Write-Output "[DECISION] âœ… Threshold met (70%)"
} else {
    Write-Warning "[DECISION] âš  Below threshold (70%)"
}

$result | ConvertTo-Json -Depth 4
