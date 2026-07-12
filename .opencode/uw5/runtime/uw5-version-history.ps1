<#
.SYNOPSIS
  UW5 v5 Version History - non-blocking git-based change tracking
.DESCRIPTION
  Auto-commits critical UW5 file changes to .opencode/uw5/.version-history/ git repo.
  Separate git repo (does not affect main UW5 repo).
  Non-blocking via Start-Job - does not slow the pipeline.
  
  Parameters:
    -Action: "commit" (commit changes) | "init" (setup repo) | "status" (show state)
    -Message: commit message (for Action=commit)
    -Uw5Root: UW5 root path
#>

param(
    [string]$Action = "commit",
    [string]$Message = "",
    [string]$Uw5Root = ""
)

# --- Path Resolution ---------------------------------------------------------
if (-not $Uw5Root) {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $Uw5Root = $scriptRoot
}
$versionDir = Join-Path $Uw5Root ".version-history"

# --- Ensure git is available -------------------------------------------------
$gitAvailable = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitAvailable) {
    return @{ success=$false; error="git not available - version history disabled" }
}

# --- Init: Create git repo ---------------------------------------------------
if ($Action -eq "init") {
    if (-not (Test-Path $versionDir)) { New-Item -ItemType Directory -Path $versionDir -Force | Out-Null }
    
    git -C $versionDir init 2>$null | Out-Null
    git -C $versionDir config core.autocrlf true 2>$null
    git -C $versionDir config user.name "UW5 v5 Auto" 2>$null
    git -C $versionDir config user.email "uw5@opencode.local" 2>$null
    
    # .gitignore - only track critical UW5 files
    @"
/STATE_MANIFEST.json
/UW5_CORE.md
/config/uw5.json
/runtime/*.ps1
/runtime/*.py
/registry/*.json
/pipeline/*.json
/memory/*.json
/memory/vector-index/index.json
/memory/vector-index/documents.json
/memory/vector-index/vocab.json
/memory/integrity/*.json
/visual/*.json
/visual/*.md
"@ | Set-Content (Join-Path $versionDir ".gitignore") -Encoding UTF8
    
    # First commit
    git -C $versionDir add -A 2>$null
    git -C $versionDir commit -m "init: UW5 v5 version history" --allow-empty 2>$null | Out-Null
    
    Write-Host "[VERSION] Git version history initialized at $versionDir"
    return @{ success=$true; action="init"; path=$versionDir }
}

# --- Status: Show git log ----------------------------------------------------
if ($Action -eq "status") {
    if (-not (Test-Path (Join-Path $versionDir ".git"))) {
        return @{ success=$false; error="Version history not initialized - run with -Action init first" }
    }
    $log = git -C $versionDir log --oneline -20 2>$null
    $status = git -C $versionDir status --short 2>$null
    return @{ success=$true; action="status"; path=$versionDir; log=@($log); uncommitted=@($status) }
}

# --- Commit: Auto-commit changes (non-blocking) -----------------------------
if ($Action -eq "commit") {
    if (-not (Test-Path (Join-Path $versionDir ".git"))) {
        & $PSCommandPath -Action init -Uw5Root $Uw5Root | Out-Null
    }
    
    if (-not $Message) { $Message = "auto: state update $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" }
    
    # Use Start-Job for non-blocking operation
    $jobScript = {
        param($d, $m)
        $s = git -C $d status --short 2>$null
        if (-not $s) { return "no changes" }
        git -C $d add -A 2>$null
        git -C $d commit -m $m 2>$null
        return "committed: $m"
    }
    
    $job = Start-Job -ScriptBlock $jobScript -ArgumentList $versionDir, $Message
    
    return @{ success=$true; action="commit"; message=$Message; job_id=$job.Id; non_blocking=$true }
}

return @{ success=$false; error="Unknown action: $Action" }
