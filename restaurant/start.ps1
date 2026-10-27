# Restaurant Management System Launch Script
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Restaurant Management System (RMS Pro) Launcher" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\backend"

Write-Host "`n[+] Checking Python environment..." -ForegroundColor Green
python -m pip install -r requirements.txt --quiet

Write-Host "[+] Launching Flask Application on http://127.0.0.1:5000/ ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:5000/"

python app.py
