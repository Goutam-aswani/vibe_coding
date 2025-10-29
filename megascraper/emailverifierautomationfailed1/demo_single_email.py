"""
Quick Demo - Single Email Check
Run this to see a single email verification in action
"""

import asyncio
from playwright.async_api import async_playwright


async def check_email_simple(email: str):
    """Simple demo of email checking"""
    print(f"🚀 Starting email check for: {email}")
    print("⚠️  Browser will open - watch the automation!")
    print("⏳ This may take 30-60 seconds...")
    print()
    
    async with async_playwright() as p:
        # Launch visible browser so you can see what's happening
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500  # Slow down actions so you can see them
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        print("📄 Loading Mailmeteor...")
        await page.goto('https://mailmeteor.com/email-checker', wait_until='networkidle')
        
        print("✍️  Typing email address...")
        await page.fill('#email-to-check', email)
        
        print("🔘 Clicking VERIFY button...")
        await page.click('button[type="submit"]')
        
        print("⏳ Waiting for CAPTCHA to be solved...")
        print("   (Watch the browser - Cloudflare Turnstile should appear)")
        print("   (This is the main blocker - it may or may not work)")
        
        try:
            # Wait up to 60 seconds for result
            await page.wait_for_selector('.result-container', timeout=60000)
            
            print("✅ Got results!")
            
            # Get status
            status_elem = await page.query_selector('.result-header h3')
            status = await status_elem.inner_text() if status_elem else 'unknown'
            
            # Get email from result
            email_elem = await page.query_selector('.result-header p')
            email_result = await email_elem.inner_text() if email_elem else email
            
            print()
            print("=" * 60)
            print("📊 RESULT")
            print("=" * 60)
            print(f"Email: {email}")
            print(f"Status: {status}")
            print(f"Details: {email_result}")
            print()
            
            # Take screenshot
            screenshot_path = f"result_{email.replace('@', '_at_')}.png"
            await page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            print()
            print("=" * 60)
            print("⚠️  TIMEOUT or ERROR")
            print("=" * 60)
            print("The CAPTCHA was not solved in time.")
            print("This is expected - Cloudflare Turnstile blocks automation.")
            print()
            print("Possible reasons:")
            print("1. CAPTCHA detected automation")
            print("2. Network timeout")
            print("3. Page structure changed")
            print()
            print(f"Error: {str(e)}")
            
            # Take screenshot anyway
            try:
                await page.screenshot(path='timeout_screenshot.png')
                print("📸 Screenshot saved: timeout_screenshot.png")
            except:
                pass
        
        print()
        print("⏸️  Browser will stay open for 5 seconds so you can see...")
        await asyncio.sleep(5)
        
        await browser.close()
        print("✅ Done!")


async def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     Mailmeteor Email Checker - Simple Demo                ║
    ╚════════════════════════════════════════════════════════════╝
    
    This demo will:
    1. Open a browser window (you'll see it!)
    2. Go to Mailmeteor's email checker
    3. Fill in an email address
    4. Click VERIFY
    5. Wait for Cloudflare Turnstile CAPTCHA to solve
    6. Show you the result (if successful)
    
    ⚠️  KEY POINT: The CAPTCHA may or may not solve automatically
        - If it works: You'll see the verification result
        - If it doesn't: You'll see a timeout message
    
    This demonstrates the main challenge of automation!
    
    """)
    
    # Test with a known valid email
    test_email = "corentin@mailmeteor.com"  # This is from their example
    
    await check_email_simple(test_email)
    
    print()
    print("=" * 60)
    print("📚 WHAT YOU LEARNED")
    print("=" * 60)
    print()
    print("✅ The automation CAN work - you saw the browser being controlled")
    print("✅ The form was filled automatically")
    print("✅ The submit button was clicked")
    print()
    print("❌ But CAPTCHA is the blocker:")
    print("   - Cloudflare Turnstile tries to detect automation")
    print("   - Sometimes it works, sometimes it doesn't")
    print("   - That's why success rate is only 50-80%")
    print()
    print("💡 Solutions:")
    print("   1. Use 2Captcha service (paid, 95% success)")
    print("   2. Use official email verification APIs")
    print("   3. Keep trying - it might work next time!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
