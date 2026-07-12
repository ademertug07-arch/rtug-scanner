# Vibe Loop — 6 Adımda AI Destekli Geliştirme

```
1. Frame outcome  → 2. Scope change  → 3. Generate
                                          ↓
           6. Integrate  ←  5. Objective checks  ←  4. Vibe check
```

Her adımda:
1. **Frame**: Hedef + kısıtlar + kabul kriterlerini yaz
2. **Scope**: Hangi dosyalar değişecek, hangileri dokunulmayacak
3. **Generate**: Tek focused pass'te AI'ya ürettir
4. **Vibe check**: Uygulamayı çalıştır, davranış/layout/edge case kontrol
5. **Objective checks**: Diff oku, test koş, perf/security kontrol
6. **Integrate**: Commit + dokümantasyon + sonraki iterasyon

Çıkış sinyalleri: diff okunabilir, testler geçer, UX eşleşir, edge case'ler kontrol edilmiş
