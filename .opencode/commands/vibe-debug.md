# Vibe Debug — AI ile Debugging

## Triage Ladder
1. **Reproduce** — Minimal case ile hatayı yakala
2. **Read diff** — Regresyonu izole et
3. **Add logging** — Hafif logging veya assertion ekle
4. **Targeted fix** — Kısıtlı, odaklı fix iste
5. **Revert if loop** — Döngüye girerse geri al, prompt'u yeniden çerçevele

## Getir: repro steps, expected vs actual, error logs, environment details

## Common Failure Modes
| Sorun | Çözüm |
|-------|-------|
| Hallucinated dependencies | Versiyon kilitle, changelog kontrol |
| Model drift | Session reset + clean summary |
| Large rewrites | Minimal patch iste |
| Overprompting | Scope'u küçült |
| Silent edge case breaks | Error state test ekle |

## Debug Prompt Template
```
Bug: <kısa açıklama>
Repro: <adım adım>
Expected: <beklenen>
Actual: <olan>
Environment: <OS, versiyon, browser>
Fix scope: <sadece hangi dosyalar>
```
