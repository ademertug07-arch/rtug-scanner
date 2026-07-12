# UW5 v5 Root Resolver
# Task: Dynamically locate .opencode/uw5/ directory. Self-contained.

param([string]$Hint = "")

# --- Search Strategy ---------------------------------------------------------
$searchPaths = @()

# 1. Environment variable override (User scope)
$envRoot = [Environment]::GetEnvironmentVariable("UW5_ROOT", "User")
if ($envRoot) { $searchPaths += $envRoot }

# 2. Environment variable override (Process scope)
$envRootProcess = [Environment]::GetEnvironmentVariable("UW5_ROOT", "Process")
if ($envRootProcess) { $searchPaths += $envRootProcess }

# 3. Hint path (explicit parameter or .opencode/uw5 under it)
if ($Hint -and (Test-Path $Hint)) {
    $searchPaths += $Hint
    $hintUw5 = Join-Path $Hint ".opencode\uw5"
    if (Test-Path $hintUw5) { $searchPaths += $hintUw5 }
}

# 4. Current working directory
$cwdUw5 = Join-Path (Get-Location) ".opencode\uw5"
$searchPaths += $cwdUw5

# 5. Walk up from PWD (search parent dirs, max 10 levels)
$current = Get-Location
for ($i = 0; $i -lt 10; $i++) {
    $testPath = Join-Path $current ".opencode\uw5"
    if (Test-Path $testPath) { $searchPaths += $testPath; break }
    $parent = Split-Path $current -Parent
    if ((-not $parent) -or ($parent -eq $current)) { break }
    $current = $parent
}

# 6. Config directory
$configUw5 = Join-Path $env:USERPROFILE ".config\opencode\.opencode\uw5"
$searchPaths += $configUw5

# 7. Desktop project (via .NET GetFolderPath to avoid encoding issues)
$desktopPath = [Environment]::GetFolderPath("Desktop")
if ($desktopPath) {
    $desktopUw5 = Join-Path $desktopPath "open code mode\.opencode\uw5"
    $searchPaths += $desktopUw5
}

# 8. WSL2 /mnt/c/ path (when called from within WSL2)
$wslLocalPath = "/mnt/c/Users/cagda/OneDrive/Masaüstü/open code mode/.opencode/uw5"
$searchPaths += $wslLocalPath

# 9. WSL2 UNC / network path via $env:WSLENV hints
$wslUbuntuHome = "/home/cagda/.opencode/uw5"
$searchPaths += $wslUbuntuHome

# --- Resolution --------------------------------------------------------------
$resolvedRoot = $null
$resolvedBy = ""

foreach ($path in $searchPaths) {
    if (-not $path) { continue }
    # Valid UW5 root: has UW5_CORE.md OR config/uw5.json
    $coreTest = Join-Path $path "UW5_CORE.md"
    $configTest = Join-Path $path "config\uw5.json"
    if ((Test-Path $coreTest) -or (Test-Path $configTest)) {
        $resolvedRoot = $path
        $resolvedBy = "found: $path"
        break
    }
    # Also check if this is a project root with .opencode/uw5 inside
    if (Test-Path (Join-Path $path ".opencode\uw5\UW5_CORE.md")) {
        $resolvedRoot = Join-Path $path ".opencode\uw5"
        $resolvedBy = "found: $resolvedRoot (nested)"
        break
    }
}

# --- Output ------------------------------------------------------------------
if ($resolvedRoot) {
    $resolvedRoot = $resolvedRoot -replace '\\$', ''
    Write-Output $resolvedRoot
    [Environment]::SetEnvironmentVariable("UW5_ROOT", $resolvedRoot, "Process")
    exit 0
} else {
    Write-Error "[UW5 ROOT] Cannot find .opencode/uw5/ directory"
    Write-Error "[UW5 ROOT] Searched:"
    foreach ($p in $searchPaths) {
        if ($p) { Write-Error "  - $p" }
    }
    exit 1
}
