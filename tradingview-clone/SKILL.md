---
name: clone-website
description: AI Website Cloner — reverse-engineer any website into a pixel-perfect Next.js + shadcn/ui + Tailwind v4 replica. 5-phase pipeline: Recon, Foundation, Spec & Dispatch, Assembly, Visual QA. Supports browser MCP (Chrome/Playwright). Built from JCodesMore/ai-website-cloner-template (19.5k⭐).
---

# AI Website Cloner

Clone any website URL into a pixel-perfect Next.js replica. Uses `.claude/skills/clone-website/SKILL.md` for the full pipeline.

## Usage
- `/clone-website <url>` — Clone a single site
- `/clone-website <url1> <url2>` — Clone multiple sites in parallel

## Requirements
- Browser MCP (Chrome MCP or Playwright MCP)
- npm run build passing

## Tech Stack
- Next.js 16 + React 19 + TypeScript strict
- shadcn/ui + Tailwind CSS v4
- Lucide React icons
- Target: Vercel deployment
