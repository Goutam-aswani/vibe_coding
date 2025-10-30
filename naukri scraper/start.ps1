# Naukri Job Scraper - Quick Start Script
# This script activates the virtual environment and starts the server

Write-Host "🚀 Starting Naukri Job Scraper..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Start the FastAPI server
Write-Host "📡 Launching FastAPI server..." -ForegroundColor Green
Write-Host "📍 Web Interface: http://localhost:8080" -ForegroundColor Yellow
Write-Host "📖 API Docs: http://localhost:8080/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Red
Write-Host ""

python main.py
