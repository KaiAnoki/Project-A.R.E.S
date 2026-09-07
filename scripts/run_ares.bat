@echo off
setlocal
cd /d %~dp0\..
if not exist .venv (
  echo [ARES] Creating virtual environment...
  python -m venv .venv || goto :fail
)
call .venv\Scripts\activate || goto :fail
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt || goto :fail
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
goto :eof
:fail
echo.
echo [ARES] Startup failed.
pause
exit /b 1
