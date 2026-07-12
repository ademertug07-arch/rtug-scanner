# UW5 v5 Health Monitor
# GÃ¶rev: CPU, RAM, session durumu, hata oranÄ±, runtime durumu takibi

param(
    [string]$Mode = "full"  # quick, full
)

# â”€â”€â”€ System Metrics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$health = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    status = "healthy"
    metrics = @{}
    warnings = @()
}

# â”€â”€â”€ DB Health â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try {
    $dbDir = "$env:USERPROFILE\.local\share\opencode"
    $dbPath = Join-Path $dbDir "opencode.db"
    $walPath = Join-Path $dbDir "opencode.db-wal"
    if (Test-Path $dbPath) {
        $dbSizeMB = [math]::Round((Get-Item $dbPath).Length / 1MB, 1)
        $walSizeMB = 0
        if (Test-Path $walPath) { $walSizeMB = [math]::Round((Get-Item $walPath).Length / 1MB, 1) }
        $health.metrics.dbSizeMB = $dbSizeMB
        $health.metrics.dbWalSizeMB = $walSizeMB
        if ($walSizeMB -gt 100) {
            $health.warnings += "Large WAL: $walSizeMB MB - checkpoint recommended"
        }
    } else {
        $health.metrics.dbSizeMB = "not_found"
    }
} catch {
    $health.metrics.dbSizeMB = "unknown"
}

# â”€â”€â”€ CPU Usage â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try {
    $cpu = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average
    $health.metrics.cpuPercent = [math]::Round($cpu.Average, 1)
} catch {
    $health.metrics.cpuPercent = "unknown"
}

# â”€â”€â”€ RAM Usage â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try {
    $os = Get-CimInstance Win32_OperatingSystem
    $usedGB = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 1)
    $totalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
    $pct = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize * 100, 1)
    $health.metrics.ramGB = "$usedGB/$totalGB"
    $health.metrics.ramPercent = $pct
} catch {
    $health.metrics.ramGB = "unknown"
}

# â”€â”€â”€ GPU / VRAM Usage (nvidia-smi based) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try {
    $gpuRaw = nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader,nounits 2>$null
    if ($gpuRaw) {
        $gpuParts = $gpuRaw -split ', '
        if ($gpuParts.Count -ge 3) {
            $gpuName = $gpuParts[0]
            $vramUsed = [int]$gpuParts[1]
            $vramTotal = [int]$gpuParts[2]
            $vramPct = [math]::Round($vramUsed / $vramTotal * 100, 1)
            $health.metrics.gpuName = $gpuName
            $health.metrics.vramUsedMB = $vramUsed
            $health.metrics.vramTotalMB = $vramTotal
            $health.metrics.vramPercent = $vramPct

            # VRAM threshold check: >90% triggers fallback
            if ($vramPct -gt 90) {
                $health.warnings += "VRAM CRITICAL: ${vramPct}% ($vramUsed/$vramTotal MB) — LOCAL/OFFLINE tiers restricted"
                [Environment]::SetEnvironmentVariable("UW5_VRAM_CRITICAL", "1", "Process")
                $health.metrics.vramFallback = "LOCAL/OFFLINE tiers auto-restricted"
            } elseif ($vramPct -gt 80) {
                $health.warnings += "VRAM high: ${vramPct}% ($vramUsed/$vramTotal MB)"
                $health.metrics.vramFallback = "monitoring"
            } else {
                [Environment]::SetEnvironmentVariable("UW5_VRAM_CRITICAL", "0", "Process")
                $health.metrics.vramFallback = "normal"
            }
        } else {
            $health.metrics.gpuName = "nvidia-smi parsed incorrectly"
        }
    } else {
        $health.metrics.gpuName = "nvidia-smi_unavailable"
    }
} catch {
    $health.metrics.gpuName = "nvidia-smi_error"
}

# â”€â”€â”€ Warnings â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if ($health.metrics.cpuPercent -ne "unknown" -and $health.metrics.cpuPercent -gt 80) {
    $health.warnings += "CPU high: $($health.metrics.cpuPercent)%"
}
if ($health.metrics.ramPercent -ne $null -and $health.metrics.ramPercent -gt 85) {
    $health.warnings += "RAM high: $($health.metrics.ramPercent)%"
}

if ($health.warnings.Count -gt 0) {
    $health.status = "degraded"
}

if ($Mode -eq "quick") {
    $gpuInfo = if ($health.metrics.gpuName -and $health.metrics.gpuName -ne "nvidia-smi_unavailable") {
        "$($health.metrics.gpuName) VRAM: $($health.metrics.vramPercent)%"
    } else { "n/a" }
    $health.metrics = @{
        cpu = $health.metrics.cpuPercent
        ram = $health.metrics.ramGB
        gpu = $gpuInfo
        db = $health.metrics.dbSizeMB
        dbwal = $health.metrics.dbWalSizeMB
        status = $health.status
    }
}

$gpuLine = if ($health.metrics.gpuName -and $health.metrics.gpuName -ne "nvidia-smi_unavailable") {
    " | GPU: $($health.metrics.gpuName) $($health.metrics.vramPercent)% ($($health.metrics.vramUsedMB)/$($health.metrics.vramTotalMB) MB)"
} else { "" }
Write-Output "[HEALTH] Status: $($health.status) | CPU: $($health.metrics.cpuPercent)% | RAM: $($health.metrics.ramGB)$gpuLine"

$health | ConvertTo-Json -Depth 3
