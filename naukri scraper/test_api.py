"""
Test script to verify if Naukri API works with direct requests
"""
import httpx
import asyncio
import json

async def test_naukri_api():
    """Test the exact API call that worked in the probe"""
    
    # The exact URL that worked in our probe
    test_url = "https://www.naukri.com/jobapi/v3/search"
    
    # Try with the exact parameters from the working probe
    params_working = {
        'noOfResults': 20,
        'urlType': 'search_by_keyword',
        'searchType': 'adv',
        'keyword': 'gen ai',
        'pageNo': 1,
        'k': 'gen ai',
        'seoKey': 'gen-ai-jobs',
        'src': 'directSearch',
        'latLong': ''
    }
    
        # Different header combinations to test
    header_tests = [
        {
            "name": "With appid and systemid (Naukri)",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'appid': '109',
                'systemid': 'Naukri'
            }
        },
        {
            "name": "With appid and systemid (jobseeker)",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'appid': '109',
                'systemid': 'jobseeker'
            }
        },
        {
            "name": "With appid and systemid (SRP)",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'appid': '109',
                'systemid': 'SRP'
            }
        },
        {
            "name": "Full headers with appid and systemid",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.naukri.com/',
                'appid': '109',
                'systemid': 'Naukri'
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        print("="*70)
        print("TESTING NAUKRI API WITH DIFFERENT HEADER CONFIGURATIONS")
        print("="*70)
        
        for test in header_tests:
            print(f"\n{'='*70}")
            print(f"TEST: {test['name']}")
            print(f"{'='*70}")
            
            try:
                response = await client.get(
                    test_url,
                    params=params_working,
                    headers=test['headers']
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        job_count = len(data.get('jobDetails', []))
                        total_jobs = data.get('noOfJobs', 0)
                        print(f"✅ SUCCESS!")
                        print(f"   - Jobs in response: {job_count}")
                        print(f"   - Total jobs available: {total_jobs}")
                        
                        if job_count > 0:
                            print(f"   - Sample job title: {data['jobDetails'][0].get('title')}")
                            print(f"   - Sample company: {data['jobDetails'][0].get('companyName')}")
                    except Exception as e:
                        print(f"❌ Could not parse JSON: {e}")
                        print(f"Response text (first 500 chars): {response.text[:500]}")
                else:
                    print(f"❌ FAILED with status {response.status_code}")
                    print(f"Response text (first 500 chars): {response.text[:500]}")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
        
        # Now test with Python Developer keyword
        print(f"\n{'='*70}")
        print("TESTING WITH 'Python Developer' KEYWORD")
        print(f"{'='*70}")
        
        params_python = {
            'noOfResults': 20,
            'urlType': 'search_by_keyword',
            'searchType': 'adv',
            'keyword': 'Python Developer',
            'pageNo': 1,
            'k': 'Python Developer',
            'seoKey': 'python-developer-jobs',
            'src': 'directSearch',
            'latLong': ''
        }
        
        # Use the best headers from above tests
        best_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.naukri.com/',
            'appid': '109'
        }
        
        try:
            response = await client.get(
                test_url,
                params=params_python,
                headers=best_headers
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                job_count = len(data.get('jobDetails', []))
                print(f"✅ SUCCESS! Found {job_count} jobs")
                if job_count > 0:
                    print(f"   Sample: {data['jobDetails'][0].get('title')} at {data['jobDetails'][0].get('companyName')}")
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("Starting API tests...\n")
    asyncio.run(test_naukri_api())
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
