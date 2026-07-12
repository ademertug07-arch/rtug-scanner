# UW5 v5 Docker Sandbox Runner
# L14 alt-mekanizma: mevcut mantıksal izolasyonu Docker container ile genişlet
# Çağrı: ./uw5-sandbox-run.ps1 -Command "python3 script.py"
# Varsayılan: mantıksal izolasyon (Docker yoksa)
# Docker modu: ./uw5-sandbox-run.ps1 -Docker -Command "..."

param(
    [string]$Command = "",
    [switch]$Docker,
    [string]$WorkDir = "",
    [int]$TimeoutSeconds = 60
)

$uw5Root = Split-Path -Parent $PSScriptRoot

if ($Docker) {
    # Docker container sandbox modu
    $dockerOk = $false
    try {
        $version = docker version --format "{{.Server.Version}}" 2>$null
        if ($version) { $dockerOk = $true }
    } catch {}

    if (-not $dockerOk) {
        Write-Warning "[UW5 SANDBOX] Docker daemon unavailable. Install Docker Desktop and start it."
        Write-Warning "[UW5 SANDBOX] Falling back to logical isolation."
        $Docker = $false
    } else {
        # Ensure image exists
        $imageExists = docker images -q uw5-sandbox 2>$null
        if (-not $imageExists) {
            Write-Host "[UW5 SANDBOX] Building uw5-sandbox image..."
            $buildResult = docker build -t uw5-sandbox -f (Join-Path $uw5Root "sandbox\Dockerfile") $uw5Root 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "[UW5 SANDBOX] Image build failed. Falling back."
                $Docker = $false
            }
        }
    }
}

if ($Docker) {
    # Docker sandbox execution
    $mountDir = if ($WorkDir) { $WorkDir } else { $uw5Root }
    $containerName = "uw5-sandbox-$(Get-Random -Maximum 99999)"
    
    Write-Host "[UW5 SANDBOX] Running in Docker container..."
    $result = docker run --rm `
        --name $containerName `
        -v "${mountDir}:/workspace" `
        -w /workspace `
        --network none `
        --memory 2g `
        --cpus 2 `
        --stop-timeout $TimeoutSeconds `
        uw5-sandbox `
        pwsh -NoLogo -NoProfile -Command $Command 2>&1
    
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-Host "[UW5 SANDBOX] Docker execution OK (exit $exitCode)"
    } else {
        Write-Warning "[UW5 SANDBOX] Docker execution exit code: $exitCode"
    }
    return $result
} else {
    # Varsayılan mantıksal izolasyon (PATH/session bazlı)
    if ($Command) {
        try {
            $result = Invoke-Expression $Command 2>&1
            return $result
        } catch {
            Write-Warning "[UW5 SANDBOX] Execution error: $_"
            return $null
        }
    }
}
