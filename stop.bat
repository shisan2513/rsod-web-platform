@echo off
chcp 65001 >nul
echo Stopping RSOD services...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    echo Killing frontend PID %%a
    taskkill /F /PID %%a 2>nul
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing backend PID %%a
    taskkill /F /PID %%a 2>nul
)

echo All services stopped.
timeout /t 2 /nobreak >nul
