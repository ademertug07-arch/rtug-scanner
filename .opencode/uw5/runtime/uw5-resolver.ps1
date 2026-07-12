# UW5 v5 Capability Resolver
# GÃ¶rev: KullanÄ±cÄ± isteÄŸini analiz et, domain/kompleksite/skill/MCP/LSP/agent/model/pipeline seÃ§

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
$registryDir = Join-Path $Uw5Root "registry"

# â”€â”€â”€ Helper: Load Registry JSON â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Load-Registry($name) {
    $path = Join-Path $registryDir "$name.json"
    if (Test-Path $path) {
        return Get-Content $path -Raw | ConvertFrom-Json
    }
    return $null
}

# â”€â”€â”€ 1. Intent Analysis â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$taskLower = $Task.ToLower()

# Domain detection via capabilities.json
$capabilities = Load-Registry "capabilities"
$matchedDomain = $null
$bestScore = 0

if ($capabilities -and $capabilities.domains) {
    $domainNames = $capabilities.domains.PSObject.Properties.Name
    foreach ($dName in $domainNames) {
        $domain = $capabilities.domains.$dName
        $score = 0
        foreach ($kw in $domain.keywords) {
            if ($taskLower -match [regex]::Escape($kw.ToLower())) {
                $score += 10
            }
        }
        if ($score -gt $bestScore) {
            $bestScore = $score
            $matchedDomain = $dName
        }
    }
}

if (-not $matchedDomain) { $matchedDomain = "general" }
$domain = $capabilities.domains.$matchedDomain

# â”€â”€â”€ 2. Complexity Detection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$complexity = "medium"
if ($taskLower.Split(' ').Count -lt 5) {
    $complexity = "simple"
} elseif ($taskLower.Split(' ').Count -gt 30) {
    $complexity = "complex"
}
if ($taskLower -match "critical|urgent|production|security|exploit") {
    $complexity = "critical"
}

# â”€â”€â”€ 3. Load Registries for Selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$skillsReg = Load-Registry "skills"
$mcpReg = Load-Registry "mcp"
$lspReg = Load-Registry "lsp"
$pluginsReg = Load-Registry "plugins"
$agentsReg = Load-Registry "agents"
$modelsReg = Load-Registry "models"

# â”€â”€â”€ 4. Skill Selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$selectedSkills = @()
if ($domain.skills) {
    $selectedSkills = @($domain.skills)
}

# â”€â”€â”€ 5. MCP Selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$selectedMcp = @()
if ($domain.mcp) {
    $selectedMcp = @($domain.mcp)
}

# â”€â”€â”€ 6. LSP Selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$selectedLsp = $null
if ($domain.lsp) {
    $selectedLsp = $domain.lsp
}

# â”€â”€â”€ 7. Plugin Selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$selectedPlugins = @()
if ($domain.plugins) {
    $selectedPlugins = @($domain.plugins)
}

# â”€â”€â”€ 8. Agent Selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$selectedAgent = $domain.agent

# â”€â”€â”€ 9. Model Selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$selectedModel = $domain.model
# Override model based on complexity
if ($complexity -eq "simple") { $selectedModel = "flash" }
elseif ($complexity -eq "complex") { $selectedModel = "deep" }
elseif ($complexity -eq "critical") { $selectedModel = "ultra" }

# VRAM-aware model fallback: if VRAM is critical (>90%), override LOCAL/OFFLINE to flash
$vramCritical = [Environment]::GetEnvironmentVariable("UW5_VRAM_CRITICAL", "Process")
if ($vramCritical -eq "1" -and $selectedModel -in @("local", "offline")) {
    Write-Warning "[RESOLVER] VRAM CRITICAL: Overriding $selectedModel -> flash (cloud tier)"
    $selectedModel = "flash"
}

# â”€â”€â”€ 9b. RAG Enrichment (LOCAL/OFFLINE tier only) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$enrichedChunks = @()
if ($selectedModel -in @("local", "offline")) {
    $retrievalScript = Join-Path $PSScriptRoot "uw5-retrieval.ps1"
    if (Test-Path $retrievalScript) {
        try {
            $retrievalResult = & $retrievalScript -query $Task -topK 4 -threshold 0.25
            if ($retrievalResult.retrieval_active -and $retrievalResult.total_chunks -gt 0) {
                $enrichedChunks = $retrievalResult.enrichedChunks
                Write-Verbose "[RESOLVER] RAG: $($retrievalResult.total_chunks) chunks in $($retrievalResult.query_time_ms)ms"
            }
        } catch {
            Write-Warning "[RESOLVER] RAG retrieval failed: $_"
        }
    }
}

# â”€â”€â”€ 10. Pipeline Selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$selectedPipeline = $domain.pipeline
# Complexity override
if ($complexity -eq "simple") { $selectedPipeline = "fast" }

# â”€â”€â”€ Output â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$result = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    task = $Task
    domain = $matchedDomain
    complexity = $complexity
    skills = $selectedSkills
    mcp = $selectedMcp
    lsp = $selectedLsp
    plugins = $selectedPlugins
    agent = $selectedAgent
    model = $selectedModel
    pipeline = $selectedPipeline
    score = $bestScore
    enrichedChunks = $enrichedChunks
    retrievalActive = ($enrichedChunks.Count -gt 0)
}

$result | ConvertTo-Json -Depth 3
