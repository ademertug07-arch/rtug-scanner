@echo off
title RTUG DAEMON DURUM
echo ========================================
echo  RTUG SURROUND DAEMON - DURUM KONTROLU
echo ========================================
echo.

wmic process where "name='python.exe' and commandline like '%%rtug_surround_daemon%%'" get processid,commandline /format:list 2>nul | findstr /i "processid commandline"

echo.
if errorlevel 1 (
    echo ❌ Daemon calismiyor!
    echo Baslatmak icin: start_daemon.bat
) else (
    echo ✅ Daemon aktif
)

echo.
echo ========================================
echo  SON TARAMA KAYITLARI
echo ========================================
if exist daemon_output.log (
    findstr /i "YENI\|BIST\|ABD\|Crypto\|hata\|HATA" daemon_output.log 2>nul
    echo.
    echo Detayli log: daemon_output.log
) else (
    echo Log dosyasi bulunamadi.
)
echo.
