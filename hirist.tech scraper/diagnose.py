"""
Quick diagnostic script to test the scraper directly
"""
import asyncio
import sys
from scraper import HiristScraper

# The working URLs
URLS_TO_TEST = [
    ("Machine Learning", "https://www.hirist.tech/k/machine-learning-jobs?ref=homepagetag&minexp=0&maxexp=1"),
    ("Artificial Intelligence", "https://www.hirist.tech/k/artificial-intelligence-jobs?ref=homepagetag&minexp=0&maxexp=1"),
    ("Generative AI", "https://www.hirist.tech/k/generative-ai-jobs?ref=homepagetag&minexp=0&maxexp=1"),
]


async def test_scraper():
    print("=" * 70)
    print("HIRIST.TECH SCRAPER DIAGNOSTIC TEST")
    print("=" * 70)
    print()
    
    scraper = HiristScraper(timeout=30)
    
    for name, url in URLS_TO_TEST:
        print(f"\n{'='*70}")
        print(f"Testing: {name}")
        print(f"URL: {url}")
        print(f"{'='*70}")
        
        try:
            # Step 1: Fetch HTML
            print("\n[1/3] Fetching HTML...")
            html = await scraper.fetch_page(url)
            
            if not html:
                print("❌ FAILED: Could not fetch HTML")
                continue
            
            print(f"✓ Success: Fetched {len(html):,} characters")
            print(f"   Preview: {html[:200]}...")
            
            # Step 2: Parse jobs
            print("\n[2/3] Parsing job postings...")
            jobs = scraper.parse_job_postings(html)
            
            if not jobs:
                print("❌ WARNING: No jobs found in HTML")
                print("\nDebugging info:")
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'lxml')
                
                # Check for job links
                job_links = soup.find_all('a', href=True)
                print(f"   Total <a> tags found: {len(job_links)}")
                
                # Check for our pattern
                import re
                pattern_links = soup.find_all('a', href=re.compile(r'/j/'))
                print(f"   Links with '/j/' pattern: {len(pattern_links)}")
                
                if pattern_links:
                    print("\n   Sample links found:")
                    for link in pattern_links[:5]:
                        print(f"      - {link.get('href')}")
                else:
                    print("\n   ⚠ No job links found with pattern '/j/'")
                    print("   The website structure might have changed!")
                
                continue
            
            print(f"✓ Success: Found {len(jobs)} job postings")
            
            # Step 3: Show sample jobs
            print("\n[3/3] Sample job data:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"\n   Job {i}:")
                print(f"      ID: {job.job_id}")
                print(f"      Title: {job.title}")
                print(f"      Company: {job.company or 'N/A'}")
                print(f"      Location: {job.location or 'N/A'}")
                print(f"      Experience: {job.experience or 'N/A'}")
                print(f"      Skills: {', '.join(job.skills[:3]) if job.skills else 'None'}")
                print(f"      URL: {job.job_url}")
            
            print(f"\n✅ {name}: SUCCESS - {len(jobs)} jobs scraped")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    print("\nStarting diagnostic test...")
    print("This will test all three working URLs\n")
    
    try:
        asyncio.run(test_scraper())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
