@echo off

:loop

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set DATETIME=%%i

set BACKUPDIR=D:\MinecraftAutoBackUp\%DATETIME%

mkdir "%BACKUPDIR%"

robocopy "." "%BACKUPDIR%" /E /XF session.lock /XD cache logs

timeout /t 600 /nobreak >nul

goto loop