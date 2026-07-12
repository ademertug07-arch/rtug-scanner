# UW5 v5 Backup System
# GÃ¶rev: .opencode/uw5/ klasÃ¶rÃ¼nÃ¼ snapshot'la, geri yÃ¼kle

param(
    [string]$Action = "backup",  # backup, list, restore
    [string]$Name = ""
)

$UW5_ROOT = Join-Path $PSScriptRoot ".." | Resolve-Path -ErrorAction SilentlyContinue
if (-not $UW5_ROOT -or -not (Test-Path (Join-Path $UW5_ROOT "UW5_CORE.md"))) {
    $resolver = Join-Path $PSScriptRoot "uw5-root-resolver.ps1"
    if (Test-Path $resolver) { $resolved = & $resolver; if ($LASTEXITCODE -eq 0) { $UW5_ROOT = $resolved } }
}
$SNAPSHOT_DIR = Join-Path $UW5_ROOT "..\..\.uw5-snapshots" | Resolve-Path -ErrorAction SilentlyContinue
if (-not $SNAPSHOT_DIR) {
    $SNAPSHOT_DIR = Join-Path $PSScriptRoot "..\..\..\.uw5-snapshots"
}
New-Item -ItemType Directory -Path $SNAPSHOT_DIR -Force | Out-Null

function Backup-UW5 {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $name = if ($Name) { $Name } else { "uw5-backup-$timestamp" }
    $target = Join-Path $SNAPSHOT_DIR $name
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Copy-Item -Recurse "$UW5_ROOT\*" "$target\" -Force
    Write-Output "[UW5 BACKUP] Saved: $target"

    # Keep last 10
    $backups = Get-ChildItem $SNAPSHOT_DIR -Directory | Where-Object { $_.Name -like "uw5-backup-*" } | Sort-Object LastWriteTime -Descending
    if ($backups.Count -gt 10) {
        $backups | Select-Object -Skip 10 | Remove-Item -Recurse -Force
        Write-Output "[UW5 BACKUP] Pruned: kept last 10"
    }
    return $target
}

function List-Backups {
    Get-ChildItem $SNAPSHOT_DIR -Directory | Where-Object { $_.Name -like "uw5-backup-*" } | Sort-Object LastWriteTime -Descending | ForEach-Object {
        Write-Output "$($_.Name) â€” $($_.LastWriteTime)"
    }
}

function Restore-UW5 {
    if (-not $Name) {
        $backups = Get-ChildItem $SNAPSHOT_DIR -Directory | Where-Object { $_.Name -like "uw5-backup-*" } | Sort-Object LastWriteTime -Descending
        if ($backups.Count -eq 0) { Write-Error "No backups found"; return }
        $Name = $backups[0].Name
    }
    $source = Join-Path $SNAPSHOT_DIR $Name
    if (-not (Test-Path $source)) { Write-Error "Backup not found: $Name"; return }

    # Clear current and restore
    Remove-Item "$UW5_ROOT\*" -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item -Recurse "$source\*" "$UW5_ROOT\" -Force
    Write-Output "[UW5 BACKUP] Restored: $Name"
}

switch ($Action) {
    "backup" { Backup-UW5 }
    "list" { List-Backups }
    "restore" { Restore-UW5 }
    default { Write-Error "Unknown action: $Action" }
}
