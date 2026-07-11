# ☁️ RTUG COLOR SURROUND — Bulut 7/24 Kurulum

## 🎯 Ne İşe Yarar?

**Windows kapalıyken bile** her 30 dakikada bir piyasaları tarar, yeni surround
pattern'leri tespit eder ve Telegram'a anında bildirim gönderir.

```
GitHub (Bulut) ──── her 30 dk ────→ Yahoo Finance ────→ Analiz ────→ Telegram
     ↑                                                       ↑
  Windows kapalı                                      Sen nerede olursan ol
```

---

## ⚡ Adım Adım Kurulum (2 dakika)

### 1️⃣ GitHub Reposu Oluştur

```bash
# GitHub'da yeni repo oluştur: https://github.com/new
# Repo adı: rtug-scanner (veya istediğin isim)
# Public veya Private fark etmez
```

### 2️⃣ Kodları GitHub'a Push Et

```bash
# Proje dizinine git
cd "C:\Users\cagda\OneDrive\Masaüstü\open code mode"

# Git init (ilk seferde)
git init
git add .
git commit -m "RTUG Color Surround Scanner - 7/24 Cloud Ready"

# GitHub repona bağla (KULLANICI adını değiştir!)
git remote add origin https://github.com/KULLANICI/rtug-scanner.git
git branch -M main
git push -u origin main
```

> 💡 `git push` istediğinde GitHub kullanıcı adı ve şifre isteyecek.
> Şifre yerine **Personal Access Token (PAT)** kullan:
> https://github.com/settings/tokens → New token → `repo` seç → Oluştur

### 3️⃣ Telegram Bilgilerini GitHub Secrets'a Ekle

GitHub'da repo sayfasına git:
```
Settings → Secrets and variables → Actions → New repository secret
```

**İki tane secret ekle:**

| Secret Adı | Değer |
|-----------|-------|
| `TELEGRAM_BOT_TOKEN` | `8882842172:AAFw6HTJVB6fXndUjH_D4wJpgXoqh6GIZiI` |
| `TELEGRAM_CHAT_ID` | `6988108865` |

### 4️⃣ ✅ Bitti! Workflow Otomatik Başlar

GitHub Actions'e gir:
```
Actions → RTUG Surround
```

Şu anlarda ilk çalışmayı göreceksin. Yeşil tik ✅ gelince sistem aktif demektir.

---

## 📊 Canlı Durum Takibi

### Workflow çalışıyor mu?
```
GitHub repo → Actions → RTUG Surround
```
Yeşil ✅ = çalışıyor, Kırmızı ❌ = hata var

### Son durum özeti
Her workflow run'ının altında bir summary tablosu var:
- Kaç pattern kayıtlı
- Son tarama zamanı
- Hangi piyasalar tarandı

### Telegram'a gelen mesaj
```
RTUG COLOR SURROUND ALERT
Kaynak: BIST 100
Zaman: 15.07.2026 14:30
Sinyal: 3 sembol
...
RTUG SURROUND DAEMON (7/24)
```

---

## 🔧 Yönetim

### Manuel çalıştırma (test için)
```
GitHub repo → Actions → RTUG Surround → Run workflow
```

### Workflow'u durdurma
```
GitHub repo → Settings → Actions → General → Disable Actions
```

### Workflow'u tekrar başlatma
Aynı yerden Actions'ı tekrar enable et.

### Free tier limitleri
| Metrik | Limit | Bizim Kullanım |
|--------|-------|---------------|
| Aylık çalışma süresi | 2000 dk | ~45 dk/ay (30dk interval ile) |
| Cache | 10 GB | ~100 KB |
| Eşzamanlı job | 1 | 1 (concurrency ile) |

> 🟢 **Bol bol yerimiz var.** 30 dk interval ile ayda sadece ~45 dk kullanıyoruz.

---

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────────────┐
│                      GITHUB ACTIONS (Bulut)                        │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Schedule: */30 * * * *                                      │   │
│  │  ┌──────────┐    ┌───────────┐    ┌──────────────┐          │   │
│  │  │ Restore  │───→│  Python   │───→│  Save Cache  │          │   │
│  │  │  Cache   │    │  Scanner  │    │  (.status)   │          │   │
│  │  └──────────┘    └─────┬─────┘    └──────────────┘          │   │
│  │                        │                                     │   │
│  │                        ▼                                     │   │
│  │                  ┌──────────┐                                │   │
│  │                  │Telegram  │                                │   │
│  │                  │  API     │                                │   │
│  │                  └──────────┘                                │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         ▲                                            ▲
         │                                            │
    Yahoo Finance                                 Telegram
    (BIST + US)                                  (Telefonun)
```

---

## ❓ Sık Sorulanlar

**S: Windows kapalıyken çalışır mı?**
Evet. GitHub'ın sunucularında çalışır, Windows'la alakası yok.

**S: Telefon kapalıyken bildirim gelir mi?**
Telegram bildirimi telefon açılınca gelir. Ama bildirim kaybolmaz.

**S: Ücretli mi?**
Hayır. GitHub Actions free tier'ı yeterli.

**S: Kripto neden yok?**
İki sebep: (1) ccxt bağımlılığını azaltmak, (2) Crypto zaten 7/24 işlem görüyor,
Surround pattern'leri hisselerde daha anlamlı. Crypto eklemek için
`--no-crypto` flag'ini kaldır ve `requirements.txt`'ye ccxt ekle.

**S: Bildirim sıklığı?**
Her 30 dakikada bir. Bunun sebebi:
- Piyasalar günlük mumlarla çalışır (5-15 dk'da yeni veri gelmez)
- GitHub free tier limitlerini aşmamak
İstersen `.github/workflows/rtug-surround.yml` dosyasındaki `cron` değerini değiştir.

**S: Kaçırdığım pattern olur mu?**
30 dk'da bir tarama yeterli çünkü:
- Yahoo Finance verisi 15-30 dk gecikmeli
- Günlük mumlar saatlerce aynı kalır
- Pattern değişimi mum kapanışında olur (günde 1)
