# VIBE CODING GUIDE — AI-Directed Development

Kaynak: [awesomeclaude.ai/vibe-coding-guide](https://awesomeclaude.ai/vibe-coding-guide)

## Definition & Ethos

Vibe coding = AI-assisted development where **sen** intent'i belirler, AI kod'u döker, **sen** onaylarsın.

| Eski Usul | Vibe Coding |
|-----------|-------------|
| Syntax odaklı | Intent odaklı |
| Her satırı sen yaz | AI döker, sen review et |
| Compile error | Behavior bug |
| Solo building | AI ile dialog |

### 4 Prensip
1. **Director mindset** — Sen tanımla, AI döksün
2. **Small scopes** — Kısa prompt, dar diff, temiz output
3. **Verify by default** — Her şeyi test et
4. **State discipline** — Sık commit, log tut, rollback hazır

## When to Vibe vs When to Code

| Vibe (hızlı dene) | Traditional (sağlam yap) |
|--------------------|--------------------------|
| MVP, demo, prototip | Safety-critical sistemler |
| Internal tool, script | Performance-critical kod |
| UI iterasyonları | Security/auth/crypto |
| Data cleanup | Büyük mimari kararlar |
| Dokümantasyon | Belirsiz gereksinimler |

## The Vibe Loop (6 Adım)

```
1. Frame outcome  → 2. Scope change  → 3. Generate
                                          ↓
           6. Integrate  ←  5. Objective checks  ←  4. Vibe check
```

## Prompting Playbook

### Prompt DNA
- **Goal**: Kullanıcı outcome'u + success criteria
- **Constraints**: Stack, libraries, non-negotiables
- **Context**: İlgili dosyalar, API'ler, data shapes
- **Inputs/Outputs**: Data I/O + expected behaviors
- **Acceptance**: Merge öncesi geçmesi gereken check'ler
- **Non-goals**: Ne değişmeyecek / eklenmeyecek

## Quality Gates

| Gate | Ne kontrol eder |
|------|----------------|
| Vibe check | Core flow, UI states, error states |
| Objective checks | Diff review, tests, perf, dependencies |
| Release ready | Docs, rollback plan, monitoring |

## Debugging & Recovery

Triage: Reproduce → Read diff → Add logging → Targeted fix → Revert if loop

## Workflow Hygiene
- Commit like checkpoints (sık commit)
- Keep a prompt log (ne sorduysan kaydet)
- Track TODOs explicitly
- Reset context when it drifts
- Keep diffs small
- Document decisions

## Prompt Recipes
| Recipe | Kullanım |
|--------|----------|
| Feature | `Goal + Constraints + Files + Acceptance` |
| Bug fix | `Repro + Expected + Actual + Fix scope` |
| Refactor | `Small diff + preserve behavior` |
| Tests | `Test plan before code` |
| UX polish | `5 improvements with before/after` |
| Security | `Risk list + suggested fixes` |

## Vibe Coding Checklist
- [ ] Goal, constraints, acceptance written down
- [ ] Scope small, file boundaries clear
- [ ] Generated code reviewed (logic + dependencies)
- [ ] App runs locally, critical flows pass
- [ ] Tests/scripts run for affected areas
- [ ] Docs/notes updated
- [ ] Commit with clear message
- [ ] Follow-up tasks captured/closed
