@echo off
REM Quick setup script for Email Verifier API with auto-refresh

echo ======================================================================
echo Email Verifier API - Setup Script
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Installing Playwright browsers...
playwright install chromium
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Playwright browsers
    pause
    exit /b 1
)

echo.
echo [3/4] Checking .env configuration...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo Created .env file from template
    ) else (
        echo ERROR: .env.example not found
        pause
        exit /b 1
    )
) else (
    echo .env file already exists
)

echo.
echo [4/4] Setup complete!
echo.
echo ======================================================================
echo NEXT STEPS:
echo ======================================================================
echo.
echo 1. Edit .env file and set your credentials:
echo    - EMAILVERIFIER_EMAIL=your_email@example.com
echo    - EMAILVERIFIER_PASSWORD=your_password
echo.
echo 2. Test cookie refresh (optional):
echo    python refresh_cookie.py
echo.
echo 3. Start the server:
echo    python start.py
echo.
echo 4. Read the documentation:
echo    - README.md (main documentation)
echo    - COOKIE_AUTOREFRESH.md (cookie refresh guide)
echo.
echo ======================================================================
pause
