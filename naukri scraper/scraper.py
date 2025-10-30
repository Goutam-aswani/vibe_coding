"""
Naukri.com Job Scraper Module
Uses Playwright browser automation to scrape job listings
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright
import re


class NaukriScraper:
    """Scraper for Naukri.com job listings using Playwright browser automation"""
    
    BASE_URL = "https://www.naukri.com"
    
    def __init__(self):
        self.browser = None
        self.context = None
    
    async def search_jobs(
        self,
        keyword: str,
        max_pages: int = 5,
        results_per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search for jobs by keyword
        
        Args:
            keyword: Job role/keyword to search for
            max_pages: Maximum number of pages to scrape (default: 5)
            results_per_page: Number of results per page (default: 20)
            
        Returns:
            Dictionary containing job listings and metadata
        """
        all_jobs = []
        total_jobs = 0
        
        # Generate seoKey from keyword (convert to URL-friendly format)
        seo_key = keyword.lower().replace(' ', '-') + '-jobs'
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for page in range(1, max_pages + 1):
                try:
                    print(f"📄 Scraping page {page} for keyword: {keyword}")
                    
                    params = {
                        'noOfResults': results_per_page,
                        'urlType': 'search_by_keyword',
                        'searchType': 'adv',
                        'keyword': keyword,
                        'pageNo': page,
                        'k': keyword,
                        'seoKey': seo_key,
                        'src': 'directSearch',
                        'latLong': ''
                    }
                    
                    response = await client.get(
                        self.BASE_URL,
                        params=params,
                        headers=self.headers,
                        follow_redirects=True
                    )
                    
                    if response.status_code != 200:
                        print(f"⚠️  Page {page} returned status {response.status_code}")
                        break
                    
                    data = response.json()
                    
                    # Extract job details
                    job_details = data.get('jobDetails', [])
                    
                    if not job_details:
                        print(f"ℹ️  No more jobs found on page {page}")
                        break
                    
                    # Get total number of jobs (from first page)
                    if page == 1:
                        total_jobs = data.get('noOfJobs', 0)
                        print(f"✓ Total jobs available: {total_jobs}")
                    
                    # Parse and clean job data
                    for job in job_details:
                        cleaned_job = self._parse_job(job)
                        all_jobs.append(cleaned_job)
                    
                    print(f"✓ Scraped {len(job_details)} jobs from page {page}")
                    
                    # Rate limiting: wait between requests
                    if page < max_pages:
                        await asyncio.sleep(1)
                
                except Exception as e:
                    print(f"❌ Error scraping page {page}: {str(e)}")
                    break
        
        return {
            'keyword': keyword,
            'total_jobs_found': total_jobs,
            'jobs_scraped': len(all_jobs),
            'pages_scraped': min(page, max_pages),
            'timestamp': datetime.now().isoformat(),
            'jobs': all_jobs
        }
    
    def _parse_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and clean job data from API response"""
        
        # Extract placeholders (experience, salary, location)
        placeholders = job.get('placeholders', [])
        experience = None
        salary = None
        locations = []
        
        for placeholder in placeholders:
            p_type = placeholder.get('type', '')
            p_label = placeholder.get('label', '')
            
            if p_type == 'experience':
                experience = p_label
            elif p_type == 'salary':
                salary = p_label
            elif p_type == 'location':
                locations.append(p_label)
        
        # Get salary details
        salary_detail = job.get('salaryDetail', {})
        min_salary = salary_detail.get('minimumSalary')
        max_salary = salary_detail.get('maximumSalary')
        currency = salary_detail.get('currency', 'INR')
        
        # Build job URL
        jd_url = job.get('jdURL', '')
        full_job_url = f"https://www.naukri.com{jd_url}" if jd_url else None
        
        return {
            'job_id': job.get('jobId'),
            'title': job.get('title'),
            'company_name': job.get('companyName'),
            'company_id': job.get('companyId'),
            'job_description': job.get('jobDescription', '').strip(),
            'job_url': full_job_url,
            'experience': experience,
            'experience_min': job.get('minimumExperience'),
            'experience_max': job.get('maximumExperience'),
            'salary': salary,
            'salary_min': min_salary,
            'salary_max': max_salary,
            'currency': currency,
            'locations': locations,
            'skills': job.get('tagsAndSkills', '').split(',') if job.get('tagsAndSkills') else [],
            'posted_date': job.get('footerPlaceholderLabel'),
            'created_timestamp': job.get('createdDate'),
            'company_logo': job.get('logoPath'),
            'is_consultant': job.get('consultant', False),
            'is_saved': job.get('isSaved', False)
        }
    
    async def search_multiple_keywords(
        self,
        keywords: List[str],
        max_pages: int = 5,
        results_per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs using multiple keywords
        
        Args:
            keywords: List of job roles/keywords to search for
            max_pages: Maximum pages per keyword
            results_per_page: Results per page
            
        Returns:
            List of results for each keyword
        """
        results = []
        
        for keyword in keywords:
            print(f"\n{'='*60}")
            print(f"🔍 Searching for: {keyword}")
            print(f"{'='*60}")
            
            result = await self.search_jobs(
                keyword=keyword.strip(),
                max_pages=max_pages,
                results_per_page=results_per_page
            )
            results.append(result)
            
            # Rate limit between different keyword searches
            if keyword != keywords[-1]:
                print("⏳ Waiting 2 seconds before next search...")
                await asyncio.sleep(2)
        
        return results


# For testing standalone
if __name__ == "__main__":
    async def test():
        scraper = NaukriScraper()
        results = await scraper.search_jobs("python developer", max_pages=2)
        print(f"\n✓ Total jobs scraped: {results['jobs_scraped']}")
        print(f"✓ Sample job: {results['jobs'][0]['title']} at {results['jobs'][0]['company_name']}")
    
    asyncio.run(test())
