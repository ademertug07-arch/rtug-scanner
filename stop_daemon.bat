@echo off
title RTUG DAEMON DURDUR
echo ========================================
echo  RTUG SURROUND DAEMON DURDURULUYOR
echo ========================================
echo.

:: Tum rtug_surround_daemon.py process'lerini bul ve oldur
for /f "tokens=2 delims=," %%a in ('wmic process where "name='python.exe' and commandline like '%%rtug_surround_daemon%%'" get processid /format:csv 2^>nul') do (
    taskkill /PID %%a /F 2>nul
    echo Durduruldu: PID %%a
)

echo.
echo ✅ Daemon durduruldu.
echo.
