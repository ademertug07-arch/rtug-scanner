# AWESOME CLAUDE — Curated Resources

Kaynak: [awesomeclaude.ai](https://awesomeclaude.ai/)

## Claude Code Cheatsheet v2.1

### Model Aliases (Jun 2026)
| Alias | Model | Kullanım |
|-------|-------|----------|
| `fable` | claude-fable-5 | Mythos-class flagship, en zor işler |
| `opus` | claude-opus-4-8 | Kompleks reasoning, mimari |
| `sonnet` | claude-sonnet-4-6 | Günlük kod, Pro varsayılan |
| `haiku` | claude-haiku-4-5 | Hızlı, basit task'ler |
| `best` | → Fable/Opus | En güçlü modeli otomatik seç |

### Effort Levels
`low` `medium` `high` `xhigh` `max` `ultracode`
`/effort <level>` veya `claude --effort <level>`

### CLI Flags
| Flag | Ne yapar |
|------|----------|
| `claude -p "query"` | Headless/print mode |
| `claude --model sonnet` | Model seç |
| `claude --effort high` | Effort seviyesi |
| `claude --safe-mode` | Tüm customizasyonları devre dışı bırak |
| `claude --permission-mode plan` | Permission modu |
| `claude --max-turns 10` | Maksimum tur |
| `claude --bg --exec 'cmd'` | Background agent |
| `claude --worktree feature-x` | Git worktree |
| `claude doctor` | Diagnostik |

### Slash Commands
`/clear` `/compact` `/resume` `/branch` `/rewind` `/model` `/effort`
`/plan` `/goal` `/code-review` `/security-review` `/verify` `/diff`
`/loop` `/batch` `/schedule` `/agents` `/hooks` `/skills` `/memory`

### Skills vs Commands
- **Slash Commands**: User-invoked (`/komut`), tek dosya, basit prompt
- **Agent Skills**: Model-invoked (otomatik), kompleks, çoklu dosya+script

## Awesome Claude Skills (169 adet, 13 kategori)

| Kategori | Öne Çıkan Skill'ler |
|----------|-------------------|
| Document | docx, pdf, pptx, xlsx, revealjs |
| Development | TDD, git-worktrees, AWS, debug-skill, blueprint, Qdrant |
| Data & Analysis | CSV summarizer, Postgres/MySQL/MSSQL, Kaggle, crypto |
| Scientific | 125+ scientific skills, materials simulation, paper-search |
| Writing | article-extractor, content-research, avoid-ai-writing |
| Learning | karpathy-llm-wiki, tapestry, swarmvault |
| Media | youtube-transcript, video-downloader, imagen, elevenlabs |
| Health | health assistant, DNA analysis |
| Collaboration | kanban, linear, meeting-insights, PM skills |
| Security | VibeSec, OWASP, Trail of Bits, defense-in-depth |
| Utility | file-organizer, skill-creator, template-skill |
| Automation | task-observer, agent-manager |
| Games | Unity agent skills |

## Top MCP Servers

| Sıra | MCP | Yıldız | Ne işe yarar |
|------|-----|--------|-------------|
| 1 | microsoft/markitdown | 152K | File → Markdown dönüşümü |
| 2 | server-everything | 87K | MCP protocol test |
| 3 | netdata | 79K | Observability |
| 4 | upstash/context7 | 57K | Code docs for LLMs |
| 5 | mindsdb | 39K | Veri platformu |
| 6 | playwright-mcp | 34K | Browser automation |
| 7 | github-mcp-server | 31K | GitHub API |
| 8 | claude-task-master | 27K | Task management |
| 9 | blender-mcp | 23K | 3D modeling |
| 10 | screenpipe | 19K | Screen/audio capture |

Tam liste: [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — 1,076 server, 39 kategori

## Ralph Wiggum Loop

Ralph = iteratif AI loop. Temel prensip:
```bash
while :; do cat PROMPT.md | claude ; done
```

### Built-in Alternatifler
| Komut | Ne yapar |
|-------|----------|
| `/goal` | Condition sağlanana kadar çalış |
| `/loop` | Interval'da tekrarla |
| `/batch` | Paralel worktree agent'ları |
| `/ralph-loop` | Plugin (completion-promise + max-iterations) |

### Best Practices
- Clear completion criteria (`<promise>COMPLETE</promise>`)
- Incremental goals (fazlara böl)
- Self-correction pattern (TDD loop)
- Hep `--max-iterations` kullan (safety net)

## Community Resources

| Kaynak | Link | Ne işe yarar |
|--------|------|-------------|
| awesome-claude-code | [hesreallyhim](https://github.com/hesreallyhim/awesome-claude-code) | Slash-commands, CLAUDE.md, CLI tools |
| awesome-claude-skills | [travisvn](https://github.com/travisvn/awesome-claude-skills) | Skill resources |
| awesome-claude-skills | [BehiSecc](https://github.com/BehiSecc/awesome-claude-skills) | 169 categorized skills |
| awesome-claude-prompts | [langgptai](https://github.com/langgptai/awesome-claude-prompts) | Prompt examples |
| awesome-claude-agents | [vijaythecoder](https://github.com/vijaythecoder/awesome-claude-agents) | Specialized AI agents |
| awesome-claude-code-subagents | [VoltAgent](https://github.com/VoltAgent/awesome-claude-code-subagents) | 100+ subagents |
| awesome-mcp-servers | [punkpeye](https://github.com/punkpeye/awesome-mcp-servers) | 1,076 MCP servers |

## Official Resources

| Kaynak | Link |
|--------|------|
| Claude Console | console.anthropic.com |
| Documentation | platform.claude.com/docs/ |
| Models & Pricing | platform.claude.com/docs/en/about-claude/models/overview |
| SDK Python | github.com/anthropics/anthropic-sdk-python |
| SDK TypeScript | github.com/anthropics/anthropic-sdk-typescript |
| Agent SDK Python | github.com/anthropics/claude-agent-sdk-python |
| Agent SDK TS | github.com/anthropics/claude-agent-sdk-typescript |
| Cookbook | github.com/anthropics/claude-cookbooks |
| Quickstarts | github.com/anthropics/claude-quickstarts |
| MCP Official | modelcontextprotocol.io |
| AWS Bedrock | aws.amazon.com/bedrock/anthropic/ |
| GCP Vertex | cloud.google.com/products/model-garden/claude |
| Azure AI | ai.azure.com/catalog/publishers/anthropic |
| Claude Desktop | claude.ai/download |
| Claude for Chrome | chromewebstore.google.com/detail/claude/... |
