"""
Debug script to inspect Naukri page structure and find correct selectors
"""
import asyncio
from playwright.async_api import async_playwright


async def inspect_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible browser
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        url = "https://www.naukri.com/python-developer-jobs"
        print(f"Opening: {url}")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Wait for page to fully load
        await asyncio.sleep(5)
        
        # Try to find job cards with various selectors
        selectors_to_try = [
            'article',
            'div[class*="tuple"]',
            'div[class*="job"]',
            'div[class*="srp"]',
            '.cust-job-tuple',
            '[data-job-id]',
            'div.row',
        ]
        
        print("\n" + "="*70)
        print("TESTING SELECTORS:")
        print("="*70)
        
        for selector in selectors_to_try:
            try:
                elements = await page.locator(selector).all()
                print(f"\n✓ Selector '{selector}' found {len(elements)} elements")
                
                if elements and len(elements) > 0:
                    # Try to get some text from first element
                    first_elem = elements[0]
                    text = await first_elem.text_content()
                    print(f"  First element text (100 chars): {text[:100] if text else 'No text'}")
            except Exception as e:
                print(f"✗ Selector '{selector}' failed: {e}")
        
        # Get page title
        title = await page.title()
        print(f"\nPage title: {title}")
        
        # Save screenshot
        await page.screenshot(path="debug_screenshot.png", full_page=False)
        print("\n📸 Screenshot saved to: debug_screenshot.png")
        
        # Save HTML
        html = await page.content()
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("📄 HTML saved to: debug_page.html")
        
        print("\nKeeping browser open for 30 seconds for manual inspection...")
        await asyncio.sleep(30)
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_page())
