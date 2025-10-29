@echo off
setlocal enabledelayedexpansion

REM Git Auto-Push for vibe_coding folder
REM Runs faster with minimal output for shutdown scenarios

set REPO_PATH=Z:\vibe_coding
set REMOTE_NAME=origin
set BRANCH_NAME=main
set GIT_USERNAME=Goutam-aswani
set GIT_EMAIL=goutamaswani43@gmail.com

REM Silent mode - only show errors
cd /d "%REPO_PATH%" 2>nul
if errorlevel 1 exit /b 0

REM Quick config
git config user.name "%GIT_USERNAME%" 2>nul
git config user.email "%GIT_EMAIL%" 2>nul
git config --global credential.helper manager 2>nul

REM Check for changes (fast check)
git status --porcelain > temp_status.txt 2>nul
for %%A in (temp_status.txt) do set STATUS_SIZE=%%~zA
del temp_status.txt 2>nul

if %STATUS_SIZE%==0 (
    REM No changes, just ensure we're synced
    git push %REMOTE_NAME% %BRANCH_NAME% >nul 2>&1
    exit /b 0
)

REM Stage, commit, and push
git add . >nul 2>&1
git commit -m "Auto commit - %date% %time%" >nul 2>&1
git push %REMOTE_NAME% %BRANCH_NAME% >nul 2>&1

exit /b 0
