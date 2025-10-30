"""
FastAPI server for foundit.in job scraper
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time
import logging

from models import (
    ScrapeRequest, 
    ScrapeResponse, 
    ScrapeStats, 
    HealthResponse
)
from scraper import FounditScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Foundit Job Scraper API",
    description="API to scrape job listings from foundit.in for multiple job roles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraper
scraper = FounditScraper()


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Foundit Job Scraper API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "POST /scrape": "Scrape jobs for multiple roles",
            "GET /health": "Health check"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_jobs(request: ScrapeRequest):
    """
    Scrape jobs from foundit.in for multiple job roles
    
    ## Request Body:
    - **job_roles**: List of job role queries (e.g., ["gen ai engineer", "data scientist"])
    - **experience_range**: Experience range in format 'min~max' (default: "0~0")
    - **country**: Country to search in (default: "India")
    - **limit_per_role**: Maximum jobs per role (1-100, default: 100)
    
    ## Example Request:
    ```json
    {
        "job_roles": ["gen ai engineer", "machine learning engineer"],
        "experience_range": "0~2",
        "country": "India",
        "limit_per_role": 50
    }
    ```
    
    ## Returns:
    - Complete list of job listings with all details
    - Statistics about the scraping operation
    """
    try:
        logger.info(f"Starting scrape for roles: {request.job_roles}")
        start_time = time.time()
        
        # Scrape jobs
        jobs, jobs_per_role = scraper.scrape_jobs(
            job_roles=request.job_roles,
            experience_range=request.experience_range,
            country=request.country,
            limit_per_role=request.limit_per_role
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Create statistics
        stats = ScrapeStats(
            total_jobs_found=len(jobs),
            jobs_per_role=jobs_per_role,
            total_roles_searched=len(request.job_roles),
            execution_time_seconds=round(execution_time, 2),
            timestamp=datetime.now()
        )
        
        logger.info(
            f"Scraping completed: {len(jobs)} jobs found in {execution_time:.2f}s"
        )
        
        return ScrapeResponse(
            success=True,
            message=f"Successfully scraped {len(jobs)} jobs for {len(request.job_roles)} role(s)",
            stats=stats,
            jobs=jobs
        )
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping jobs: {str(e)}"
        )


@app.get("/example-request")
async def example_request():
    """Get an example request body for the /scrape endpoint"""
    return {
        "description": "Example request body for POST /scrape",
        "example": {
            "job_roles": [
                "gen ai engineer",
                "machine learning engineer",
                "data scientist"
            ],
            "experience_range": "0~0",
            "country": "India",
            "limit_per_role": 50
        },
        "notes": {
            "job_roles": "You can search for multiple roles at once",
            "experience_range": "Format: 'min~max' (e.g., '0~0' for freshers, '2~5' for 2-5 years)",
            "country": "Currently optimized for 'India'",
            "limit_per_role": "Maximum 100 jobs per role. API will deduplicate across roles."
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*80)
    print("🚀 Starting Foundit Job Scraper API")
    print("="*80)
    print("\n📋 Available endpoints:")
    print("  • http://localhost:8080/docs - Interactive API documentation")
    print("  • http://localhost:8080/health - Health check")
    print("  • http://localhost:8080/scrape - Scrape jobs (POST)")
    print("  • http://localhost:8080/example-request - Example request")
    print("\n" + "="*80 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )
