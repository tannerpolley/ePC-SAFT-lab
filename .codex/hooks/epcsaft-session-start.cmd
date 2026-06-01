@echo off
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0epcsaft-session-start.ps1"
exit /b %ERRORLEVEL%
