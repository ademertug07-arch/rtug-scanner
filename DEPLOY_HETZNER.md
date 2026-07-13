# RTUG Server — Hetzner VPS Deployment

> Hedef: 7/24 calisan, sadece %%70+ guvenli sinyalleri Telegram'a gonderir.

---

## 1. Hetzner'da VPS Olustur

1. [Hetzner Cloud Console](https://console.hetzner.cloud) — Hesap olustur, odeme ekle
2. New Project -> New Server -> **CX22** (2 vCPU, 4GB RAM, ~€4/ay)
3. Image: **Ubuntu 24.04 LTS**
4. SSH key ekle (veya email ile sifre al)
5. Create -> IP adresini not et

---

## 2. SSH ile Baglan

```bash
ssh root@<VPS_IP>
# Sifreyle girdiysen once SSH key ayarla
```

---

## 3. Sistemi Hazirla

```bash
# Kullanici olustur
adduser rtug
usermod -aG sudo rtug

# Python3 paketleri
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git curl

# Dizini olustur
mkdir -p /opt/rtug/logs /opt/rtug/.rtug-memory /opt/rtug/.rtug-backtest /opt/rtug/.rtug-alerts
chown -R rtug:rtug /opt/rtug
```

---

## 4. Dosyalari Yukle

### Secenek A — GitHub (oneri)

```bash
# Yerelde git repo'ya ekle
git remote add vps rtug@<VPS_IP>:/opt/rtug

# Ya da direkt scp ile kopyala
# Yerel bilgisayarinda:
cd "C:\Users\cagda\OneDrive\Masaüstü\open code mode"
scp -r *.py *.txt .env requirements-vps.txt rtug.service rtug@<VPS_IP>:/opt/rtug/
scp -r .rtug-memory .rtug-backtest .rtug-alerts rtug@<VPS_IP>:/opt/rtug/
```

### Secenek B — SCP ile manuel

Yerel PowerShell'den:
```powershell
# RTUG dosyalarini VPS'e kopyala
scp -r C:\Users\cagda\OneDrive\Masaüstü\open code mode\*.py rtug@<VPS_IP>:/opt/rtug/
scp C:\Users\cagda\OneDrive\Masaüstü\open code mode\.env rtug@<VPS_IP>:/opt/rtug/
scp C:\Users\cagda\OneDrive\Masaüstü\open code mode\requirements-vps.txt rtug@<VPS_IP>:/opt/rtug/
scp C:\Users\cagda\OneDrive\Masaüstü\open code mode\rtug.service rtug@<VPS_IP>:/opt/rtug/

# Memory/backtest/alert data
scp -r C:\Users\cagda\OneDrive\Masaüstü\open code mode\.rtug-memory rtug@<VPS_IP>:/opt/rtug/
scp -r C:\Users\cagda\OneDrive\Masaüstü\open code mode\.rtug-backtest rtug@<VPS_IP>:/opt/rtug/
scp -r C:\Users\cagda\OneDrive\Masaüstü\open code mode\.rtug-alerts rtug@<VPS_IP>:/opt/rtug/
```

---

## 5. Python Ortami

```bash
ssh root@<VPS_IP>

cd /opt/rtug

# Sanal ortam (oneri)
python3 -m venv venv
source venv/bin/activate

# Bagimliliklari kur
pip install -r requirements-vps.txt

# Test et
python3 rtug_server.py --once
```

---

## 6. Systemd Servisi

```bash
# Servis dosyasini kopyala
cp /opt/rtug/rtug.service /etc/systemd/system/

# Yetkileri duzelt
chmod 644 /etc/systemd/system/rtug.service

# Servisi baslat
systemctl daemon-reload
systemctl enable rtug.service
systemctl start rtug.service

# Durum kontrol
systemctl status rtug.service
journalctl -u rtug.service -f
```

---

## 7. Log Goruntuleme

```bash
# Canli log
journalctl -u rtug.service -f

# Son 100 satir
journalctl -u rtug.service --no-pager -n 100

# Dosya logu
tail -f /opt/rtug/logs/rtug_server.log
```

---

## 8. Guvenlik (Opsiyonel)

```bash
# UFW firewall
ufw allow 22/tcp      # SSH
ufw allow 5000/tcp    # Webhook (TradingView)
ufw enable

# Fail2ban (SSH brute force koruma)
apt install fail2ban -y
```

---

## 9. Telegram Test

Servis calistiktan sonra Telegram'da bir mesaj gorurseniz calisiyordur.
Manuel test:
```bash
cd /opt/rtug && python3 -c "
import requests, os
from dotenv import load_dotenv
load_dotenv('.env')
token = os.environ['TELEGRAM_BOT_TOKEN']
chat = os.environ['TELEGRAM_CHAT_ID']
r = requests.post(f'https://api.telegram.org/bot{token}/sendMessage',
    json={'chat_id': chat, 'text': '<b>RTUG TEST — VPS calisiyor!</b>', 'parse_mode': 'HTML'})
print(r.status_code, r.text[:200])
"
```

---

## 10. Guncelleme

```bash
# Yeni surumu yukle
cd /opt/rtug
git pull  # veya scp ile yeni dosyalari gonder

# Servisi yeniden baslat
systemctl restart rtug.service
```

---

## SISTEM MIMARISI

```
VPS (7/24)
  ├── rtug_server.py
  │     ├── Monitor Thread (pattern tarama)
  │     │     ├── Confidence Gate (%%70+)
  │     │     ├── MTF Validator (%%40+)
  │     │     └── Alert Tracker (TP/FP)
  │     └── Flask Webhook (TradingView alert)
  │
  ├── .env (Telegram token)
  ├── .rtug-memory/ (pattern memory)
  ├── .rtug-alerts/ (alert logs)
  └── logs/ (rtug_server.log)

Telegram API  ←─── [Sadece %%70+ sinyaller]
```

> Not: %%70 confidence = pattern_match * 0.35 + MTF * 0.35 + history * 0.20 + volume_boost
