# UW5 v5 Context Guard
# GÃ¶rev: Context bÃ¼yÃ¼klÃ¼ÄŸÃ¼ takip, otomatik Ã¶zetleme, gereksiz veri temizleme

param(
    [string]$Mode = "check",  # check, compact, clean
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

# â”€â”€â”€ Context State File â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$contextDir = Join-Path $Uw5Root "runtime\.context"
New-Item -ItemType Directory -Path $contextDir -Force | Out-Null
$stateFile = Join-Path $contextDir "context-state.json"

# â”€â”€â”€ Load or Init State â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if (Test-Path $stateFile) {
    $state = Get-Content $stateFile -Raw | ConvertFrom-Json
} else {
    $state = @{
        turnCount = 0
        estimatedTokens = 0
        lastCompact = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        compactCount = 0
    }
}

# â”€â”€â”€ Mode: check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if ($Mode -eq "check") {
    $state.turnCount++
    # Simulate token estimation based on turn count
    $state.estimatedTokens = $state.turnCount * 1500  # rough estimate

    $result = @{
        turnCount = $state.turnCount
        estimatedTokens = $state.estimatedTokens
        needsCompact = $state.turnCount -ge 10 -or $state.estimatedTokens -ge 15000
        lastCompact = $state.lastCompact
        compactCount = $state.compactCount
    }

    Write-Output "[CONTEXT GUARD] Turns: $($state.turnCount) | Tokens: ~$($state.estimatedTokens)K"
    if ($result.needsCompact) {
        Write-Output "[CONTEXT GUARD] âš  Compact recommended (10+ turns or 15K+ tokens)"
    }

    $state | ConvertTo-Json | Set-Content $stateFile
    return $result | ConvertTo-Json
}

# â”€â”€â”€ Mode: compact â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if ($Mode -eq "compact") {
    $state.turnCount = 5  # keep last 5 turns equivalent
    $state.estimatedTokens = 5000
    $state.lastCompact = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $state.compactCount++
    $state | ConvertTo-Json | Set-Content $stateFile

    Write-Output "[CONTEXT GUARD] Compacted (count: $($state.compactCount))"
    return @{
        compacted = $true
        compactCount = $state.compactCount
        timestamp = $state.lastCompact
    } | ConvertTo-Json
}

# â”€â”€â”€ Mode: clean â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if ($Mode -eq "clean") {
    Remove-Item -Path "$contextDir\*" -Recurse -Force -ErrorAction SilentlyContinue
    $state = @{
        turnCount = 0
        estimatedTokens = 0
        lastCompact = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        compactCount = $state.compactCount
    }
    $state | ConvertTo-Json | Set-Content $stateFile
    Write-Output "[CONTEXT GUARD] Context cleaned"
    return @{ cleaned = $true } | ConvertTo-Json
}
