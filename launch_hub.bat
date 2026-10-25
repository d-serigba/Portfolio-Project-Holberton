start cmd /k "cd /d %~dp0docs\api && py app.py"
timeout /t 3
start http://127.0.0.1:5000
pause
