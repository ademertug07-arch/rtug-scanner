Write-Host "=== CMD FLASH DİAGNOZ SCRIPTİ ===" -ForegroundColor Cyan
Write-Host "Çalıştırma: Yönetici PowerShell'de bu dosyaya sağ tık > PowerShell ile çalıştır" -ForegroundColor Yellow
Write-Host ""

# 1. Event Viewer'da son hatalar
Write-Host "`n[1] Event Viewer - Son 24 saat Application hataları:" -ForegroundColor Green
Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=(Get-Date).AddDays(-1); Level=2} -MaxEvents 20 -ErrorAction SilentlyContinue | 
    Select-Object TimeCreated, Id, ProviderName, Message | Format-Table -Wrap -AutoSize

Write-Host "`n[2] Event Viewer - Son 24 saat System hataları:" -ForegroundColor Green
Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).AddDays(-1); Level=2} -MaxEvents 20 -ErrorAction SilentlyContinue | 
    Select-Object TimeCreated, Id, ProviderName, Message | Format-Table -Wrap -AutoSize

# 2. Scheduled tasks - başarısız olanlar
Write-Host "`n[3] Scheduled Tasks - Başarısız olanlar:" -ForegroundColor Green
schtasks /query /fo CSV /v 2>$null | ConvertFrom-Csv | Where-Object {
    $_.'Sonuç' -ne '0' -and $_.'Sonuç' -ne '267011' -and $_.Durum -ne 'Devre Dışı'
} | Select-Object 'Görev Yolu', 'Görev Adı', 'Son Çalışma Zamanı', 'Sonuç' | Format-Table -AutoSize

# 3. Startup programs
Write-Host "`n[4] Startup Programs:" -ForegroundColor Green
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-Table -AutoSize

# 4. Registry Run keys
Write-Host "`n[5] Registry Run Keys:" -ForegroundColor Green
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue | Format-List
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue | Format-List
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce" -ErrorAction SilentlyContinue | Format-List

# 5. Check Windows Update corruption
Write-Host "`n[6] Windows Update Agent kontrolü:" -ForegroundColor Green
dism /online /cleanup-image /checkhealth /quiet 2>$null
Write-Host "(Yukarıdaki komut tamamlandıysa sorun yok)"

# 6. Common problematic tasks
Write-Host "`n[7] Sık görülen problemli taskler:" -ForegroundColor Green
$problematicTasks = @(
    "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
    "\Microsoft\Windows\Windows Update\Automatic App Update",
    "\Microsoft\Office\Office Automatic Updates 2.0",
    "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector",
    "\Microsoft\Windows\Location\Notifications",
    "\Microsoft\Windows\CloudExperienceHost\CreateObjectTask",
    "\Microsoft\Windows\Shell\FamilySafetyMonitor",
    "\Microsoft\Windows\Shell\FamilySafetyRefresh"
)
foreach ($task in $problematicTasks) {
    $t = Get-ScheduledTask -TaskPath (Split-Path $task -Parent) -TaskName (Split-Path $task -Leaf) -ErrorAction SilentlyContinue
    if ($t) {
        $info = Get-ScheduledTaskInfo -TaskName $t.TaskName -TaskPath $t.TaskPath -ErrorAction SilentlyContinue
        Write-Host "  $task : Durum=$($t.State) SonSonuç=$($info.LastTaskResult)" -ForegroundColor Yellow
    }
}

# 7. Çalışan process'lerin command line'ları (şüpheli cmd başlatmaları)
Write-Host "`n[8] Şüpheli cmd.exe / powershell çağrıları:" -ForegroundColor Green
Get-CimInstance Win32_Process -Filter "Name='cmd.exe' OR Name='powershell.exe'" | 
    Select-Object ProcessId, Name, CommandLine, CreationDate | Format-Table -Wrap -AutoSize

Write-Host ""
Write-Host "=== TAMAMLANDI ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Yukarıdaki çıktıyı bana gönder, sebebi bulup kalıcı çözüm sunayım." -ForegroundColor Magenta
