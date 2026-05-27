@echo off
chcp 65001 >nul
title RSOD Platform

echo.
echo ================================
echo   RSOD Platform Launcher
echo ================================
echo.

echo [1/3] Starting Docker services...
docker-compose up -d

echo [2/3] Starting Backend...
powershell -Command "Start-Process -WindowStyle Hidden -FilePath 'powershell' -ArgumentList '-Command', 'cd \"%~dp0backend\"; python -m uvicorn main:app --reload --port 8000'"

echo [3/3] Starting Frontend...
powershell -Command "Start-Process -WindowStyle Hidden -FilePath 'powershell' -ArgumentList '-Command', 'cd \"%~dp0frontend\"; npx vite --host'"

echo.
echo ================================
echo   All services started!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo ================================
echo.
echo Press any key to close this window (services keep running)...
pause >nul
exit
