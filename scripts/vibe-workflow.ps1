param(
    [switch]$Init,
    [switch]$Check,
    [switch]$Log,
    [switch]$Handoff,
    [string]$Prompt = "",
    [string]$Goal = "",
    [string]$Scope = "",
    [string]$Feature = "",
    [string]$Bug = ""
)

$ErrorActionPreference = "Continue"
$wsRoot = Split-Path -Parent $PSScriptRoot
$logFile = "$wsRoot\prompt-log.md"

# ============================================
#  PROMPT LOG
# ============================================
function Add-PromptLog {
    param([string]$Prompt, [string]$Outcome = "pending", [string]$Tags = "")

    $entry = @"
## $(Get-Date -Format "yyyy-MM-dd HH:mm")
- **Prompt**: $Prompt
- **Outcome**: $Outcome
- **Tags**: $Tags
- **Status**: $(if ($Outcome -eq "done") { "✅" } else { "⏳" })

"@

    if (-not (Test-Path $logFile)) {
        "# Prompt Log`n`n" | Set-Content $logFile -Force
    }
    $existing = Get-Content $logFile -Raw -ErrorAction SilentlyContinue
    $entry + $existing | Set-Content $logFile -Force
    Write-Host "[VIBE] Prompt log'a kaydedildi: $Prompt" -ForegroundColor Green
}

# ============================================
#  CHECKLIST
# ============================================
function Show-Checklist {
    Write-Host ""
    Write-Host "=== VIBE CHECKLIST ===" -ForegroundColor Cyan
    Write-Host ""
    $items = @(
        "Goal, constraints, acceptance yazildi mi?",
        "Prompt scope kucuk ve file boundaries net mi?",
        "Generated code review edildi mi?",
        "App local'de calisiyor ve critical flow'lar geciyor mu?",
        "Testler ilgili alanlarda kosuldu mu?",
        "Dokumantasyon/notlar guncellendi mi?",
        "Commit net bir mesajla olusturuldu mu?",
        "Follow-up task'ler kaydedildi/kapatildi mi?"
    )
    foreach ($item in $items) {
        Write-Host "  [ ] $item" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Her birini gozden gecir, tamamlananlari [x] ile isaretle." -ForegroundColor DarkGray
}

# ============================================
#  HANDOFF GENERATOR
# ============================================
function New-Handoff {
    param([string]$Context, [string]$Changes, [string]$Checks, [string]$OpenIssues, [string]$NextPrompt)

    $handoff = @"
# Vibe Handoff — $(Get-Date -Format "yyyy-MM-dd HH:mm")

## Context
$Context

## Changes
$Changes

## Checks
$Checks

## Open Issues
$OpenIssues

## Next Prompt
$NextPrompt
"@
    $path = "$wsRoot\handoff-$(Get-Date -Format "yyyyMMdd_HHmmss").md"
    $handoff | Set-Content $path -Force
    Write-Host "[VIBE] Handoff: $path" -ForegroundColor Cyan
}

# ============================================
#  VIBE LOOP INIT
# ============================================
function Start-VibeLoop {
    if (-not $Goal) { Write-Host "[VIBE] HATA: -Goal parametresi gerekli" -ForegroundColor Red; return }
    if (-not $Scope) { Write-Host "[VIBE] HATA: -Scope parametresi gerekli" -ForegroundColor Red; return }

    Write-Host ""
    Write-Host "=== VIBE LOOP ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Step 1/6: Frame Outcome" -ForegroundColor Yellow
    Write-Host "  Goal: $Goal" -ForegroundColor White
    Write-Host "  Scope: $Scope" -ForegroundColor White
    Write-Host ""
    Write-Host "Step 2/6: Scope the Change" -ForegroundColor Yellow
    Write-Host "  Dependencies identified. Ready to generate." -ForegroundColor Green
    Write-Host ""
    Write-Host "Komut sirasi:" -ForegroundColor DarkGray
    Write-Host "  1. Prompt'u yaz ve AI'ya gonder" -ForegroundColor DarkGray
    Write-Host "  2. '/vibe-check' ile dogrula" -ForegroundColor DarkGray
    Write-Host "  3. '/vibe-checklist' ile release kontrolu yap" -ForegroundColor DarkGray
    Write-Host "  4. '/vibe-log' ile prompt'u kaydet" -ForegroundColor DarkGray
    Write-Host ""

    Add-PromptLog -Prompt $Goal -Outcome "started" -Tags $Scope
}

# ============================================
#  MAIN
# ============================================
if ($Init) { Start-VibeLoop; return }
if ($Check) { Show-Checklist; return }
if ($Log) { Add-PromptLog -Prompt $Prompt -Outcome "done" -Tags $Feature; return }
if ($Handoff) { New-Handoff -Context $Goal -Changes $Scope; return }

Write-Host ""
Write-Host "=== VIBE WORKFLOW ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Kullanim:" -ForegroundColor Yellow
Write-Host "  .\scripts\vibe-workflow.ps1 -Init -Goal 'hedef' -Scope 'kapsam'" -ForegroundColor White
Write-Host "  .\scripts\vibe-workflow.ps1 -Check" -ForegroundColor White
Write-Host "  .\scripts\vibe-workflow.ps1 -Log -Prompt 'ne yapildi'" -ForegroundColor White
Write-Host "  .\scripts\vibe-workflow.ps1 -Handoff -Goal 'context'" -ForegroundColor White
Write-Host ""
