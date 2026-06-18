@echo off
setlocal

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5678" ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F
)

endlocal
