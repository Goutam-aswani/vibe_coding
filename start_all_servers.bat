@echo off
REM Start all servers using individual batch files
echo Starting all servers...

REM n8n and ngrok
call start_n8n.bat
timeout /t 2 /nobreak >nul
call start_ngrok.bat
timeout /t 1 /nobreak >nul

REM Email scraper
call start_email_scraper.bat
timeout /t 1 /nobreak >nul

REM Megascraper email verifier
call start_megascraper.bat
timeout /t 1 /nobreak >nul

REM Job board scrapers
call start_dice_scraper.bat
timeout /t 1 /nobreak >nul
call start_foundit_scraper.bat
timeout /t 1 /nobreak >nul
call start_hirist_scraper.bat
timeout /t 1 /nobreak >nul
call start_naukri_scraper.bat

echo.
echo All servers started!
echo Press any key to exit...
pause >nul  