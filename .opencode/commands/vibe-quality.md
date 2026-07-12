# Vibe Quality Gates — 3 Katmanlı Kalite Kontrol

## 1. Vibe Check (subjective)
- Core flow end-to-end çalışıyor
- UI spacing, copy, states doğru
- Console hatası veya broken link yok
- Error states açık ve yardımcı

## 2. Objective Checks (measurable)
- Diff oku: beklenmeyen değişiklik var mı?
- İlgili testleri koş
- Performans-sensitive path'leri kontrol et
- Bağımlılıklar gerçek ve gerekli mi?

## 3. Release Ready (shippable)
- Docs ve handoff notları güncel
- Rollback planı veya önceki commit hazır
- Monitoring/logging eklendi (gerekliyse)
- Follow-up task'ler kaydedildi

Sıra: Vibe check → Objective checks → Release ready
Her gate fail olursa, stack'leme, düzelt ve baştan koş.
