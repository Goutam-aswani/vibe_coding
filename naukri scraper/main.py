"""
FastAPI Server for Naukri Job Scraper
Provides API endpoints and web interface for scraping Naukri.com job listings
"""
import asyncio
import sys
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
from pathlib import Path

from scraper_playwright import NaukriScraper

# Fix for Python 3.13 on Windows - use ProactorEventLoop for subprocess support
if sys.platform == 'win32' and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Initialize FastAPI app
app = FastAPI(
    title="Naukri Job Scraper API",
    description="Scrape job listings from Naukri.com by keyword",
    version="1.0.0"
)

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Initialize scraper
scraper = NaukriScraper()


# Request/Response Models
class JobSearchRequest(BaseModel):
    keywords: List[str] = Field(
        ..., 
        description="List of job roles/keywords to search for",
        example=["Python Developer", "Data Scientist"]
    )
    max_pages: Optional[int] = Field(
        default=3,
        ge=1,
        le=20,
        description="Maximum number of pages to scrape per keyword (1-20)"
    )
    results_per_page: Optional[int] = Field(
        default=20,
        ge=10,
        le=50,
        description="Number of results per page (10-50)"
    )


class JobSearchResponse(BaseModel):
    success: bool
    message: str
    total_keywords: int
    results: List[dict]


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/scrape", response_model=JobSearchResponse)
async def scrape_jobs(search_request: JobSearchRequest):
    """
    Scrape jobs from Naukri.com for given keywords
    
    **Parameters:**
    - keywords: List of job roles to search for
    - max_pages: Maximum pages per keyword (default: 3)
    - results_per_page: Results per page (default: 20)
    
    **Returns:**
    - Job listings data for each keyword
    """
    try:
        if not search_request.keywords:
            raise HTTPException(status_code=400, detail="At least one keyword is required")
        
        # Clean and filter empty keywords
        keywords = [k.strip() for k in search_request.keywords if k.strip()]
        
        if not keywords:
            raise HTTPException(status_code=400, detail="Valid keywords are required")
        
        # Scrape jobs
        results = await scraper.search_multiple_keywords(
            keywords=keywords,
            max_pages=search_request.max_pages,
            results_per_page=search_request.results_per_page
        )
        
        total_jobs = sum(r['jobs_scraped'] for r in results)
        
        return JobSearchResponse(
            success=True,
            message=f"Successfully scraped {total_jobs} jobs for {len(keywords)} keyword(s)",
            total_keywords=len(keywords),
            results=results
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")


@app.post("/scrape-form", response_class=HTMLResponse)
async def scrape_jobs_form(
    request: Request,
    keywords: str = Form(...),
    max_pages: int = Form(3)
):
    """
    Form submission endpoint for web interface
    Accepts comma-separated keywords
    """
    try:
        # Parse comma-separated keywords
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        
        if not keyword_list:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "Please enter at least one job role"
                }
            )
        
        # Scrape jobs
        results = await scraper.search_multiple_keywords(
            keywords=keyword_list,
            max_pages=max_pages,
            results_per_page=20
        )
        
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "keywords": keyword_list,
                "results": results
            }
        )
    
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Error: {str(e)}"
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "naukri-job-scraper"}


# Run server
if __name__ == "__main__":
    print("🚀 Starting Naukri Job Scraper Server...")
    print("📍 Access the web interface at: http://localhost:8007")
    print("📖 API documentation at: http://localhost:8007/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8007,
        reload=False  # Disabled to avoid issues with Playwright on Python 3.13
    )
