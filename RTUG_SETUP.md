# RTUG BREAKOUT ALERT — Kurulum Kılavuzu (n8n)

## 📂 Proje Dosyaları

| Dosya | Açıklama |
|---|---|
| `rtug_breakout_alert.pine` | **Pine Script** — TradingView indikatörü + 8 alertcondition |
| `rtug_telegram_bot.py` | **Python Bot** — (alternatif, localhost) |
| `C:\Users\cagda\OneDrive\Masaüstü\obsidian\n8n-workflows\rtug-breakout-alert.json` | **n8n Workflow** — Tavsiye edilen ✅ |
| `.env.rtug.example` | **Örnek config** |

---

## 🏆 Önerilen Yöntem: n8n (Çünkü localhost çalışmıyor)

n8n ile TradingView → Webhook → Telegram zinciri kuruyoruz.
n8n zaten sistemde kurulu (`npm global: n8n`).

---

## 🔧 Adım 1: Pine Script'i TradingView'e Ekle

1. TradingView'de **Pine Editor**'ı aç
2. `rtug_breakout_alert.pine` içeriğini **kopyala → yapıştır**
3. 💾 **Save** → İsim: `RTUG BREAKOUT ALERT`
4. Chart'a ekle: **Indicators → RTUG BREAKOUT ALERT**

---

## 🚀 Adım 2: n8n'i Başlat

```bash
# n8n'i başlat (port 5678 varsayılan)
n8n start
```

📍 n8n arayüz: `http://localhost:5678`

---

## 📥 Adım 3: Workflow'u İçe Aktar

1. n8n'de **Workflows** sayfasına git
2. Sağ üst **Import from File** butonuna tıkla
3. Şu dosyayı seç:  
   `C:\Users\cagda\OneDrive\Masaüstü\obsidian\n8n-workflows\rtug-breakout-alert.json`
4. Workflow açılacak → **Save** (Kaydet)

---

## ⚙️ Adım 4: Telegram Credential'ını Kontrol Et

Workflow'da **Telegram'a Gönder** düğümünü aç:
- `Credential for Telegram API`: **Telegram Bot** seçili olmalı
- `Chat ID`: `6988108865` (varsayılan)

Eğer credential yoksa:
1. n8n'de **Credentials** → **Add Credential**
2. **Telegram API** seç
3. Bot token'ını gir (Telegram @BotFather'dan al)
4. İsim: `Telegram Bot`

---

## 🔗 Adım 5: Webhook URL'ini Al

1. Workflow'da **TradingView Webhook** düğümünü aç
2. **Webhook URLs** bölümündeki **Production URL**'i kopyala:
   ```
   https://localhost:5678/webhook/rtug-breakout
   ```
   ⚠️ Bu URL localhost olduğu için TradingView erişemez!

### Çözüm: ngrok ile publik yap

```bash
# ngrok'u indir: https://ngrok.com/download
ngrok http 5678
```

ngrok şöyle bir URL verecek:
```
https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

**Webhook URL'n şu şekilde olacak:**
```
https://xxxx-xx-xx-xx-xx.ngrok-free.app/webhook/rtug-breakout
```

---

## 📊 Adım 6: TradingView Alert Oluştur

1. Chart'ta sağ tık → **Add Alert**
2. **Condition**: `RTUG BREAKOUT ALERT` seç
3. **Alert on:** İstediğin sinyali seç:
   - `RTUG Bullish Breakout` 🟢
   - `RTUG Bearish Breakout` 🔴
   - `RTUG Super Bullish` 🚀
   - `RTUG Super Bearish` 🔻
   - `RTUG Fast Div Cross Up/Down` ⚡
   - `RTUG Momentum Bullish/Bearish` 📊
4. **Webhook URL**: `https://xxxx.ngrok-free.app/webhook/rtug-breakout`
5. ✅ **Create**

İstersen **tüm sinyaller için tek bir alert** kurabilirsin (tek alert, 8 sinyal).

---

## 📋 n8n Workflow Yapısı

```
TradingView → Webhook (POST /rtug-breakout)
                  ↓
           Parse TV Data (Code Node - JSON parse + mesaj formatla)
                  ↓
           Telegram'a Gönder (HTML formatında mesaj)
```

