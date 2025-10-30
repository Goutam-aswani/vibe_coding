"""
Naukri.com Job Scraper Module
Uses Playwr            # Add JavaScript to mask automation and look more like a real browser
            await self.context.add_init_script("""
                // Override webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override plugins length
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Add chrome property
                window.chrome = {
                    runtime: {}
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)rowser automation to scrape job listings reliably
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page
import re


class NaukriScraper:
    """Scraper for Naukri.com job listings using Playwright browser automation"""
    
    BASE_URL = "https://www.naukri.com"
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def _init_browser(self):
        """Initialize browser if not already initialized"""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security'
                ]
            )
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
                }
            )
            
            # Add JavaScript to mask automation and look like real browser
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                window.chrome = { runtime: {} };
            """)
    
    async def _close_browser(self):
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        self.context = None
        self.browser = None
        self.playwright = None
    
    async def search_jobs(
        self,
        keyword: str,
        max_pages: int = 5,
        results_per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search for jobs by keyword using browser automation
        
        Args:
            keyword: Job role/keyword to search for
            max_pages: Maximum number of pages to scrape (default: 5)
            results_per_page: Number of results per page (default: 20)
            
        Returns:
            Dictionary containing job listings and metadata
        """
        all_jobs = []
        total_jobs = 0
        pages_scraped = 0
        
        try:
            await self._init_browser()
            page = await self.context.new_page()
            
            # Build search URL
            search_url = f"{self.BASE_URL}/{keyword.lower().replace(' ', '-')}-jobs"
            
            for page_num in range(1, max_pages + 1):
                try:
                    print(f"📄 Scraping page {page_num} for keyword: {keyword}")
                    
                    # Add page number to URL if not first page
                    page_url = search_url if page_num == 1 else f"{search_url}-{page_num}"
                    
                    # Navigate to page
                    print(f"🌐 Loading: {page_url}")
                    await page.goto(page_url, wait_until="networkidle", timeout=60000)
                    
                    # Wait for job listings to load
                    try:
                        print(f"⏳ Waiting for job cards to appear...")
                        await page.wait_for_selector('.cust-job-tuple', timeout=30000)
                        print(f"✓ Job cards loaded")
                    except Exception as e:
                        print(f"⚠️  Timeout waiting for job cards: {e}")
                        print(f"⚠️  No job listings found on page {page_num}")
                        break
                    
                    # Extract total jobs count (only on first page)
                    if page_num == 1:
                        try:
                            count_text = await page.locator('.styles_jhc__badge__KKQZu, .nI-gNb-count, span[class*="count"]').first.text_content()
                            if count_text:
                                total_jobs = int(re.sub(r'[^0-9]', '', count_text))
                                print(f"✓ Total jobs available: {total_jobs}")
                        except Exception:
                            print("ℹ️  Could not extract total job count")
                    
                    # Extract job listings
                    job_cards = await page.locator('.cust-job-tuple').all()
                    
                    print(f"🔍 DEBUG: Found {len(job_cards)} .cust-job-tuple elements on page {page_num}")
                    
                    if not job_cards:
                        print(f"⚠️  No job listings found on page {page_num}")
                        break
                    
                    print(f"✓ Found {len(job_cards)} job cards on page {page_num}")
                    
                    for card in job_cards:
                        try:
                            job_data = await self._extract_job_from_card(card)
                            if job_data:
                                all_jobs.append(job_data)
                        except Exception as e:
                            print(f"⚠️  Error extracting job: {e}")
                            continue
                    
                    pages_scraped = page_num
                    print(f"✓ Scraped {len(job_cards)} jobs from page {page_num}")
                    
                    # Rate limiting between pages
                    if page_num < max_pages:
                        await asyncio.sleep(2)
                
                except Exception as e:
                    print(f"❌ Error scraping page {page_num}: {str(e)}")
                    break
            
            await page.close()
        
        finally:
            await self._close_browser()
        
        return {
            'keyword': keyword,
            'total_jobs_found': total_jobs,
            'jobs_scraped': len(all_jobs),
            'pages_scraped': pages_scraped,
            'timestamp': datetime.now().isoformat(),
            'jobs': all_jobs
        }
    
    async def _extract_job_from_card(self, card) -> Optional[Dict[str, Any]]:
        """Extract job data from a job card element"""
        try:
            # Job title (in row1 > h2 > a.title)
            title = await card.locator('h2 a.title').first.text_content()
            title = title.strip() if title else None
            
            # Company name (in row2 > a.comp-name)
            company = await card.locator('a.comp-name').first.text_content()
            company = company.strip() if company else None
            
            # Job URL
            job_url = None
            try:
                link = await card.locator('h2 a.title').first.get_attribute('href')
                if link:
                    job_url = link if link.startswith('http') else f"{self.BASE_URL}{link}"
            except Exception:
                pass
            
            # Experience (in row3 > .exp-wrap > .expwdth)
            experience = None
            try:
                exp_text = await card.locator('.exp-wrap .expwdth').first.text_content()
                if exp_text:
                    experience = exp_text.strip()
            except Exception:
                pass
            
            # Salary (in row3 > .sal-wrap)
            salary = None
            try:
                salary_text = await card.locator('.sal-wrap').first.text_content()
                if salary_text and 'Not disclosed' not in salary_text:
                    salary = salary_text.strip()
            except Exception:
                pass
            
            # Location (in row3 > .loc-wrap > .locWdth)
            locations = []
            try:
                loc_text = await card.locator('.loc-wrap .locWdth').first.text_content()
                if loc_text:
                    locations = [loc.strip() for loc in loc_text.split(',')]
            except Exception:
                pass
            
            # Job description snippet (in row4 > .job-desc)
            description = None
            try:
                desc_text = await card.locator('.job-desc').first.text_content()
                if desc_text:
                    description = desc_text.strip()
            except Exception:
                pass
            
            # Skills/tags (in row5 > .tags-gt > li)
            skills = []
            try:
                tags = await card.locator('.tags-gt li').all()
                for tag in tags:
                    skill_text = await tag.text_content()
                    if skill_text:
                        skills.append(skill_text.strip())
            except Exception:
                pass
            
            # Posted date (in row6 > .job-post-day)
            posted_date = None
            try:
                date_text = await card.locator('.job-post-day').first.text_content()
                if date_text:
                    posted_date = date_text.strip()
            except Exception:
                pass
            
            # Company logo (img.logoImage)
            logo_url = None
            try:
                logo_elem = await card.locator('img.logoImage').first.get_attribute('src')
                if logo_elem:
                    logo_url = logo_elem
            except Exception:
                pass
            
            # Only return if we have at least title and company
            if title and company:
                return {
                    'title': title,
                    'company_name': company,
                    'job_url': job_url,
                    'experience': experience,
                    'salary': salary,
                    'locations': locations,
                    'job_description': description,
                    'skills': skills,
                    'posted_date': posted_date,
                    'company_logo': logo_url
                }
            
            return None
        
        except Exception as e:
            print(f"Error extracting job card: {e}")
            return None
    
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
                print("⏳ Waiting 3 seconds before next search...")
                await asyncio.sleep(3)
        
        return results


# For testing standalone
if __name__ == "__main__":
    async def test():
        scraper = NaukriScraper()
        results = await scraper.search_jobs("python developer", max_pages=2)
        print(f"\n✓ Total jobs scraped: {results['jobs_scraped']}")
        if results['jobs']:
            print(f"✓ Sample job: {results['jobs'][0]['title']} at {results['jobs'][0]['company_name']}")
    
    asyncio.run(test())
