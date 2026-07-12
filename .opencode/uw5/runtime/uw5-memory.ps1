# UW5 v5 Memory Engine
# GÃ¶rev: BaÅŸarÄ±lÄ± Ã§Ã¶zÃ¼mleri ve hatalarÄ± KAIROS + Golden state'e kaydet

param(
    [string]$Task = "",
    [string]$Uw5Root = "",
    [string]$Status = "success",
    [string]$ErrorSignature = "",
    [string]$Agent = "",
    [string]$Model = "",
    [string]$Resolution = ""
)

if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
    if (-not (Test-Path (Join-Path $Uw5Root "UW5_CORE.md")) -and -not (Test-Path (Join-Path $Uw5Root "config\uw5.json"))) {
        $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
        if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $Uw5Root = $resolved } }
    }
}
$memoryDir = Join-Path $Uw5Root "memory"

# â”€â”€â”€ Ensure memory directories exist â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$kairosDir = Join-Path $memoryDir "kairos"
$goldenDir = Join-Path $memoryDir "golden"
New-Item -ItemType Directory -Path $kairosDir -Force | Out-Null
New-Item -ItemType Directory -Path $goldenDir -Force | Out-Null

# â”€â”€â”€ KAIROS Record â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$kairosRecord = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    task = $Task
    status = $Status
    agent = $Agent
    model = $Model
    errorSignature = $ErrorSignature
    resolution = $Resolution
}

$kairosFile = Join-Path $kairosDir "$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$kairosRecord | ConvertTo-Json | Set-Content $kairosFile
Write-Output "[UW5 MEMORY] KAIROS saved: $kairosFile"

# â”€â”€â”€ Golden State â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$goldenState = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    task = $Task
    status = $Status
    agent = $Agent
    model = $Model
    pipelineResult = $Resolution
}

$goldenFile = Join-Path $goldenDir "golden-state.json"
$goldenState | ConvertTo-Json | Set-Content $goldenFile
Write-Output "[UW5 MEMORY] Golden state saved: $goldenFile"

# â”€â”€â”€ Rotate KAIROS (keep last 100) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$allKairos = Get-ChildItem $kairosDir -Filter "*.json" | Sort-Object LastWriteTime -Descending
if ($allKairos.Count -gt 100) {
    $allKairos | Select-Object -Skip 100 | Remove-Item -Force
    Write-Output "[UW5 MEMORY] KAIROS rotation: kept last 100"
}

# â”€â”€â”€ Return â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@{
    saved = $true
    kairos = $kairosFile
    golden = $goldenFile
    timestamp = $kairosRecord.timestamp
} | ConvertTo-Json
