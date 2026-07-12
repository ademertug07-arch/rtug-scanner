# Claude Code Cheatsheet v2.1

## Models
`/model fable|opus|sonnet|haiku|best`

## Effort
`/effort low|medium|high|xhigh|max|ultracode`

## Key CLI Flags
| Flag | Kullanım |
|------|----------|
| `claude -p "query"` | Headless mode |
| `claude --model fable` | Model seç |
| `claude --effort xhigh` | Effort seviyesi |
| `claude --safe-mode` | Troubleshooting modu |
| `claude --permission-mode plan` | Sadece plan |
| `claude --bg --exec 'cmd'` | Background agent |
| `claude doctor` | Diagnostik |
| `claude update` | Güncelle |

## Headless Examples
```bash
claude -p "Analyze these errors" --output-format json
gh pr diff 123 | claude -p --allowedTools "Read,Grep"
claude --max-turns 3 -p "Generate summary"
```

## Slash Commands
`/clear` `/compact` `/resume` `/branch` `/rewind` `/context`
`/model` `/effort` `/fast` `/plan` `/goal` `/code-review` `/simplify`
`/security-review` `/verify` `/diff` `/loop` `/batch` `/schedule`
`/agents` `/hooks` `/skills` `/reload-skills` `/memory` `/init`
`/config` `/permissions` `/mcp` `/status` `/usage` `/doctor`

## Env Variables
`ANTHROPIC_MODEL` `ANTHROPIC_BASE_URL` `MAX_THINKING_TOKENS`
`CLAUDE_CODE_EFFORT_LEVEL` `CLAUDE_CODE_SAFE_MODE`
`CLAUDE_CODE_USE_BEDROCK` `CLAUDE_CODE_USE_VERTEX`

Tam detay: AWESOMECLAUDE.md
Kaynak: awesomeclaude.ai/code-cheatsheet
