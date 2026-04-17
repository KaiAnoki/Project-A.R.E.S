@echo off
echo [ARES] Stopping local ARES windows if they are open...
taskkill /FI "WINDOWTITLE eq ARES Server" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq ARES Ollama" /T /F >nul 2>nul
echo [ARES] Done.
pause
