# SİNGULARİTY ENGİNE KULLANIM KILAVUZU
## Hiçbir şey bilmeyen biri için adım adım

---

# 1. GİRİŞ — BU SİSTEM NE İŞE YARAR?

Bu bir **AI yazılım asistanı** sistemidir. Şu işleri yapar:

- **Sana kod yazar** (web sitesi, oyun, bot, her şey)
- **Kendini otomatik yedekler** (çökerse geri gelirsin)
- **AI'ya komut verirken en iyi yöntemleri kullanır**
- **Her şeyi tek bir yerden yönetirsin**

---

# 2. SİSTEMİ BAŞLATMAK

## 2.1 İlk Adım — OpenCode'u Aç

Masaüstündeki "open code mode" klasörüne git.
Burada bir terminal aç (sağ tık → Terminal'de aç).
Şu komutu yaz:

```
opencode
```

Açıldığında karşında bir sohbet ekranı olacak. İşte burada komut yazıyorsun.

## 2.2 Ne Zaman Ne Kullanacağın

Her şey için tek bir komut var: **`/uw5`**

```
/uw5 bana bir web sitesi yap
/uw5 backup al
/uw5 kodumu kontrol et
```

`/uw5` ne istediğini anlar ve doğru yere yönlendirir.

---

# 3. YEDEKLEME SİSTEMİ (SNA) — EN ÖNEMLİ KISIM

## 3.1 Otomatik Yedekleme (Hiçbir Şey Yapmana Gerek Yok)

Bilgisayar her açıldığında, Windows otomatik olarak bir script çalıştırır.
Bu script senin tüm AI sistemini yedekler.
Hiçbir şey yapmana gerek yok. Sadece bilgisayarı aç, o işi halleder.

**Ne yedeklenir:**
- Bütün komut ayarların
- Bütün AI becerilerin (skill)
- Bütün script'lerin
- Bütün MCP sunucu ayarların
- Kimlik doğrulama bilgilerin
- OpenCode veritabanın

**Kaç yedek kalır:** Son 5 yedek saklanır, eskiler otomatik silinir.

## 3.2 Manuel Yedek Alma

İstersen kendin de yedek alabilirsin. Terminalde şunu yaz:

```
.\scripts\sna-backup.ps1
```

**Farklı seçenekler:**

| Komut | Ne Yapar |
|-------|----------|
| `.\scripts\sna-backup.ps1` | Normal yedek (config + script + command + skills) |
| `.\scripts\sna-backup.ps1 -Quick` | Sadece ayarları yedekle (çok hızlı) |
| `.\scripts\sna-backup.ps1 -Full` | Her şeyi yedekle (cache dahil, uzun sürebilir) |
| `.\scripts\sna-backup.ps1 -Name "önemli an"` | Yedeğe isim ver |

Veya `/uw5` üzerinden de aynısını yapabilirsin:

```
/uw5 yedek al
/uw5 hızlı yedek
/uw5 tam yedek
```

## 3.3 Sistem Çökerse — Geri Yükleme

**DİKKAT: EN ÖNEMLİ KISIM**

Sistem bozulursa veya yeni bilgisayara geçersen:

### Yöntem 1 — Tek Komutla (En Kolay)

Terminalde şunu yaz:

```
.\scripts\sna-restore.ps1
```

Bu, son yedeğini bulur ve her şeyi geri yükler. İşlem bitince OpenCode'u kapatıp tekrar aç.

### Yöntem 2 — Kendin Seçerek

Önce hangi yedekler var gör:

```
.\scripts\sna-restore.ps1 -List
```

Çıktıda şuna benzer şeyler göreceksin:
```
[2026-07-07 15:52] sna-full-20260707_155221 - 6.515 MB
[2026-07-07 15:31] sna-boot-20260707_153036 - 6.510 MB
```

İstediğini şöyle geri yükle:

```
.\scripts\sna-restore.ps1 -From "C:\Users\cagda\.opencode-backups\sna-full-20260707_155221"
```

### Yöntem 3 — Yedek Klasöründen Direkt

Her yedek klasörünün içinde kendi `restore.ps1`'i var.

```
cd C:\Users\cagda\.opencode-backups\sna-full-20260707_155221\
.\restore.ps1
```

### Yöntem 4 — /uw5 ile

```
/uw5 geri yükle
/uw5 restore et
/uw5 yedeklerimi göster
```

## 3.4 Yedekler Nerede Duruyor?

Hepsi şurada:
```
C:\Users\cagda\.opencode-backups\
```

Her yedek kendi klasöründe. İçinde:
- `config/` — ayar dosyaların
- `scripts/` — script'lerin
- `skills/` — AI becerilerin
- `opencode-plugins/` — eklentilerin
- `custom-commands/` — özel komutların
- `cache-core/` — önbellek ve veritabanın
- `restore.ps1` — geri yükleme script'i (her yedekte var)

---

# 4. KOMUT SİSTEMİ

## 4.1 Tüm Komutlar

Eğer `/uw5` yazarsan, ne istediğini otomatik anlar. Ama istersen spesifik komutlar da var:

### AI Geliştirme Komutları (Vibe Coding)

| Komut | Ne Yapar |
|-------|----------|
| `/vibe-loop` | 6 adımda AI ile kod geliştirme döngüsü başlatır |
| `/vibe-prompt` | AI'ya en iyi nasıl komut yazacağını gösterir |
| `/vibe-quality` | Kod kalitesini kontrol etmeyi gösterir |
| `/vibe-debug` | Hata bulma yöntemlerini gösterir |
| `/vibe-checklist` | İşi bitirmeden önce kontrol listesi sunar |
| `/vibe-safety` | Güvenlik kurallarını gösterir |

### Awesome Claude (AI Bilgi Kaynağı)

| Komut | Ne Yapar |
|-------|----------|
| `/ac` | Tüm Awesome Claude kaynaklarına açılan kapı |
| `/ac-cheatsheet` | Claude Code'un tüm kısayol ve komutları |
| `/ac-skills` | 169 tane AI becerisinin listesi |
| `/ac-mcp` | Popüler MCP sunucuları ve kurulumları |
| `/ac-ralph` | Sürekli AI döngüsü tekniği |
| `/ac-community` | Topluluk listeleri ve kaynaklar |
| `/ac-official` | Resmi Anthropic kaynakları |

### Diğer Komutlar

| Komut | Ne Yapar |
|-------|----------|
| `/compact` | Konuşma geçmişini temizler (bellek tasarrufu) |
| `/review` | Son kod değişikliklerini kontrol eder |
| `/scan` | Güvenlik taraması yapar |
| `/build` | Projeyi derler |
| `/explain` | Seçili kodu açıklar |
| `/sessions` | Geçmiş konuşmaları listeler |

---

# 5. BASİT KULLANIM SENARYOLARI

## 5.1 "Bana bir web sitesi yap"

Terminale yaz:

```
/uw5 bana bir landing page yap, mavi temalı, GSAP animasyonlu
```

Sistem senin için kodu yazar, dosyayı oluşturur.

## 5.2 "Boot yedeği alındı mı?"

Kontrol etmek için:

```
.\scripts\sna-restore.ps1 -List
```

Eğer `sna-boot-` ile başlayan bir yedek varsa, boot yedeği alınmış demektir.

## 5.3 "Sistem bozuldu, geri dönmem lazım"

```
.\scripts\sna-restore.ps1
```

## 5.4 "Bir Python script'i yaz"

```
/uw5 bana bir to-do list API'si yaz Python Flask ile
```

---

# 6. SİSTEMİN MANTIĞI (ÖZET)

1. **Her boot'ta yedek alınır** → Hiçbir şey kaybolmaz
2. **`/uw5` her şeyi anlar** → Ne istersen o olur
3. **Vibe Coding** → AI'dan kaliteli kod almanın formülü
4. **Awesome Claude** → AI hakkında her şey burada

---

# 7. ACİL DURUM PROSEDÜRÜ

Eğer sistem tamamen çöktüyse ve OpenCode bile açılmıyorsa:

1. Dosya Gezgini'ni aç
2. Şuraya git: `C:\Users\cagda\.opencode-backups\`
3. En son tarihli klasörü bul (ör: `sna-full-20260707_155221`)
4. İçindeki `restore.ps1`'e çift tıkla
5. PowerShell açılır, her şeyi geri yükler
6. OpenCode'u tekrar aç — her şey yerinde

---

# 8. ÖNEMLİ UYARILAR

- **Yedekler silinmez** — sadece son 5'in dışındaki boot yedekleri silinir
- **Manuel yedekler** (`sna-full-*`) hiçbir zaman otomatik silinmez
- **Yeni bilgisayara geçerken** yedek klasörünü USB'ye kopyala, yeni bilgisayarda restore et
- **Her şey tek bir yerde** — hem yedekler, hem script'ler, hem komutlar
