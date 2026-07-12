# UW5 v5 WSL2 Bridge
# Task: Execute commands inside WSL2 (Ubuntu) when WSL2 provides perf/stability advantage
# Usage:
#   .\uw5-wsl2.ps1 -Command "python3 script.py"
#   .\uw5-wsl2.ps1 -PythonScript "runtime/uw5-retrieval.py" -Args ".opencode/uw5 \"query\" 3"

param(
    [string]$Command = "",
    [string]$PythonScript = "",
    [string]$Args = "",
    [string]$Distro = "Ubuntu"
)

$uw5Root = Split-Path -Parent $PSScriptRoot

if (-not $Command -and -not $PythonScript) {
    Write-Host "[UW5 WSL2] UW5 v5 WSL2 Bridge"
    Write-Host ""
    Write-Host "STATUS:"
    $wslStatus = wsl -d $Distro --status 2>&1
    Write-Host "  Distro: $Distro"
    Write-Host "  Status: $(wsl -l -v 2>&1 | Select-String $Distro)"
    
    # Check GPU
    $gpuInfo = wsl -d $Distro nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1
    Write-Host "  GPU: $gpuInfo"
    
    # Check Python
    $pyVer = wsl -d $Distro python3 --version 2>&1
    Write-Host "  Python: $pyVer"
    
    Write-Host ""
    Write-Host "USAGE:"
    Write-Host "  .\uw5-wsl2.ps1 -Command 'ollama list'"
    Write-Host "  .\uw5-wsl2.ps1 -PythonScript 'runtime/uw5-retrieval.py' -Args '.opencode/uw5 \"test\" 3'"
    Write-Host ""
    Write-Host "NOTE: Windows-native Ollama (PID $(@(Get-Process ollama* -ErrorAction SilentlyContinue).Id -join ', ')) is preferred over WSL2 Ollama."
    Write-Host "  GPU passthrough is identical in both environments (same RTX 4070)."
    Write-Host "  WSL2 lacks required Python ML packages (numpy) for retrieval scripts."
    exit 0
}

if ($Command) {
    wsl -d $Distro $Command 2>&1
    exit $LASTEXITCODE
}

if ($PythonScript) {
    $wslUw5Path = "/mnt/c/Users/cagda/OneDrive/Masaüstü/open code mode/.opencode/uw5"
    $wslScript = Join-Path $wslUw5Path $PythonScript
    $wslArgs = $Args
    wsl -d $Distro python3 "$wslScript" $wslArgs 2>&1
    exit $LASTEXITCODE
}
