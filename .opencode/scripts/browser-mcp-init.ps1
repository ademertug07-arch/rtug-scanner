# Browser MCP Trio Init — Playwright + Chrome DevTools + Puppeteer
param(
  [string]$MCP = "all",
  [string]$Url = "",
  [switch]$Help
)

$ErrorActionPreference = "Continue"

function Show-Help {
  Write-Host @"
Browser MCP Trio — v1.0
Usage: .opencode\scripts\browser-mcp-init.ps1 [options]

Options:
  -MCP <type>   Browser MCP to init (playwright | chrome | puppeteer | all)
  -Url <url>    Quick test URL (takes screenshot)
  -Help         Show this help

Examples:
  .\browser-mcp-init.ps1 -MCP playwright -Url https://example.com
  .\browser-mcp-init.ps1 -MCP all
"@
}

function Init-Playwright {
  Write-Host "[Playwright MCP] Checking..."
  try {
    $v = npx @playwright/mcp@latest --version 2>$null
    if (-not $v) { throw "not found" }
    Write-Host "[Playwright MCP] OK — $v"
  } catch {
    Write-Host "[Playwright MCP] Installing via npx..."
    npx @playwright/mcp@latest --help *>$null
    Write-Host "[Playwright MCP] Ready (npx will cache on first use)"
  }
}

function Init-ChromeDevTools {
  Write-Host "[Chrome DevTools MCP] Checking..."
  try {
    $v = npx @anthropic/chrome-dev-tools-mcp@latest --version 2>$null
    if (-not $v) { throw "not found" }
    Write-Host "[Chrome DevTools MCP] OK — $v"
  } catch {
    Write-Host "[Chrome DevTools MCP] Installing via npx..."
    npx @anthropic/chrome-dev-tools-mcp@latest --help *>$null
    Write-Host "[Chrome DevTools MCP] Ready"
  }
}

function Init-Puppeteer {
  Write-Host "[Puppeteer MCP] Checking..."
  try {
    $v = npx puppeteer-mcp@latest --version 2>$null
    if (-not $v) { throw "not found" }
    Write-Host "[Puppeteer MCP] OK — $v"
  } catch {
    Write-Host "[Puppeteer MCP] Installing via npx..."
    npx puppeteer-mcp@latest --help *>$null
    Write-Host "[Puppeteer MCP] Ready"
  }
}

if ($Help) { Show-Help; exit 0 }

switch ($MCP.ToLower()) {
  "playwright"      { Init-Playwright }
  "chrome"          { Init-ChromeDevTools }
  "puppeteer"       { Init-Puppeteer }
  "all" {
    Init-Playwright
    Init-ChromeDevTools
    Init-Puppeteer
  }
  default {
    Write-Warning "Unknown MCP: $MCP. Use: playwright, chrome, puppeteer, or all"
    Show-Help
    exit 1
  }
}

if ($Url) {
  Write-Host "[Browser MCP] Quick test: $Url"
  try {
    npx @playwright/mcp@latest screenshot $Url --output "$env:TEMP\mcp-test-screenshot.png"
    Write-Host "[Browser MCP] Screenshot saved to $env:TEMP\mcp-test-screenshot.png"
  } catch {
    Write-Warning "[Browser MCP] Screenshot test failed: $_"
  }
}

Write-Host "[Browser MCP Trio] Init complete."
