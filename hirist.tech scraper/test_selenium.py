"""
Test the new Selenium-based scraper
"""
from scraper_selenium import HiristSeleniumScraper

print("="*70)
print("TESTING SELENIUM SCRAPER")
print("="*70)
print()

url = "https://www.hirist.tech/k/machine-learning-jobs?ref=homepagetag&minexp=0&maxexp=1"

print(f"Testing URL: {url}")
print()

try:
    with HiristSeleniumScraper(headless=True, timeout=30) as scraper:
        print("Scraping jobs...")
        jobs = scraper.scrape_jobs(url)
        
        print(f"\n{'='*70}")
        print(f"✅ SUCCESS: Found {len(jobs)} jobs!")
        print(f"{'='*70}\n")
        
        if jobs:
            print("Sample jobs:")
            for i, job in enumerate(jobs[:5], 1):
                print(f"\n{i}. {job.title}")
                print(f"   Company: {job.company or 'N/A'}")
                print(f"   Location: {job.location or 'N/A'}")
                print(f"   Experience: {job.experience or 'N/A'}")
                print(f"   Skills: {', '.join(job.skills[:5]) if job.skills else 'N/A'}")
                print(f"   URL: {job.job_url}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
