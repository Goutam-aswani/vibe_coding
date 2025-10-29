"""
Mailmeteor Email Checker Automation - Using Playwright (Browser Automation)
Best for: Testing, small scale, no budget
Cost: Free (but slower and less reliable)
"""

import asyncio
from typing import Dict, Optional
from playwright.async_api import async_playwright, Page


class EmailCheckerWithPlaywright:
    def __init__(self, headless: bool = False):
        """
        Initialize email checker with Playwright browser automation
        
        Args:
            headless: Run browser in headless mode (False recommended for Turnstile)
        """
        self.headless = headless
        self.url = "https://mailmeteor.com/email-checker"
        
    async def check_email(self, email: str) -> Optional[Dict]:
        """
        Check if an email is valid using browser automation
        
        Args:
            email: Email address to verify
            
        Returns:
            Dict with verification results or None if failed
        """
        print(f"\n📧 Checking email: {email}")
        
        async with async_playwright() as p:
            try:
                # Launch browser with stealth settings
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                    ]
                )
                
                # Create context with realistic settings
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                )
                
                page = await context.new_page()
                
                # Add stealth scripts
                await page.add_init_script("""
                    // Remove webdriver flag
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Mock chrome object
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Mock permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                    );
                """)
                
                print("🌐 Loading page...")
                await page.goto(self.url, wait_until='networkidle')
                
                print("✍️  Filling email...")
                await page.fill('#email-to-check', email)
                
                print("🔘 Clicking verify button...")
                await page.click('button[type="submit"]')
                
                print("⏳ Waiting for CAPTCHA to solve and results to load...")
                print("   (This may take 10-30 seconds...)")
                
                # Wait for result container to appear
                try:
                    await page.wait_for_selector('.result-container', timeout=45000)
                except:
                    print("❌ Timeout waiting for results. CAPTCHA might have failed.")
                    await browser.close()
                    return None
                
                print("📊 Extracting results...")
                
                # Extract status
                status_element = await page.query_selector('.result-header h3')
                status_text = await status_element.inner_text() if status_element else 'unknown'
                status = status_text.lower().strip()
                
                # Extract detailed checks
                checks = {}
                check_items = await page.query_selector_all('.result-details-item')
                
                for item in check_items:
                    title_elem = await item.query_selector('span.mr-2')
                    badge_elem = await item.query_selector('.badge')
                    
                    if title_elem and badge_elem:
                        title = await title_elem.inner_text()
                        check_status = await badge_elem.inner_text()
                        
                        # Map titles to keys
                        key_map = {
                            'Format': 'format',
                            'Professional': 'disposable',
                            'Domain status': 'domain_status',
                            'Mailbox': 'smtp'
                        }
                        
                        key = key_map.get(title.strip(), title.lower())
                        checks[key] = check_status.lower().strip()
                
                await browser.close()
                
                result = {
                    'email': email,
                    'status': status,
                    'valid': status == 'valid',
                    'checks': checks
                }
                
                # Print result
                status_emoji = "✅" if result['valid'] else "❌"
                print(f"{status_emoji} Status: {result['status'].upper()}")
                for check_name, check_status in checks.items():
                    print(f"   {check_name}: {check_status}")
                
                return result
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                try:
                    await browser.close()
                except:
                    pass
                return None
    
    async def check_emails_batch(self, emails: list, delay: int = 5) -> list:
        """
        Check multiple emails with delay between requests
        
        Args:
            emails: List of email addresses
            delay: Seconds to wait between requests (default 5)
            
        Returns:
            List of verification results
        """
        results = []
        
        print(f"🚀 Checking {len(emails)} emails with {delay}s delay...")
        print(f"⚠️  Browser will open in {'headless' if self.headless else 'visible'} mode")
        
        for i, email in enumerate(emails, 1):
            print(f"\n{'=' * 60}")
            print(f"Progress: {i}/{len(emails)}")
            print(f"{'=' * 60}")
            
            result = await self.check_email(email)
            results.append(result)
            
            # Delay between requests (except last one)
            if i < len(emails):
                print(f"\n⏳ Waiting {delay} seconds before next check...")
                await asyncio.sleep(delay)
        
        return results


async def main():
    """Example usage"""
    
    # Initialize checker
    # Set headless=True for background operation (may have lower success rate)
    # Set headless=False to see browser (better for Turnstile)
    checker = EmailCheckerWithPlaywright(headless=False)
    
    # Example 1: Check single email
    print("=" * 60)
    print("EXAMPLE 1: Single Email Check")
    print("=" * 60)
    result = await checker.check_email("corentin@mailmeteor.com")
    
    if result:
        print(f"\n✅ Successfully checked: {result['email']}")
        print(f"   Valid: {result['valid']}")
    
    # Example 2: Check multiple emails
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Batch Email Check")
    print("=" * 60)
    
    emails_to_check = [
        "elon@spacex.com",
        "invalid@mailmeteor.com",
        "test@example.com",
    ]
    
    results = await checker.check_emails_batch(emails_to_check, delay=5)
    
    # Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r is not None]
    valid_count = sum(1 for r in successful if r.get('valid'))
    
    print(f"✅ Successfully checked: {len(successful)}/{len(results)}")
    print(f"✅ Valid emails: {valid_count}/{len(successful)}")
    print(f"❌ Invalid emails: {len(successful) - valid_count}/{len(successful)}")
    
    if len(successful) < len(results):
        failed_count = len(results) - len(successful)
        print(f"⚠️  Failed to check: {failed_count}/{len(results)}")


if __name__ == "__main__":
    # Install dependencies first:
    # pip install playwright
    # playwright install chromium
    
    asyncio.run(main())
