@echo off
cd /d %~dp0

:: 1. Génère le .env au premier lancement uniquement
if not exist "%~dp0docs\api\.env" (
    echo [INFO] Premier lancement : generation des cles secretes...
    py -3.12 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32)); print('JWT_SECRET_KEY=' + secrets.token_hex(32))" > "%~dp0docs\api\.env"
    echo [INFO] Fichier .env cree.
)

:: 2. Lance l'API
echo [INFO] Lancement de l'API Flask...
start cmd /k "cd /d %~dp0docs\api && set DISABLE_SQLALCHEMY_CEXT=1 && py -3.12 app.py"

:: 3. Laisse le serveur démarrer
timeout /t 3 /nobreak >nul

:: 4. Ouvre le navigateur
echo [INFO] Ouverture du navigateur...
start http://127.0.0.1:5000
