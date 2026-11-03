@echo off
cd /d %~dp0

echo [INFO] Lancement de l'API Flask...
start "API Flask" cmd /k "cd /d %~dp0docs\api && py -3.12 app.py"

timeout /t 3 /nobreak >nul

echo [INFO] Lancement du Hub...
cd /d %~dp0docs
py -3.12 main.py
