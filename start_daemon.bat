@echo off
title RTUG SURROUND DAEMON (5dk)
echo ========================================
echo  RTUG SURROUND DAEMON BASLATILIYOR
echo  Interval: 5 dakika
echo  Tarih: %date% %time%
echo ========================================
echo.

set TELEGRAM_BOT_TOKEN=8882842172:AAFw6HTJVB6fXndUjH_D4wJpgXoqh6GIZI
set TELEGRAM_CHAT_ID=6988108865

start /B python rtug_surround_daemon.py --interval 5 > daemon_output.log 2>&1

echo ✅ Daemon arka planda calisiyor.
echo    PID: (yukaridaki python process)
echo    Log: daemon_output.log
echo.
echo Durdurmak icin: stop_daemon.bat
echo.
