@echo off
cd /d "%~dp0"
echo [INFO] Lancement de l'API Flask...
start "Flask" python app.py
timeout /t 3 /nobreak >nul
echo [INFO] Ouverture du navigateur...
start http://127.0.0.1:5000