### Telegram'a Gönderilecek Mesaj Örneği:
```
🔔 RTUG BREAKOUT ALERT
━━━━━━━━━━━━━━━━━
💰 Sembol: BTCUSDT
💲 Fiyat: 65432.50
🕐 Zaman: 2026-07-10 14:30:00
━━━━━━━━━━━━━━━━━
🚀 Sinyal: SÜPER BOĞA
📊 Şiddet: 🔥 GÜÇLÜ
━━━━━━━━━━━━━━━━━
🐂 Bull Div: 5/5
🐻 Bear Div: 0/5
D1:▲ D2:▲ D3:▲ D5:▲ D6:▲
━━━━━━━━━━━━━━━━━
📈 Chartı Aç
#BTCUSDT
```

---

## 🧠 YENİ: Multi-Symbol Scanner (Tüm Piyasalar)

Tek bir chart'a bağlı kalmak yerine **tüm hisseleri/kriptoları otomatik tara**.

### Scanner Dosyaları

| Dosya | Açıklama |
|---|---|
| `rtug_scanner_core.py` | **Sinyal motoru** — OBV divergence hesaplama, breakout tespiti, conviction score |
| `rtug_multi_symbol_scanner.py` | **Multi-symbol tarayıcı** — yfinance + Binance'den veri indir, tüm sembolleri tara, Telegram'a raporla |

### Desteklenen Piyasalar

| Piyasa | Kaynak | Sembol Sayısı |
|---|---|---|
| **BIST 100** 🇹🇷 | Yahoo Finance (`THYAO.IS`, `GARAN.IS`, ...) | 63 hisse |
| **US Stocks** 🇺🇸 | Yahoo Finance (`AAPL`, `META`, ...) | 35 hisse |
| **Kripto** ₿ | Binance (ccxt) — BTC, ETH, SOL, XRP, DOGE, ... | 30 coin |

### Kullanım

```bash
# Tüm piyasaları tara
python rtug_multi_symbol_scanner.py

# Sadece BIST
python rtug_multi_symbol_scanner.py --bist

# Sadece US hisseleri (paralel, hızlı)
python rtug_multi_symbol_scanner.py --us --fast

# Sadece kripto
python rtug_multi_symbol_scanner.py --crypto --fast

# Telegram'a göndermeden sadece konsola yazdır
python rtug_multi_symbol_scanner.py --us --no-telegram
```

### Output Örneği

```
🔔 RTUG TARAMA SONUÇLARI
📂 Kaynak: US Stocks
📊 Sinyal: 18 sembol
━━━━━━━━━━━━━━━━━
🟢 MSTR | BOĞA KIRILIMI    🐂5/5 🐻0/5 | Skor: 100% | $93.96
🚀 KONTR.IS | SÜPER BOĞA    🐂5/5 🐻0/5 | Skor: 100%
🔴 AAPL | AYI KIRILIMI      🐂0/5 🐻5/5 | Skor: 25%  | $314.35
⚡ ADBE | HIZLI AŞAĞI KESİŞ 🐂4/5 🐻1/5 | Skor: 87%
━━━━━━━━━━━━━━━━━
📈 RTUG BREAKOUT SCANNER
```

### n8n ile Periyodik Tarama

`rtug-scheduled-scanner.json` workflow'unu içe aktar:
1. n8n → **Import from File**
2. Zamanlayıcı: her saat başı çalışır (isteğe göre ayarlanabilir)
3. Telegram'a otomatik rapor gönderir

### Telegram Token (.env)

Scanner'ın Telegram'a mesaj göndermesi için:

```bash
# Örnek .env dosyasını kopyala
copy .env.rtug.example .env
```

`.env` dosyasını düzenle:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz   ← @BotFather'dan al
TELEGRAM_CHAT_ID=6988108865                                  ← mevcut chat ID'n
```

Bot token'ını yoksa Telegram @BotFather'dan al. Chat ID'n sabit (`6988108865`).

---

## 🩺 Test (n8n Webhook)

Workflow'u test etmek için:

```bash
# Webhook'u simüle et
curl -X POST http://localhost:5678/webhook/rtug-breakout \
  -H "Content-Type: application/json" \
  -d '{"ticker":"BTCUSDT","close":"65432","type":"SUPER_BULLISH","bull_count":5,"bear_count":0,"d1":1,"d2":1,"d3":1,"d5":1,"d6":1,"time":"2026-07-10 14:30"}'
