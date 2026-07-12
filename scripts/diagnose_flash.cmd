@echo off
title CMD Flash Diagnoz
color 0F
echo ============================================
echo    CMD FLASH PENCCERESI DIAZNOZ ARACI
echo ============================================
echo.

echo [1] Scheduled Tasks - Basarisiz olanlar:
echo -----------------------------------------
schtasks /query /fo LIST /v | findstr /B /C:"GorevYolu" /C:"GorevAdi" /C:"Sonuc" /C:"SonCalismaZamani" /C:"Durum"
echo.

echo [2] Startup klasoru:
echo --------------------
dir "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" 2>nul
dir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup" 2>nul
echo.

echo [3] Registry Run keys:
echo -----------------------
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" 2>nul
echo.
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" 2>nul
echo.

echo [4] Son 50 sistem olayi (Event ID 1000,1001,1002):
echo --------------------------------------------------
wevtutil qe System /q:"*[System[(EventID=1000 or EventID=1001 or EventID=1002)]]" /c:10 /f:text /rd:true 2>nul
echo.

echo [5] Son 50 uygulama hatasi:
echo ----------------------------
wevtutil qe Application /q:"*[System[(Level=2)]]" /c:10 /f:text /rd:true 2>nul
echo.

echo ============================================
echo YUKARIDAKI CIKTILARI KOPYALA VE BANA GONDER
echo ============================================
pause
