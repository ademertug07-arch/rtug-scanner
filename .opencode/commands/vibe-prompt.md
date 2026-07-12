# Vibe Prompt — Prompt DNA + Template

## Prompt DNA
| Bileşen | Açıklama |
|---------|----------|
| **Goal** | Kullanıcı outcome'u + success criteria |
| **Constraints** | Stack, libraries, pattern'ler, non-negotiables |
| **Context** | İlgili dosyalar, API'ler, data shapes |
| **Inputs/Outputs** | Data I/O + expected behaviors |
| **Acceptance** | Merge öncesi geçmesi gereken check'ler |
| **Non-goals** | Ne değişmeyecek / eklenmeyecek |

## Prompt Template
```
Role: You are maintaining this repo.
Goal: <what the user should be able to do>
Constraints: <stack, libraries, style rules>
Context: <files, endpoints, data models>
Files: <what can change / what must not>
Acceptance: <tests, UI checks, edge cases>
Non-goals: <explicitly out of scope>
Deliverable: <patches + brief summary>
```

## Teknikler
- Önce plan iste, sonra kod
- Tek feature = tek prompt
- Diff-first: küçük yamalar iste, tüm dosyayı değil
- Gerçekçi sample data ver
- Acceptance criteria zorunlu tut
- Risk sor: model olası regresyonları söylesin