```

Telegram'a mesaj gitmeli ✅

---

## 📋 Alert Tipleri

| Alert | Koşul | Şiddet |
|---|---|---|
| **Bullish Breakout** 🟢 | 4+/5 divergence pozitif + OBV artıyor | Normal |
| **Bearish Breakout** 🔴 | 4+/5 divergence negatif + OBV düşüyor | Normal |
| **Super Bullish** 🚀 | 5/5 divergence bullish + OBV > 0.3 | Yüksek |
| **Super Bearish** 🔻 | 5/5 divergence bearish + OBV < -0.3 | Yüksek |
| **Fast Div Cross Up** ⚡ | Div6 sıfır çizgisini yukarı keser | Anlık |
| **Fast Div Cross Down** ⚡ | Div6 sıfır çizgisini aşağı keser | Anlık |
| **Momentum Bullish** 📊 | Bullish divergence sayısı aniden artar | Uyarı |
| **Momentum Bearish** 📊 | Bearish divergence sayısı aniden artar | Uyarı |

---

## 🔄 Alternatif: localhost çalışırsa Python Bot

Eğer localhost erişilebilir durumdaysa:
```bash
python rtug_telegram_bot.py
```
Webhook: `http://localhost:5000/webhook`

---

# 🎯 YENİ: RTUG COLOR SURROUND DETECTOR

## Nedir?

RTUG OBV NEON indikatöründe renklerin birbirini "sarması" (surround) patterni.
Bu pattern, farklı zaman dilimlerindeki divergence'ların renk kodları sayesinde
görsel olarak fark edilmeyebilecek durumları tespit eder.

## Renk Kodu Sistemi

| Div | Periyot | YUKARI Renk | AŞAĞI Renk | Anlamı |
|-----|---------|-------------|-------------|--------|
| Div1 | 100/20 | 🟣 **Mor** | 🩷 Pembe | **En yavaş** — büyük trend |
| Div2 | 70/15 | 🔴 **Kırmızı** | 🟠 Turuncu | **Orta** — trend onayı |
| Div3 | 50/20 | 🟢 Yeşil | 🟡 Sarı | Orta-hızlı |
| Div5 | 15/5 | 🩷 Pembe | 🟣 **Mor** | Hızlı #2 |
| Div6 | 8/3 | 🔵 **Mavi** | 🟤 Kahve | **En hızlı** — anlık momentum |
| Core | — | ⚪ **Beyaz** | ⚪ Beyaz | Tüm div'lerin merkez çizgisi |

## Tespit Edilen Pattern'ler

### 🟢 BOĞA SARMA (Mor+Mavi Kırmızıyı Sardı)
```
Div1(Mor)  ↑ — Uzun vade BOĞA
Div6(Mavi) ↑ — Kısa vade BOĞA
Div2(Kırmızı) ↓ — Orta vade AYI (sıkıştı!)
→ Düşüş bitiyor, ALIM bölgesi
```

### 🔴 AYI SARMA (Pembe+Kahve Kırmızıyı Sardı)
```
Div1(Pembe)  ↓ — Uzun vade AYI
Div6(Kahve)  ↓ — Kısa vade AYI
Div2(Kırmızı) ↑ — Orta vade BOĞA (sıkıştı!)
→ Yükseliş bitiyor, SAT bölgesi
```

### 🟣 DERİN SARMA (4/5 Divergence Consensus)
5 divergence'ın 4+'ü aynı yönü gösterir, sadece 1 tanesi ters.
Ters olan divergence yakında dönecek demektir — güçlü sinyal.

### 🔵 TERS DAİRE SARMA (Reverse Circles)
Reverse divergences (Band B'deki daireler) forward divergences'ların
(Band A'daki çizgiler) tersini söylüyorsa bu bir **uyarı** sinyalidir.

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `rtug_color_surround.pine` | **Pine Script** — TradingView'de renk surround tespiti + 12 alert condition |
| `rtug_scanner_core.py` | **Python Core** — Color surround engine (güncellendi) |
| `rtug_multi_symbol_scanner.py` | **Multi-Scanner** — Surround pattern'leri de tarar + Telegram bildirimi (güncellendi) |

## TradingView'de Kullanım

1. Pine Editor'da `rtug_color_surround.pine` içeriğini yapıştır
2. **Save** → İsim: `RTUG COLOR SURROUND`
3. Chart'a ekle: **Indicators → RTUG COLOR SURROUND**
4. **Alert** oluştur: Sağ tık → Add Alert → Condition: RTUG COLOR SURROUND'dan
   - `BULLISH SURROUND (Purple+Blue wrap Red)` 🟢
   - `BEARISH SURROUND (Pink+Brown wrap Red)` 🔴
   - `STRONG BULLISH SURROUND` 🟢
   - `DEEP BULLISH SURROUND` 🟣
   - `REVERSE CIRCLE BULLISH` 🔵

## Python Scanner

```bash
# Color Surround dahil tüm sinyaller taranır
python rtug_multi_symbol_scanner.py --fast --no-telegram
```
