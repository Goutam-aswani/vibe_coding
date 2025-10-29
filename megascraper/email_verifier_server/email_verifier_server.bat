@echo off
REM ============================================================================
REM Email Verifier API Server Startup Script
REM ============================================================================
REM This script activates the virtual environment and starts the FastAPI server
REM on port 8002
REM This script can be run from anywhere - it will find its own location
REM ============================================================================

echo.
echo ======================================================================
echo Starting Email Verifier API Server on Port 8002
echo ======================================================================
echo.

REM Save current directory and change to script's directory
pushd "%~dp0"

REM Activate virtual environment using absolute path
echo Activating virtual environment...
call "%~dp0..\.venv\Scripts\activate.bat"

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    echo Please ensure the .venv folder exists in the parent directory.
    pause
    exit /b 1
)

echo Virtual environment activated!
echo.

REM Set the port to 8002
set PORT=8002

REM Start the server
echo Starting server on http://localhost:8002
echo API Documentation: http://localhost:8002/docs
echo.
python start.py

REM If server stops, deactivate venv
deactivate

REM Return to original directory
popd

echo.
echo Server stopped.
pause
