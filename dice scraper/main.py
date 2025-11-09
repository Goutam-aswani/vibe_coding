from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode

app = FastAPI(
    title="Dice.com Job Scraper API",
    description="API to scrape job postings from Dice.com",
    version="1.0.0"
)


class JobPosting(BaseModel):
    """Model for a single job posting"""
    title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    posted_date: Optional[str] = Field(None, description="When the job was posted")
    salary: Optional[str] = Field(None, description="Salary information")
    job_type: Optional[str] = Field(None, description="Employment type (Full-time, Contract, etc.)")
    description: Optional[str] = Field(None, description="Job description snippet")
    job_url: Optional[str] = Field(None, description="Link to the full job posting")
    company_url: Optional[str] = Field(None, description="Link to company profile")


class JobListResponse(BaseModel):
    """Response model for job listings"""
    total_jobs: int = Field(..., description="Total number of jobs found")
    jobs: List[JobPosting] = Field(..., description="List of job postings")
    search_query: str = Field(..., description="Search query used")
    filters: dict = Field(..., description="Filters applied")


def scrape_dice_jobs(
    search_query: str = "AI engineer",
    workplace_type: str = "Remote",
    page: int = 1
) -> JobListResponse:
    """
    Scrape job postings from Dice.com
    
    Args:
        search_query: Job title or keywords to search for
        workplace_type: Workplace type filter (Remote, Hybrid, On-Site)
        page: Page number to fetch
        
    Returns:
        JobListResponse with scraped job data
    """
    
    # Build the URL
    params = {
        'q': search_query,
        'filters.workplaceTypes': workplace_type,
        'page': page
    }
    
    base_url = "https://www.dice.com/jobs"
    url = f"{base_url}?{urlencode(params)}"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        jobs_list = []
        
        # Find all job cards - these are typically in article or div tags with specific classes
        # Based on the structure, jobs seem to be in a card-like format
        job_cards = soup.find_all('div', class_=re.compile('card|job'))
        
        # If the above doesn't work, try finding by links to job details
        if not job_cards:
            # Look for job detail links as an alternative
            job_links = soup.find_all('a', href=re.compile(r'/job-detail/'))
            
            # Process each unique job
            processed_urls = set()
            
            for link in job_links:
                job_url = link.get('href', '')
                if not job_url or job_url in processed_urls:
                    continue
                
                processed_urls.add(job_url)
                
                if not job_url.startswith('http'):
                    job_url = f"https://www.dice.com{job_url}"
                
                # Try to find the parent container for this job
                parent = link.find_parent(['div', 'article'])
                
                if parent:
                    # Extract job title - try multiple methods
                    title = None
                    # Method 1: Try aria-label attribute
                    title = link.get('aria-label', '').strip()
                    # Method 2: Try title attribute
                    if not title:
                        title = link.get('title', '').strip()
                    # Method 3: Try getting text from link
                    if not title:
                        title = link.get_text(strip=True)
                    # Method 4: Look for title in nested spans or divs
                    if not title:
                        title_elem = link.find(['span', 'div', 'h2', 'h3'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                    
                    # Clean up the title - remove "View Details for" prefix and hash suffix
                    if title:
                        # Remove "View Details for" prefix
                        title = re.sub(r'^View Details for\s+', '', title, flags=re.IGNORECASE)
                        # Remove hash pattern at the end (hex string in parentheses)
                        title = re.sub(r'\s*\([a-f0-9]{32}\)\s*$', '', title)
                        title = title.strip()
                    
                    # Extract company name - look for company links
                    company = None
                    company_url = None
                    # Find ALL company links (there might be multiple - logo and text)
                    company_links = parent.find_all('a', href=re.compile(r'/company-profile/'))
                    
                    for company_link in company_links:
                        company_url = company_link.get('href', '')
                        if company_url and not company_url.startswith('http'):
                            company_url = f"https://www.dice.com{company_url}"
                        
                        # Try to get company name from the link text
                        temp_company = company_link.get_text(strip=True)
                        
                        # Skip if it's empty or just "Company Logo" or similar generic text
                        if temp_company:
                            company_lower = temp_company.lower()
                            if 'logo' not in company_lower and company_lower not in ['company', 'company profile']:
                                company = temp_company
                                break  # Found a good company name, stop searching
                    
                    # If still no company name found, try attributes or extract from URL
                    if not company and company_links:
                        company_link = company_links[0]  # Use first link for fallback
                        company = company_link.get('aria-label', '').strip()
                        if not company:
                            company = company_link.get('title', '').strip()
                        
                        # If still no company name, extract from company_url
                        if not company and company_url:
                            # Extract from URL parameter companyname=...
                            company_match = re.search(r'companyname=([^&]+)', company_url)
                            if company_match:
                                from urllib.parse import unquote
                                company = unquote(company_match.group(1))
                    
                    # Extract location and posted date
                    location = None
                    posted_date = None
                    
                    # Look for text patterns in the parent
                    text_content = parent.get_text(separator='|', strip=True)
                    
                    # Try to find location (typically mentions city, state, or Remote)
                    location_patterns = [
                        r'Remote(?:\s+or\s+[^|•]+)?',
                        r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?'
                    ]
                    for pattern in location_patterns:
                        location_match = re.search(pattern, text_content)
                        if location_match:
                            location = location_match.group(0)
                            break
                    
                    # Try to find posted date
                    date_patterns = [
                        r'Today',
                        r'Yesterday',
                        r'\d+d ago',
                        r'\d+w ago',
                        r'\d+m ago'
                    ]
                    for pattern in date_patterns:
                        date_match = re.search(pattern, text_content)
                        if date_match:
                            posted_date = date_match.group(0)
                            break
                    
                    # Extract salary information
                    salary = None
                    salary_patterns = [
                        r'\$[\d,]+(?:\s*-\s*\$?[\d,]+)?(?:\s+(?:per\s+)?(?:year|hour|hr))?',
                        r'USD\s+[\d,]+(?:\.00)?\s*-\s*[\d,]+(?:\.00)?\s+per\s+(?:year|hour)',
                        r'Depends on Experience'
                    ]
                    for pattern in salary_patterns:
                        salary_match = re.search(pattern, text_content)
                        if salary_match:
                            salary = salary_match.group(0)
                            break
                    
                    # Extract job type
                    job_type = None
                    job_type_patterns = [
                        r'Full-time',
                        r'Part-time',
                        r'Contract',
                        r'Third Party',
                        r'Internship'
                    ]
                    for pattern in job_type_patterns:
                        type_match = re.search(pattern, text_content)
                        if type_match:
                            job_type = type_match.group(0)
                            break
                    
                    # Extract job description snippet
                    description = None
                    # Look for paragraphs or divs with description text
                    desc_elem = parent.find(['p', 'div'], class_=re.compile(r'description|summary|snippet'))
                    if desc_elem:
                        description = desc_elem.get_text(strip=True)[:300]  # Limit to 300 chars
                    else:
                        # Get all text elements and find the longest one (likely the description)
                        text_elements = parent.find_all(['p', 'div'])
                        longest_text = ""
                        for elem in text_elements:
                            elem_text = elem.get_text(strip=True)
                            # Skip if it looks like company name, location, or salary
                            if company and company in elem_text and len(elem_text) < 100:
                                continue
                            if location and location in elem_text and len(elem_text) < 100:
                                continue
                            if salary and salary in elem_text and len(elem_text) < 100:
                                continue
                            # Keep the longest text that's substantial
                            if len(elem_text) > len(longest_text) and len(elem_text) > 50:
                                longest_text = elem_text
                        
                        if longest_text:
                            description = longest_text[:300]  # Limit to 300 chars
                    
                    # Create job posting object
                    job = JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        posted_date=posted_date,
                        salary=salary,
                        job_type=job_type,
                        description=description,
                        job_url=job_url,
                        company_url=company_url
                    )
                    
                    jobs_list.append(job)
        
        # Create response
        response_data = JobListResponse(
            total_jobs=len(jobs_list),
            jobs=jobs_list,
            search_query=search_query,
            filters={
                'workplace_type': workplace_type,
                'page': page
            }
        )
        
        return response_data
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from Dice.com: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing job data: {str(e)}")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Dice.com Job Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/jobs": "Search for jobs on Dice.com",
            "/docs": "Interactive API documentation",
            "/health": "Health check endpoint"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/jobs", response_model=JobListResponse, tags=["Jobs"])
async def get_jobs(
    q: str = Query("AI engineer", description="Job title or keywords to search for"),
    workplace_type: str = Query("Remote", description="Workplace type (Remote, Hybrid, On-Site)"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)")
):
    """
    Scrape job postings from Dice.com
    
    Parameters:
    - **q**: Search query for job title or keywords
    - **workplace_type**: Filter by workplace type (Remote, Hybrid, On-Site)
    - **page**: Page number to fetch
    
    Returns:
    - List of job postings with details including:
        - Job title
        - Company name
        - Location
        - Salary information
        - Job type (Full-time, Contract, etc.)
        - Description snippet
        - Links to job and company pages
    """
    
    return scrape_dice_jobs(
        search_query=q,
        workplace_type=workplace_type,
        page=page
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
