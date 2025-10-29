"""
FastAPI application for scraping Hirist.tech job postings
"""
import logging
import re
from typing import Optional
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import ScrapeResponse, ErrorResponse, JobPosting
from scraper_selenium import HiristSeleniumScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hirist.tech Job Scraper API",
    description="A FastAPI application to scrape and retrieve job postings from Hirist.tech",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static working URLs for scraping (verified to work)
WORKING_URLS = {
    "artificial_intelligence": "https://www.hirist.tech/k/artificial-intelligence-jobs?ref=homepagetag&minexp=0&maxexp=1",
    "generative_ai": "https://www.hirist.tech/k/generative-ai-jobs?ref=homepagetag&minexp=0&maxexp=1",
    "machine_learning": "https://www.hirist.tech/k/machine-learning-jobs?ref=homepagetag&minexp=0&maxexp=1"
}

# Default URL for scraping (using machine learning as default)
DEFAULT_URL = WORKING_URLS["machine_learning"]


@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to Hirist.tech Job Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "scrape_jobs": "/scrape-jobs",
            "scrape_all": "/scrape-all",
            "health": "/health",
            "docs": "/docs"
        },
        "working_urls": WORKING_URLS,
        "default_category": "machine_learning",
        "usage": "Visit /docs for interactive API documentation"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Hirist.tech Job Scraper API"
    }


@app.get(
    "/scrape-jobs",
    response_model=ScrapeResponse,
    responses={
        200: {
            "description": "Successfully scraped job postings",
            "model": ScrapeResponse
        },
        400: {
            "description": "Invalid request parameters",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    },
    tags=["Job Scraping"]
)
async def scrape_jobs(
    category: Optional[str] = Query(
        None,
        description="Job category to scrape: 'artificial_intelligence', 'generative_ai', or 'machine_learning'. If not provided, uses machine_learning",
        example="machine_learning"
    ),
    url: Optional[str] = Query(
        None,
        description="Custom URL to scrape (overrides category if provided)",
        example="https://www.hirist.tech/k/machine-learning-jobs?ref=homepagetag&minexp=0&maxexp=1"
    )
):
    """
    Scrape job postings from Hirist.tech
    
    This endpoint fetches and parses job postings from Hirist.tech. 
    You can either provide a custom URL or use the default AI/ML jobs URL.
    
    **Parameters:**
    - **url**: (Optional) Custom URL to scrape from Hirist.tech
    - **min_exp**: Minimum years of experience (0-20)
    - **max_exp**: Maximum years of experience (0-20)
    
    **Returns:**
    - List of job postings with details including:
        - Job ID
        - Title
        - Company
        - Location
        - Experience required
        - Skills
        - Posted date
        - Job URL
        - Company rating and reviews (if available)
    
    **Example:**
    ```
    GET /scrape-jobs?category=machine_learning
    GET /scrape-jobs?category=artificial_intelligence
    GET /scrape-jobs?url=https://www.hirist.tech/k/python-jobs
    ```
    
    **Available Categories:**
    - artificial_intelligence
    - generative_ai
    - machine_learning
    """
    try:
        # Determine target URL
        if url and url.strip():
            # Custom URL provided - decode if it's URL-encoded and strip whitespace
            decoded_url = unquote(url.strip())
            target_url = decoded_url
            logger.info(f"Using custom URL: {target_url}")
            if decoded_url != url:
                logger.info(f"URL was decoded from: {url}")
            
            # Validate URL starts with http
            if not target_url.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid URL format. URL must start with http:// or https://. Got: {target_url}"
                )
        elif category and category.strip() and category in WORKING_URLS:
            # Valid category provided
            target_url = WORKING_URLS[category]
            logger.info(f"Using category '{category}': {target_url}")
        elif category and category.strip():
            # Invalid category
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category '{category}'. Valid categories are: {', '.join(WORKING_URLS.keys())}"
            )
        else:
            # Use default
            target_url = DEFAULT_URL
            logger.info(f"Using default URL (machine_learning): {target_url}")
        
        logger.info(f"Starting scrape for URL: {target_url}")
        
        # Perform scraping with Selenium
        with HiristSeleniumScraper(headless=True, timeout=30) as scraper:
            jobs = scraper.scrape_jobs(target_url)
        
        if not jobs:
            return ScrapeResponse(
                success=True,
                jobs_count=0,
                jobs=[],
                message="No job postings found. The page structure might have changed or no jobs match the criteria."
            )
        
        logger.info(f"Successfully scraped {len(jobs)} job postings")
        
        return ScrapeResponse(
            success=True,
            jobs_count=len(jobs),
            jobs=jobs,
            message=f"Successfully scraped {len(jobs)} job postings"
        )
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape jobs: {str(e)}"
        )


