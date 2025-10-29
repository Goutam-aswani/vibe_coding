"""
Example script to test the Hirist.tech Job Scraper API
"""
import asyncio
import json
from typing import Optional

import httpx


async def test_api(base_url: str = "http://localhost:8005"):
    """
    Test the scraper API endpoints
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 60)
        print("Testing Hirist.tech Job Scraper API")
        print("=" * 60)
        print()
        
        # Test 1: Root endpoint
        print("1. Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
        
        # Test 2: Health check
        print("2. Testing health check...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
        
        # Test 3: Scrape jobs (default)
        print("3. Testing job scraping (default URL)...")
        print("   This may take 10-30 seconds...")
        try:
            response = await client.get(f"{base_url}/scrape-jobs")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Success: Found {data['jobs_count']} jobs")
                
                # Display first few jobs
                if data['jobs']:
                    print()
                    print("   Sample jobs:")
                    for i, job in enumerate(data['jobs'][:3], 1):
                        print(f"\n   Job {i}:")
                        print(f"      Title: {job['title']}")
                        print(f"      Company: {job.get('company', 'N/A')}")
                        print(f"      Location: {job.get('location', 'N/A')}")
                        print(f"      Experience: {job.get('experience', 'N/A')}")
                        print(f"      Skills: {', '.join(job['skills'][:5])}")
                        print(f"      URL: {job.get('job_url', 'N/A')}")
                        print(f"      Premium: {job['is_premium']}")
                
                # Save full response to file
                with open('scraped_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print()
                print(f"   ✓ Full results saved to: scraped_jobs.json")
            else:
                print(f"   ❌ Error: {response.text}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
        
        print("=" * 60)
        print("Test completed!")
        print("=" * 60)


async def scrape_custom_url(url: str, base_url: str = "http://localhost:8005"):
    """
    Scrape a custom URL
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"Scraping custom URL: {url}")
        print("This may take 10-30 seconds...")
        print()
        
        try:
            response = await client.get(
                f"{base_url}/scrape-jobs",
                params={"url": url}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Success: Found {data['jobs_count']} jobs")
                
                # Display summary
                if data['jobs']:
                    print("\nJob Summary:")
                    for i, job in enumerate(data['jobs'][:5], 1):
                        print(f"{i}. {job['title']} at {job.get('company', 'N/A')} - {job.get('location', 'N/A')}")
                
                return data
            else:
                print(f"❌ Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


if __name__ == "__main__":
    # Run the basic test
    asyncio.run(test_api())
    
    # Uncomment to test with custom URL:
    # asyncio.run(scrape_custom_url("https://www.hirist.tech/c/python-jobs"))
