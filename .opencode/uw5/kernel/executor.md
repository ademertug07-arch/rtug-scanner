# UW5 Execution Engine
## Görevi: Pipeline'ı yürüt, adımları logla, hataları yönet.

### Execution Modes
- Sequential: adımlar sırayla çalışır (bağımlı task'ler)
- Parallel: bağımsız adımlar eşzamanlı çalışır
- Hybrid: karışık (bazı adımlar paralel, bazıları sıralı)

### Pipeline Yürütme Prosedürü
1. Pipeline tanımını al (hangi L katmanları)
2. Her katman için:
   a. Katmanı başlat
   b. Girdiyi hazırla
   c. Çalıştır
   d. Çıktıyı doğrula
   e. Sonraki katmana geç
3. Hata varsa → Self-Healing (L16)
4. Tamamlandı → Golden State (L19)

### Error Recovery
- İlk hata: 3 kez patch → retry → verify
- 3 başarısız: fallback strateji uygula
- Tüm hatalar KAIROS'a kaydedilir