@app.get(
    "/scrape-all",
    response_model=ScrapeResponse,
    responses={
        200: {
            "description": "Successfully scraped all job categories",
            "model": ScrapeResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    },
    tags=["Job Scraping"]
)
async def scrape_all_categories():
    """
    Scrape job postings from all available categories
    
    This endpoint scrapes all three working URLs:
    - Artificial Intelligence jobs
    - Generative AI jobs  
    - Machine Learning jobs
    
    Returns combined results from all categories with duplicates removed.
    
    **Example:**
    ```
    GET /scrape-all
    ```
    """
    try:
        all_jobs = []
        seen_job_ids = set()
        total_scraped = 0
        
        logger.info("Starting to scrape all categories...")
        
        for category, url in WORKING_URLS.items():
            try:
                logger.info(f"Scraping category: {category}")
                with HiristSeleniumScraper(headless=True, timeout=30) as scraper:
                    jobs = scraper.scrape_jobs(url)
                
                # Remove duplicates based on job_id
                unique_jobs = []
                for job in jobs:
                    if job.job_id not in seen_job_ids:
                        seen_job_ids.add(job.job_id)
                        unique_jobs.append(job)
                
                all_jobs.extend(unique_jobs)
                total_scraped += len(jobs)
                logger.info(f"Category '{category}': Found {len(jobs)} jobs ({len(unique_jobs)} unique)")
                
            except Exception as e:
                logger.error(f"Error scraping category '{category}': {str(e)}")
                continue
        
        if not all_jobs:
            return ScrapeResponse(
                success=True,
                jobs_count=0,
                jobs=[],
                message="No job postings found across all categories."
            )
        
        logger.info(f"Successfully scraped {len(all_jobs)} unique jobs from {total_scraped} total")
        
        return ScrapeResponse(
            success=True,
            jobs_count=len(all_jobs),
            jobs=all_jobs,
            message=f"Successfully scraped {len(all_jobs)} unique job postings from all categories (total: {total_scraped})"
        )
        
    except Exception as e:
        logger.error(f"Error during scraping all categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape all categories: {str(e)}"
        )


@app.get(
    "/debug-html",
    tags=["Debug"]
)
async def debug_fetch_html(
    category: Optional[str] = Query(
        "machine_learning",
        description="Category to test"
    )
):
    """
    DEBUG: Fetch raw HTML from a URL to see what's being received
    
    This helps debug if the scraper is getting the right content.
    """
    try:
        if category in WORKING_URLS:
            url = WORKING_URLS[category]
        else:
            url = DEFAULT_URL
        
        logger.info(f"DEBUG: Fetching {url}")
        with HiristSeleniumScraper(headless=True, timeout=30) as scraper:
            html = scraper.fetch_page(url)
        
        if html:
            # Count job links
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            job_links = soup.find_all('a', href=re.compile(r'/j/'))
            
            return {
                "url": url,
                "html_length": len(html),
                "html_preview": html[:1000],  # First 1000 chars
                "total_links": len(soup.find_all('a')),
                "job_links_found": len(job_links),
                "sample_job_links": [link.get('href') for link in job_links[:5]]
            }
        else:
            return {"error": "Failed to fetch HTML"}
    except Exception as e:
        return {"error": str(e)}


@app.get(
    "/jobs/{job_id}",
    response_model=JobPosting,
    responses={
        404: {
            "description": "Job not found",
            "model": ErrorResponse
        }
    },
    tags=["Job Scraping"]
)
async def get_job_by_id(job_id: str):
    """
    Get a specific job by its ID
    
    **Note:** This endpoint requires scraping the jobs first. 
    In a production environment, you would store scraped jobs in a database.
    
    Currently, this is a placeholder endpoint demonstrating the API structure.
    """
    # This would query a database in a production environment
    raise HTTPException(
        status_code=501,
        detail="This endpoint requires database integration. Please use /scrape-jobs to fetch jobs."
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom HTTP exception handler
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "details": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    General exception handler
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "details": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )
