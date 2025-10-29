"""Simple synchronous test"""
import httpx
import json

def test():
    print("Testing API at http://localhost:8005...")
    
    try:
        # Test root
        response = httpx.get("http://localhost:8005/", timeout=10)
        print(f"\n✓ Root endpoint: {response.status_code}")
        print(response.json())
        
        # Test scrape
        print("\nTesting /scrape-jobs?category=machine_learning...")
        print("(This will take ~30 seconds...)")
        response = httpx.get(
            "http://localhost:8005/scrape-jobs",
            params={"category": "machine_learning"},
            timeout=60
        )
        print(f"\n✓ Scrape endpoint: {response.status_code}")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Jobs found: {data['jobs_count']}")
        
        if data['jobs_count'] > 0:
            print(f"\nFirst 3 jobs:")
            for i, job in enumerate(data['jobs'][:3], 1):
                print(f"\n{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   URL: {job['job_url']}")
        
        # Save results
        with open('results.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Full results saved to results.json")
        
    except httpx.ConnectError:
        print("✗ Cannot connect. Is the server running?")
        print("  Start it with: .\\venv\\Scripts\\python.exe -m uvicorn main:app --port 8005")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test()
