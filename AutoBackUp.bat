@echo off
title Minecraft Auto Backup

echo Minecraft 자동 백업 스크립트 시작...

:loop
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set DATETIME=%%i

set BACKUPDIR=D:\MinecraftAutoBackUp\%DATETIME%

echo [%date% %time%] 백업 시작: %BACKUPDIR%

mkdir "%BACKUPDIR%"

robocopy "." "%BACKUPDIR%" /E /XF session.lock *.log /XD cache logs backups plugins/update /MT:4 /R:2 /W:5

echo [%date% %time%] 백업 완료

:: 10분마다 실행
timeout /t 600 /nobreak >nul

goto loop