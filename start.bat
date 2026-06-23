@echo off
REM ============================================================
REM  RehearsalRoom - cukup Python, tidak perlu Node/PostgreSQL
REM  Dobel-klik file ini.
REM ============================================================
setlocal
cd /d "%~dp0rehearsalroom-backend"

if not exist "venv" (
    echo [Setup] Membuat virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo [Setup] Install dependencies ^(sekali saja, mohon tunggu^)...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

echo.
echo  ============================================
echo   RehearsalRoom siap!
echo   Database SQLite + data dummy dibuat otomatis.
echo   Buka browser ke:  http://localhost:8000
echo   Tekan CTRL+C di jendela ini untuk berhenti.
echo  ============================================
echo.

start "" http://localhost:8000
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
