"""
Selenium-based web scraper for Hirist.tech job postings
This version uses a real browser to handle JavaScript-rendered content
"""
import re
import logging
import time
from typing import List, Optional
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from models import JobPosting

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HiristSeleniumScraper:
    """
    Selenium-based scraper for Hirist.tech job postings
    Uses Chrome browser to render JavaScript and extract job data
    """
    
    BASE_URL = "https://www.hirist.tech"
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize the Selenium scraper
        
        Args:
            headless: Run browser in headless mode (no GUI)
            timeout: Page load timeout in seconds
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None
    
    def _init_driver(self):
        """Initialize Chrome WebDriver"""
        if self.driver:
            return
        
        logger.info("Initializing Chrome WebDriver...")
        
        # Configure Chrome options
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Additional options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable logging
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Initialize driver with webdriver-manager
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(self.timeout)
        
        logger.info("✓ Chrome WebDriver initialized")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            self.driver = None
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL using Selenium
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        try:
            self._init_driver()
            
            logger.info(f"Loading URL: {url}")
            self.driver.get(url)
            
            # Wait for job links to appear (they're loaded by JavaScript)
            logger.info("Waiting for job listings to load...")
            try:
                # Wait up to 15 seconds for job links to appear
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/j/']"))
                )
                logger.info("✓ Job listings loaded")
            except TimeoutException:
                logger.warning("Timeout waiting for job links - may still have some content")
            
            # Scroll to load more jobs (if lazy loading is used)
            logger.info("Scrolling to load all jobs...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for any lazy-loaded content
            
            # Get the page source
            html = self.driver.page_source
            logger.info(f"✓ Fetched {len(html):,} characters of HTML")
            
            return html
            
        except Exception as e:
            logger.error(f"Error fetching page: {str(e)}")
            return None
    
    def extract_job_id(self, job_url: str) -> Optional[str]:
        """
        Extract job ID from URL
        
        Args:
            job_url: Job posting URL
            
        Returns:
            Job ID or None
        """
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
        job_links = soup.find_all('a', href=re.compile(r'/j/[^?]+\d+'))
        
        logger.info(f"Found {len(job_links)} potential job links")
        
        if len(job_links) == 0:
            logger.warning("No job links found! Checking page structure...")
            # Debug: show what we do have
            all_links = soup.find_all('a', href=True)
            logger.info(f"Total links found: {len(all_links)}")
            if all_links:
                logger.info(f"Sample links: {[l.get('href')[:50] for l in all_links[:5]]}")
        
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
                
                # Parse job details
                title = ""
                company = None
                experience = None
                location = None
                posted_date = None
                skills = []
                is_premium = 'PREMIUM' in job_text.upper()
                company_rating = None
                reviews_count = None
                
                # Extract experience pattern: "X - Y yrs"
                exp_match = re.search(r'(\d+\s*-\s*\d+\s*yrs?)', job_text)
                if exp_match:
                    experience = exp_match.group(1)
                
                # Extract posted date
                posted_match = re.search(r'Posted\s+(\d+\s+(?:day|days|week|weeks|month|months)\s+ago)', job_text, re.IGNORECASE)
                if posted_match:
                    posted_date = posted_match.group(1)
                
                # Extract rating
                rating_match = re.search(r'(\d+\.?\d*)\s+grey-divider\s+(\d+\+)\s+Reviews?', job_text)
                if rating_match:
                    company_rating = rating_match.group(1)
                    reviews_count = rating_match.group(2)
                
                # Extract title from URL
                url_parts = job_url.split('/j/')
                if len(url_parts) > 1:
                    title_from_url = url_parts[1].split('?')[0]
                    title_from_url = re.sub(r'-\d+$', '', title_from_url)
                    title = ' '.join(word.capitalize() for word in title_from_url.split('-'))
                
                # Extract company name
                company_match = re.match(r'^([A-Z][A-Za-z0-9\s&.-]+?)\s*-', job_text)
                if company_match:
                    company = company_match.group(1).strip()
                
                # Extract location
                location_patterns = [
                    'Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Chennai', 'Pune', 
                    'Kolkata', 'Gurgaon', 'Gurugram', 'Noida', 'Greater-Noida',
                    'Multiple Locations', 'Anywhere-in-India'
                ]
                for loc in location_patterns:
                    if loc in job_text:
                        location = loc
                        break
                
                # Extract skills
                skill_keywords = [
                    'Python', 'Java', 'JavaScript', 'Machine Learning', 'Deep Learning',
                    'Artificial Intelligence', 'AI', 'ML', 'NLP', 'Data Science',
                    'Data Scientist', 'LLM', 'Generative AI', 'Prompt Engineering',
                    'TensorFlow', 'PyTorch', 'Computer Vision', 'Chatbot', 'Rasa',
                    'RAG', 'Agentic AI', 'Data Modeling', 'SQL', 'NoSQL', 'AWS',
                    'Azure', 'GCP', 'Docker', 'Kubernetes', 'React', 'Node.js'
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
    
    def scrape_jobs(self, url: str) -> List[JobPosting]:
        """
        Scrape job postings from a URL
        
        Args:
            url: The URL to scrape
            
        Returns:
            List of JobPosting objects
        """
        try:
            html = self.fetch_page(url)
            if not html:
                return []
            
            jobs = self.parse_job_postings(html)
            return jobs
            
        finally:
            # Always close the browser when done
            self.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
