"""
API Probe Script - Discover Naukri.com internal JSON endpoints
This script uses Playwright to load the page and capture all XHR/Fetch requests
to identify the API endpoint that returns job listings data.
"""
import asyncio
import json
from playwright.async_api import async_playwright

TARGET_URL = "https://www.naukri.com/gen-ai-jobs?k=gen%20ai"
OUTPUT_FILE = "api_probe_results.json"


async def probe_api():
    """Load the page and capture all network requests to find the API endpoint."""
    captured_requests = []
    all_urls = []
    
    async with async_playwright() as p:
        # Use more realistic browser settings
        browser = await p.chromium.launch(
            headless=False,  # Run visible to see what happens
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York"
        )
        
        # Add extra stealth
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()
        
        # Capture ALL requests
        async def handle_request(request):
            all_urls.append({
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type
            })
        
        # Capture all responses
        async def handle_response(response):
            try:
                url = response.url
                content_type = response.headers.get("content-type", "")
                status = response.status
                
                # Log all API-like URLs
                if any(keyword in url.lower() for keyword in ['api', 'search', 'job', 'listing', 'data', 'jobs-listing']):
                    print(f"🔍 Interesting URL: {url[:120]}")
                
                # Look for JSON responses (likely API calls)
                if "json" in content_type or "application/json" in content_type:
                    # Try to get the JSON body
                    try:
                        body = await response.json()
                        request_data = {
                            "url": url,
                            "status": status,
                            "content_type": content_type,
                            "method": response.request.method,
                            "body": body
                        }
                        captured_requests.append(request_data)
                        print(f"✓ Captured JSON response from: {url[:100]}...")
                    except Exception as e:
                        print(f"✗ Could not parse JSON from {url[:80]}... - {e}")
            except Exception as e:
                print(f"Error handling response: {e}")
        
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        print(f"🌐 Loading page: {TARGET_URL}")
        print("⏳ Waiting for network activity and job listings to load...\n")
        
        # Navigate to the page
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        
        # Wait longer for dynamic content
        print("⏳ Waiting 15 seconds for JS to execute and load content...")
        await page.wait_for_timeout(15000)
        
        # Take a screenshot to see what rendered
        await page.screenshot(path="page_screenshot.png", full_page=True)
        print("📸 Screenshot saved to: page_screenshot.png")
        
        # Save the rendered HTML
        html_content = await page.content()
        with open("rendered_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("📄 Rendered HTML saved to: rendered_page.html\n")
        
        # Try to wait for job listings to appear
        try:
            await page.wait_for_selector(".jobTuple, .job-tuple, [class*='job'], article, [class*='srp']", timeout=5000)
            print("✓ Job listings detected on page\n")
        except Exception as e:
            print(f"⚠ Could not detect job listings: {e}\n")
        
        await browser.close()
    
    # Save results
    results = {
        "target_url": TARGET_URL,
        "total_json_responses": len(captured_requests),
        "total_requests": len(all_urls),
        "all_request_urls": all_urls,
        "captured_requests": captured_requests
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"📊 PROBE RESULTS")
    print(f"{'='*60}")
    print(f"Total JSON responses captured: {len(captured_requests)}")
    print(f"\nResults saved to: {OUTPUT_FILE}")
    
    # Print summary of captured endpoints
    if captured_requests:
        print(f"\n{'='*60}")
        print("📋 DISCOVERED ENDPOINTS:")
        print(f"{'='*60}\n")
        for idx, req in enumerate(captured_requests, 1):
            print(f"{idx}. {req['method']} {req['url']}")
            print(f"   Status: {req['status']}")
            if isinstance(req['body'], dict):
                # Show key fields if it looks like job data
                if 'jobDetails' in req['body'] or 'jobs' in req['body'] or 'data' in req['body']:
                    print(f"   🎯 LIKELY JOB DATA ENDPOINT")
                    print(f"   Keys: {list(req['body'].keys())[:10]}")
            print()
    else:
        print("\n⚠ No JSON API endpoints captured.")
        print("The site may use:")
        print("  - Server-side rendering with HTML only")
        print("  - Obfuscated/encrypted API calls")
        print("  - Anti-bot detection that blocked the request")
    
    return results


if __name__ == "__main__":
    print(f"{'='*60}")
    print("🔍 NAUKRI.COM API PROBE")
    print(f"{'='*60}\n")
    asyncio.run(probe_api())
