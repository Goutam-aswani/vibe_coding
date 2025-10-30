@echo off
REM ============================================================================
REM Email Verifier API - Quick Start (Port 8001)
REM ============================================================================
REM This script can be run from anywhere - it will find its own location
REM ============================================================================

REM Save current directory and change to script's directory
pushd "%~dp0"

echo.
echo ======================================================================
echo Starting Email Verifier API on http://localhost:8001
echo ======================================================================
echo.
echo API Documentation: http://localhost:8001/docs
echo Health Check: http://localhost:8001/health
echo.
echo Press CTRL+C to stop the server
echo ======================================================================
echo.

REM Start uvicorn directly with port 8002 using absolute path
"%~dp0..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

REM Return to original directory
popd

pause
