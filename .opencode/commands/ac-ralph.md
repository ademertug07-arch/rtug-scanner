# Ralph Wiggum Loop — Iteratif AI Geliştirme

"Ralph is a Bash loop" — Geoffrey Huntley, 2025

```bash
while :; do cat PROMPT.md | claude ; done
```

## Built-in Komutlar
| Komut | Ne yapar |
|-------|----------|
| `/goal all tests pass` | Condition sağlanana kadar çalış |
| `/loop 5m check deploy` | Interval'da tekrarla |
| `/batch "migrate Jest to Vitest"` | Paralel worktree agent'ları |

## Ralph Loop Plugin
```
/ralph-loop:ralph-loop "Build a hello world API" --completion-promise "DONE" --max-iterations 10
/ralph-loop:cancel-ralph
```

## Best Practices
- **Clear completion criteria**: `<promise>COMPLETE</promise>` kullan
- **Incremental goals**: Fazlara böl (Phase 1/2/3)
- **Self-correction**: TDD loop ile hata varsa düzelt
- **Safety net**: Her zaman `--max-iterations` kullan
- **Escape hatches**: 15 iterasyon sonra alternatif öner

## Ready Templates

**Feature**: `/loop "Implement X with tests. Output <promise>COMPLETE</promise>" --max-iterations 30`
**TDD**: `/goal "all tests for X pass with >80% coverage"`
**Bug Fix**: `/goal "bug X is fixed with regression test"`
**Refactor**: `/goal "Y refactored, all tests still pass"`

Kaynak: awesomeclaude.ai/ralph-wiggum
