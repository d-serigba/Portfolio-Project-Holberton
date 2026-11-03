@echo off
cd /d %~dp0

:: 1. Force SQLAlchemy en mode 100% pur Python pour éviter le plantage sur Python 3.12
set DISABLE_SQLALCHEMY_CEXT=1

:: 2. Nettoie le fichier C récalcitrant dans ton Python global s'il est présent
python -c "import pathlib; [p.unlink() for p in pathlib.Path(r'C:\Users\kirbs\AppData\Local\Programs\Python\Python312\Lib\site-packages\sqlalchemy').rglob('*_cy*') if p.is_file()]" 2>nul

echo [INFO] Lancement de l'API Flask...
start cmd /k "cd /d %~dp0docs\api && set DISABLE_SQLALCHEMY_CEXT=1 && py -3.12 app.py"

:: 3. Petite pause pour laisser le serveur démarrer
timeout /t 3 /nobreak >nul

echo [INFO] Ouverture du navigateur...
start http://127.0.0.1:5000
