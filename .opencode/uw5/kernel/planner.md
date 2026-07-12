# UW5 Task Planner
## Görevi: Görevi adımlara böl, bağımlılıkları belirle, sıralama yap.

### Adımlar
1. **Goal Analysis** — Kullanıcının gerçek hedefini anla
2. **Task Breakdown** — Hedefi alt görevlere böl
3. **Dependency Planning** — Hangi adım hangi adımdan önce gelmeli
4. **Parallelization** — Bağımsız adımları paralel çalıştır
5. **Milestone Definition** — Kontrol noktaları belirle

### Task Breakdown Formatı
```
Goal: <ne istediği>
├─ Task 1: <ne yapılacak>
│  ├─ Subtask 1.1
│  └─ Subtask 1.2
├─ Task 2: ...
└─ Validation: <başarı kriteri>
```

### Örnek
Goal: "TradingView göstergemi düzelt"
├─ Task 1: Hata analizi (dosyaları oku, hatayı bul)
│  ├─ .pine dosyasını oku
│  ├─ plot() sayısını kontrol et
│  └─ hatayı tespit et
├─ Task 2: Düzeltme (kodu düzenle)
│  ├─ plot() limitini düşür
│  └─ override et
└─ Validation: Pine Check çalıştır, 64-limit raporu al
