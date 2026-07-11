# RTUG COLOR SURROUND — 7/24 Canli Bildirim Sistemi

## 🚀 Hızlı Kurulum (2 dk)

```powershell
# 1. PowerShell'i Yönetici olarak aç
# 2. Kurulum scriptini çalıştır:
.\setup_surround_daemon.ps1
```

Script sırasıyla:
1. Pip paketlerini yükler
2. Telegram token'ını test eder
3. Windows Task Scheduler'a görev ekler (her açılışta otomatik başlar)
4. Daemon'u başlatır

---

## 📋 Sistem Mimarisi

```
┌─────────────────────────────────────────────────┐
│                 DAEMON (7/24)                    │
│  python rtug_surround_daemon.py                  │
│                                                   │
│  Her 15 dk'da bir:                                │
│    ├─ BIST  (60 hisse - Yahoo Finance)           │
│    ├─ US    (35 hisse - Yahoo Finance)           │
│    └─ Crypto (25 coin - Binance)                 │
│                                                   │
│  Pattern tespiti:                                 │
│    ├─ Bullish Surround 🟣                         │
│    ├─ Bearish Surround 🔴                         │
│    ├─ Strong Bullish Surround 🟢                  │
│    ├─ Deep Surround 🟣/🔴                         │
│    └─ Reverse Circle 🔵/🟠                        │
│                                                   │
│  Çıktı:                                           │
│    └─ Telegram'a anında bildirim                  │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Kullanım

### Normal çalıştırma (her 15 dk'da bir tarar):
```bash
python rtug_surround_daemon.py
```

### Özel aralık (her 5 dk'da bir):
```bash
python rtug_surround_daemon.py --interval 5
```

### Tek seferlik tarama:
```bash
python rtug_surround_daemon.py --once
```

### Sadece BIST tara:
```bash
python rtug_surround_daemon.py --once --no-us --no-crypto
```

### Sadece kripto tara:
```bash
python rtug_surround_daemon.py --once --no-bist --no-us
```

---

## 🪟 Windows Task Scheduler (Otomatik Başlatma)

Daemon her Windows açılışında otomatik başlasın:

```bash
# EKLE (yönetici PowerShell):
python rtug_surround_daemon.py --install --interval 15

# KALDIR:
python rtug_surround_daemon.py --uninstall
```

---

## 📊 Telegram'da Ne Göreceksin?

### Yeni surround tespit edildiğinde:
```
RTUG COLOR SURROUND ALERT
Kaynak: BIST 100
Zaman: 15.07.2026 14:30
Sinyal: 3 sembol
----------------------------
P> THYAO.IS | BOGA SARMA [Purple+Blue>Red]
   Skor: 78% | D1:MOR UP D2:TURUNCU DN D6:MAVI UP
   Bull:4/5 Bear:1/5 | $312.50
R< GARAN.IS | AYI SARMA [Pink+Brown>Red]
   Skor: 22% | D1:PEMBE DN D2:KIRMIZI UP D6:KAHVE DN
   Bull:1/5 Bear:4/5 | $124.30
----------------------------
RTUG SURROUND DAEMON (7/24)
```

### Daemon başladığında:
```
RTUG SURROUND DAEMON BASLADI
Interval: 15 dk
BIST: 60 hisse
US: 35 hisse
Crypto: 25 coin
Zaman: 15.07.2026 14:00
```

---

## ⚙️ TradingView + Webhook (Alternatif, Gerçek Zamanlı)

Daha hızlı (mum kapanışı anında) bildirim için:

### Pine Script:
1. TradingView'de Pine Editor'ı aç
2. `rtug_color_surround.pine` içeriğini yapıştır
3. **Save** → İsim: `RTUG COLOR SURROUND`
4. Chart'a ekle

### Alert Kurulumu:
1. Chart'ta sağ tık → **Add Alert**
2. **Condition**: `RTUG COLOR SURROUND` seç
3. İstediğin alert'i seç:
   - `BULLISH SURROUND (Purple+Blue wrap Red)` 🟣
   - `BEARISH SURROUND (Pink+Brown wrap Red)` 🔴
   - `STRONG BULLISH SURROUND` 🟢
   - `DEEP BULLISH SURROUND` 🟣
   - `REVERSE CIRCLE BULLISH` 🔵
4. **Webhook URL**: (n8n/ngrok kuruluysa)

### Webhook için:
```bash
# ngrok kur (https://ngrok.com/download)
# n8n'i başlat
n8n start

# ngrok ile publik yap
ngrok http 5678

# n8n'e workflow'u import et:
# obsidian\n8n-workflows\rtug-surround-webhook.json
```

---

## 🩺 Test

```bash
# Daemon'u test et (tek sefer, telegram olmadan):
python rtug_surround_daemon.py --once --no-telegram --no-crypto

# Scanner core test:
python rtug_scanner_core.py
```

---

## 📁 Dosya Yapısı

| Dosya | Açıklama |
|-------|----------|
| `rtug_surround_daemon.py` | **Ana daemon** (7/24 çalışır) |
| `setup_surround_daemon.ps1` | **Tek tıkla kurulum** |
| `rtug_color_surround.pine` | TradingView indikatörü |
| `rtug_scanner_core.py` | Sinyal motoru (güncellendi) |
| `rtug_multi_symbol_scanner.py` | Multi-symbol tarayıcı (güncellendi) |
| `.env` | Telegram bot token |
| `logs/surround_daemon.log` | Daemon logları |
| `.surround_status.json` | Bildirilen pattern'lerin kaydı |
| `obsidian/n8n-workflows/rtug-surround-webhook.json` | n8n workflow (yedek) |
| `SURROUND_7x7_SETUP.md` | Bu dosya |

---

## ⚠️ Önemli Notlar

1. **İnternet gerekli**: Yahoo Finance ve Binance API'leri çalışır
2. **Windows açık kalmalı**: Daemon kapanırsa bildirim durur
3. **Tekrar bildirim önleme**: Aynı pattern 24 saat içinde tekrar bildirilmez
4. **BIST verisi**: Yahoo Finance BIST'te bazen gecikmeli olabilir
5. **Bildirim yoksa**: Log kontrol et: `logs\surround_daemon.log`
