# When to Vibe vs When to Code

## Vibe (hızlı dene, tolere edilebilir hata)
- MVP, demo, investor prototype
- Internal tool ve automation script
- UI iterasyonları ve content-heavy pages
- Data cleanup veya tek seferlik migration (review ile)
- Documentation scaffolding
- Net testleri ve boundary'leri olan refactor'lar

## Traditional (yavaş, sağlamlaştır)
- Safety-critical veya regulated sistemler (review'suz)
- Performance-critical algoritmalar ve low-level optimizasyonlar
- Büyük mimari kararlar (human design olmadan)
- Security-heavy auth veya cryptography (expert olmadan)
- Belirsiz gereksinimler veya çözülmemiş product soruları
- Test'siz veya dokümantasyonsuz uzun ömürlü sistemler

## Hybrid Path
Vibe ile iskele kur + exploration yap → Requirements kilitle → Test yaz → Human rigor ile refactor et
