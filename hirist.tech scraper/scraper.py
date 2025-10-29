"""
Web scraper for Hirist.tech job postings
"""
import re
import logging
from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from models import JobPosting

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HiristScraper:
    """
    Scraper for Hirist.tech job postings
    """
    
    BASE_URL = "https://www.hirist.tech"
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the scraper
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                logger.info(f"Fetching URL: {url}")
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def extract_job_id(self, job_url: str) -> Optional[str]:
        """
        Extract job ID from URL
        
        Args:
            job_url: Job posting URL
            
        Returns:
            Job ID or None
        """
        # Extract numeric ID from URL like: /j/machine-learning-engineer-1566140
        match = re.search(r'-(\d+)(?:\?|$)', job_url)
        return match.group(1) if match else None
    
    def parse_job_postings(self, html: str) -> List[JobPosting]:
        """
        Parse job postings from HTML content
        
        Args:
            html: HTML content to parse
            
        Returns:
            List of JobPosting objects
        """
        soup = BeautifulSoup(html, 'lxml')
        jobs = []
        
        # Find all job posting links
        # Based on the webpage structure, job links follow pattern: /j/{job-title}-{id}
        job_links = soup.find_all('a', href=re.compile(r'/j/[^?]+\d+'))
        
        logger.info(f"Found {len(job_links)} potential job links")
        
        # Process unique job links (avoid duplicates)
        seen_urls = set()
        
        for link in job_links:
            try:
                job_url = link.get('href', '')
                
                # Skip if we've already seen this URL
                if job_url in seen_urls:
                    continue
                    
                seen_urls.add(job_url)
                
                # Make URL absolute
                if job_url and not job_url.startswith('http'):
                    job_url = urljoin(self.BASE_URL, job_url)
                
                # Extract job ID
                job_id = self.extract_job_id(job_url)
                if not job_id:
                    continue
                
                # Get job text content
                job_text = link.get_text(strip=True)
                
                # Parse job details from the link text
                # Structure appears to be: [logo] Company - Title Experience Location Posted Skills PREMIUM INFO
                parts = job_text.split()
                
                # Extract company and title (usually at the beginning)
                # Look for company name (often has special chars or capital letters)
                title = ""
                company = None
                experience = None
                location = None
                posted_date = None
                skills = []
                is_premium = 'PREMIUM' in job_text.upper()
                company_rating = None
                reviews_count = None
                
                # Try to extract from structured content
                # Look for experience pattern: "X - Y yrs"
                exp_match = re.search(r'(\d+\s*-\s*\d+\s*yrs?)', job_text)
                if exp_match:
                    experience = exp_match.group(1)
                
                # Look for posted date: "Posted X days/weeks ago" or "Posted X day/week ago"
                posted_match = re.search(r'Posted\s+(\d+\s+(?:day|days|week|weeks)\s+ago)', job_text, re.IGNORECASE)
                if posted_match:
                    posted_date = posted_match.group(1)
                
                # Look for rating: "star-icon 4.7 grey-divider 5+ Reviews"
                rating_match = re.search(r'(\d+\.?\d*)\s+grey-divider\s+(\d+\+)\s+Reviews?', job_text)
                if rating_match:
                    company_rating = rating_match.group(1)
                    reviews_count = rating_match.group(2)
                
                # Extract title - usually the main text before experience
                # Try to find the job title by looking at the URL
                url_parts = job_url.split('/j/')
                if len(url_parts) > 1:
                    title_from_url = url_parts[1].split('?')[0]
                    # Remove job ID from end
                    title_from_url = re.sub(r'-\d+$', '', title_from_url)
                    # Replace hyphens with spaces and capitalize
                    title = ' '.join(word.capitalize() for word in title_from_url.split('-'))
                
                # Extract company name - look for patterns before the title
                # Company names often appear with special formatting
                company_match = re.match(r'^([A-Z][A-Za-z0-9\s&.-]+?)\s*-', job_text)
                if company_match:
                    company = company_match.group(1).strip()
                
                # Extract location - common locations
                location_patterns = [
                    'Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Chennai', 'Pune', 
                    'Kolkata', 'Gurgaon', 'Gurugram', 'Noida', 'Greater-Noida',
                    'Multiple Locations', 'Anywhere-in-India'
                ]
                for loc in location_patterns:
                    if loc in job_text:
                        location = loc
                        break
                
                # Extract skills - common tech skills
                skill_keywords = [
                    'Python', 'Java', 'JavaScript', 'Machine Learning', 'Deep Learning',
                    'Artificial Intelligence', 'AI', 'ML', 'NLP', 'Data Science',
                    'Data Scientist', 'LLM', 'Generative AI', 'Prompt Engineering',
                    'TensorFlow', 'PyTorch', 'Computer Vision', 'Chatbot', 'Rasa',
                    'RAG', 'Agentic AI', 'Data Modeling'
                ]
                
                for skill in skill_keywords:
                    if skill in job_text:
                        skills.append(skill)
                
                # Remove duplicates from skills
                skills = list(dict.fromkeys(skills))
                
                # Create JobPosting object
                job = JobPosting(
                    job_id=job_id,
                    title=title or "Job Title Not Parsed",
                    company=company,
                    location=location,
                    experience=experience,
                    posted_date=posted_date,
                    skills=skills,
                    job_url=job_url,
                    company_rating=company_rating,
                    reviews_count=reviews_count,
                    is_premium=is_premium
                )
                
                jobs.append(job)
                logger.debug(f"Parsed job: {job.title} ({job.job_id})")
                
            except Exception as e:
                logger.warning(f"Error parsing job link: {str(e)}")
                continue
        
        logger.info(f"Successfully parsed {len(jobs)} unique job postings")
        return jobs
    
    async def scrape_jobs(self, url: str) -> List[JobPosting]:
        """
        Scrape job postings from a URL
        
        Args:
            url: The URL to scrape
            
        Returns:
            List of JobPosting objects
        """
        html = await self.fetch_page(url)
        if not html:
            return []
        
        return self.parse_job_postings(html)
