@echo off
title Restaurant Management System (RMS Pro)
echo ===================================================
echo   Restaurant Management System - Starting Server
echo ===================================================
echo.

cd /d "%~dp0backend"
echo Checking Python dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo Starting Flask Server at http://127.0.0.1:5000/
echo Opening Owner Portal in default web browser...
start http://127.0.0.1:5000/

python app.py
pause
