<#
.SYNOPSIS
  UW5 v5 Retrieval Middleware - RAG context enrichment for LOCAL/OFFLINE tier
.DESCRIPTION
  L03/L04 sub-component: query_vector_index <task> returns tagged context chunks.
  Only for LOCAL and OFFLINE models (<200ms target).
  
  Returns:
    Enriched JSONObject with enrichedChunks, total_chunks, query_time_ms, tier
  
  Integration:
    uw5-resolver.ps1 calls this after L07 if tier=="local"/"offline"
#>

param(
    [string]$query = "",
    [int]$topK = 4,
    [float]$threshold = 0.25,
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

$result = @{
    enrichedChunks = @()
    total_chunks = 0
    query_time_ms = 0
    retrieval_active = $false
    tier = "local"
}

$pyScript = Join-Path $Uw5Root "runtime\uw5-retrieval.py"
$vectorDir = Join-Path $Uw5Root "memory\vector-index"
$indexFile = Join-Path $vectorDir "index.json"

if (-not (Test-Path $indexFile)) {
    Write-Verbose "[RETRIEVAL] Vector index not built yet"
    return $result
}

try {
    $startTime = Get-Date
    $jsonOutput = python $pyScript $Uw5Root $query $topK $threshold 2>&1 | Out-String
    
    $data = $jsonOutput | ConvertFrom-Json
    
    $result.enrichedChunks = $data.results
    $result.total_chunks = @($data.results).Count
    $result.query_time_ms = [math]::Round(((Get-Date) - $startTime).TotalMilliseconds, 1)
    $result.retrieval_active = $true
    
    if ($result.total_chunks -gt 0) {
        Write-Verbose "[RETRIEVAL] $($result.total_chunks) chunks found in $($result.query_time_ms)ms"
    }
} catch {
    Write-Warning "[RETRIEVAL] Error: $($_.Exception.Message)"
}

return $result
