# UW5 Auto-Push — non-blocking, silent push to GitHub remote
# Call from executor.ps1 after each successful task (L19 dual-backup)

param(
    [string]$Branch = "master",
    [switch]$Force
)

$uw5Root = Split-Path -Parent $PSScriptRoot
$vhDir = Join-Path $uw5Root ".version-history"

if (-not (Test-Path $vhDir)) {
    Write-Warning "[UW5 PUSH] .version-history not found at $vhDir"
    exit 1
}

Push-Location $vhDir

# Verify remote exists
$remote = git remote -v 2>$null
if (-not $remote) {
    Write-Warning "[UW5 PUSH] No remote configured — skipping push"
    Pop-Location
    exit 0
}

# Push silently (non-blocking), catch failures
$pushArgs = @("push", "origin", $Branch)
if ($Force) { $pushArgs += "--force" }

try {
    $result = & git $pushArgs 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-Host "[UW5 PUSH] ✓ Remote sync OK: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    } else {
        # Silent failure — token may not have write permission yet
        Write-Warning "[UW5 PUSH] Sync skipped (remote $exitCode) — token permission?"
    }
} catch {
    Write-Warning "[UW5 PUSH] Sync error: $_"
}

# Prune stale remote-tracking branches
try { & git remote prune origin 2>$null } catch {}

Pop-Location
exit 0
