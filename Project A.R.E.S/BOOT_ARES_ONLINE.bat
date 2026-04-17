@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d %~dp0

echo ======================================
echo           PROJECT ARES BOOT
echo ======================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ARES] Python is not installed or not on PATH.
  echo [ARES] Install Python 3.11+ and rerun this file.
  pause
  exit /b 1
)

where ollama >nul 2>nul
if errorlevel 1 (
  echo [ARES] Ollama is not installed.
  echo [ARES] Download it from https://ollama.com and rerun this file.
  pause
  exit /b 1
)

if not exist .venv (
  echo [ARES] Creating Python environment...
  python -m venv .venv
  if errorlevel 1 goto :fail
)

call .venv\Scripts\activate
if errorlevel 1 goto :fail

echo [ARES] Installing dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo [ARES] Checking Ollama service...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 2; exit 0 } catch { exit 1 }"
if errorlevel 1 (
  echo [ARES] Starting Ollama in the background...
  start "ARES Ollama" /min cmd /c "ollama serve"
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddSeconds(20); do { try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 2 | Out-Null; exit 0 } catch { Start-Sleep -Milliseconds 750 } } while((Get-Date) -lt $deadline); exit 1"
  if errorlevel 1 (
    echo [ARES] Ollama did not start in time.
    pause
    exit /b 1
  )
)

echo [ARES] Checking local models...
set MODEL_FOUND=
for /f "usebackq delims=" %%M in (`ollama list 2^>nul ^| findstr /R /C:"llama3.1:8b" /C:"qwen2.5:7b" /C:"phi3:mini"`) do set MODEL_FOUND=1
if not defined MODEL_FOUND (
  echo [ARES] No recommended ARES model was found.
  echo [ARES] Pulling phi3:mini now for the fastest first boot...
  ollama pull phi3:mini
  if errorlevel 1 (
    echo [ARES] Model download failed.
    pause
    exit /b 1
  )
)

echo [ARES] Starting ARES server...
start "ARES Server" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [ARES] Waiting for ARES to come online...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddSeconds(25); do { try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health -TimeoutSec 2; if($r.StatusCode -eq 200){ exit 0 } } catch { Start-Sleep -Milliseconds 750 } } while((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 (
  echo [ARES] Server did not become ready in time.
  echo [ARES] Check the 'ARES Server' window for details.
  pause
  exit /b 1
)

echo [ARES] Opening browser...
start "" http://127.0.0.1:8000

echo.
echo [ARES] ARES is online.
echo [ARES] Keep the 'ARES Server' window open while using it.
goto :eof

:fail
echo.
echo [ARES] Boot failed.
pause
exit /b 1
