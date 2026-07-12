---
description: OpenCode Zen — curated model gateway. Sign up, configure, and use 50+ verified models with automatic best-model selection.
---

# OpenCode Zen Integration

## What is Zen?
A curated, pay-as-you-go model gateway by Anomaly (OpenCode team). 50+ tested models optimized for coding agents. Single API key, no provider inconsistency.

## Setup
1. Go to https://opencode.ai/zen, sign up, add $20 balance
2. Copy your API key
3. Set env var: `$env:OPENCODE_ZEN_API_KEY = "your-key"`
4. Or login via TUI: `/connect` → select OpenCode Zen → paste key

## Models Available
- DeepSeek V4 Flash (free): `deepseek-v4-flash-free`
- DeepSeek V4 Flash: `deepseek-v4-flash` ($0.14/$0.28)
- DeepSeek-V4-Pro-Max: `deepseek-v4-pro` ($1.74/$3.84)
- GPT-5.5: `gpt-5.5` ($5/$30)
- Claude Sonnet 5: `claude-sonnet-5` ($2/$10)
- Claude Opus 4.8: `claude-opus-4-8` ($5/$25)
- Gemini 3.5 Flash: `gemini-3.5-flash` ($1.5/$9)
- And 45+ more

## Usage
Zen is automatically used when:
- `/uw5 <task>` — auto-selects best Zen model for the task complexity
- Simple task → `deepseek-v4-flash-free` (free, fast)
- Medium task → `deepseek-v4-flash` ($0.14/$0.28)
- Complex task → GPT-5.5 or Claude Sonnet 5
- Critical/architecture → Claude Opus 4.8

## Model Selection Logic
Task complexity determines which Zen model to use:
1. Quick/exploratory → free tier (deepseek-v4-flash-free)
2. Code generation → balanced (deepseek-v4-flash or gpt-5.4-mini)
3. Complex architecture → premium (claude-sonnet-5 or gpt-5.5)
4. Critical review → max quality (claude-opus-4-8)

## Cost Control
- Zen auto-top-up: balance < $5 → adds $20
- Monthly spend limits configurable in Zen dashboard
- Current model `deepseek-v4-flash-free` costs $0 — Zen not required for basic use
