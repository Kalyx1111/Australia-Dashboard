@echo off
setlocal EnableExtensions
title AUSTRALIA DASHBOARD
cd /d "%~dp0"

cls
echo.
echo ============================================================
echo              AUSTRALIA DASHBOARD
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found. Install it from https://python.org
    echo and make sure "Add python.exe to PATH" is checked during setup.
    echo.
    pause
    exit /b 1
)
echo [OK] Python detected.
echo.

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment - first run only, happens once...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create the virtual environment.
        pause
        exit /b 1
    )
)
echo [OK] Virtual environment ready.
echo.

echo Checking required Python packages...
"venv\Scripts\python.exe" -m pip install -r requirements.txt --disable-pip-version-check -q
if errorlevel 1 (
    echo [ERROR] Failed to install required packages.
    pause
    exit /b 1
)
echo [OK] Dependencies ready.
echo.

start "AUSTRALIA DASHBOARD - SERVER (auto-restart on crash)" cmd /k "cd /d ""%~dp0"" && venv\Scripts\python.exe supervisor.py"

echo Waiting for the server on port 8830...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ready=$false; for($i=1;$i -le 40;$i++){ try { $r=Invoke-WebRequest -Uri 'http://127.0.0.1:8830/' -UseBasicParsing -TimeoutSec 1; if($r.StatusCode -ge 200 -and $r.StatusCode -lt 500){$ready=$true;break} } catch {}; Start-Sleep -Seconds 1 }; if($ready){exit 0}else{exit 1}"

if errorlevel 1 (
    echo.
    echo [ERROR] Server did not respond on port 8830. Check the SERVER window.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   AUSTRALIA DASHBOARD IS ONLINE - http://127.0.0.1:8830/
echo ============================================================
echo.
start "" "http://127.0.0.1:8830/"
timeout /t 3 /nobreak >nul
exit /b 0
