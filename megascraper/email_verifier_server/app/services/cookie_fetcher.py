"""
Automated Cookie Fetcher Service
Logs into check.emailverifier.online and extracts the session cookie
"""

import asyncio
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class CookieFetcher:
    """Automated cookie fetcher using Playwright"""
    
    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = True,
        timeout: int = 30000
    ):
        """
        Initialize cookie fetcher
        
        Args:
            email: Login email for emailverifier.online
            password: Login password
            headless: Run browser in headless mode
            timeout: Timeout for operations in milliseconds
        """
        self.email = email
        self.password = password
        self.headless = headless
        self.timeout = timeout
        self.login_url = "https://check.emailverifier.online/bulk-verify-email/index.php"
        
    async def fetch_cookie(self) -> Optional[str]:
        """
        Fetch session cookie by logging in
        
        Returns:
            PHPSESSID cookie value or None if failed
        """
        logger.info("🔐 Starting automated cookie fetch...")
        
        async with async_playwright() as p:
            browser = None
            try:
                # Launch browser
                logger.info("🌐 Launching browser...")
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navigate to login page
                logger.info(f"📍 Navigating to {self.login_url}")
                await page.goto(self.login_url, timeout=self.timeout)
                await page.wait_for_load_state('networkidle', timeout=self.timeout)
                
                # Check if already logged in (might redirect)
                current_url = page.url
                logger.info(f"📍 Current URL: {current_url}")
                
                # Try to find login form
                logger.info("🔍 Looking for login form...")
                
                # Common login form selectors - we'll try multiple patterns
                email_selectors = [
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[id="email"]',
                    'input[name="username"]',
                    'input[placeholder*="email" i]',
                    'input[placeholder*="Email" i]',
                ]
                
                password_selectors = [
                    'input[type="password"]',
                    'input[name="password"]',
                    'input[id="password"]',
                ]
                
                # Try to find email field
                email_field = None
                for selector in email_selectors:
                    try:
                        email_field = await page.wait_for_selector(selector, timeout=5000)
                        if email_field:
                            logger.info(f"✅ Found email field with selector: {selector}")
                            break
                    except:
                        continue
                
                if not email_field:
                    logger.error("❌ Could not find email input field")
                    # Take screenshot for debugging
                    await page.screenshot(path='login_page_debug.png')
                    logger.info("📸 Saved screenshot to login_page_debug.png for debugging")
                    return None
                
                # Try to find password field
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = await page.wait_for_selector(selector, timeout=5000)
                        if password_field:
                            logger.info(f"✅ Found password field with selector: {selector}")
                            break
                    except:
                        continue
                
                if not password_field:
                    logger.error("❌ Could not find password input field")
                    await page.screenshot(path='login_page_debug.png')
                    logger.info("📸 Saved screenshot to login_page_debug.png for debugging")
                    return None
                
                # Fill in credentials
                logger.info("✍️  Filling in credentials...")
                await email_field.fill(self.email)
                await password_field.fill(self.password)
                
                # Small delay to simulate human behavior
                await asyncio.sleep(1)
                
                # Find and click submit button
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Sign in")',
                    'button:has-text("Log in")',
                    'input[value*="Login" i]',
                    'input[value*="Sign in" i]',
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = await page.wait_for_selector(selector, timeout=5000)
                        if submit_button:
                            logger.info(f"✅ Found submit button with selector: {selector}")
                            break
                    except:
                        continue
                
                if not submit_button:
                    logger.warning("⚠️  Could not find submit button, trying to press Enter...")
                    await password_field.press('Enter')
                else:
                    logger.info("🖱️  Clicking login button...")
                    await submit_button.click()
                
                # Wait for navigation after login
                logger.info("⏳ Waiting for login to complete...")
                try:
                    await page.wait_for_load_state('networkidle', timeout=self.timeout)
                    await asyncio.sleep(2)  # Additional wait for redirects
                except PlaywrightTimeoutError:
                    logger.warning("⚠️  Timeout waiting for navigation, continuing anyway...")
                
                # Check if login was successful
                current_url = page.url
                logger.info(f"📍 After login URL: {current_url}")
                
                # Get all cookies
                cookies = await context.cookies()
                
                # Find PHPSESSID cookie
                phpsessid = None
                for cookie in cookies:
                    if cookie['name'] == 'PHPSESSID':
                        phpsessid = cookie['value']
                        logger.info(f"✅ Found PHPSESSID cookie: {phpsessid[:20]}... (truncated)")
                        break
                
                if not phpsessid:
                    logger.error("❌ PHPSESSID cookie not found after login")
                    logger.info(f"Available cookies: {[c['name'] for c in cookies]}")
                    # Take screenshot for debugging
                    await page.screenshot(path='after_login_debug.png')
                    logger.info("📸 Saved screenshot to after_login_debug.png for debugging")
                    return None
                
                logger.info("✅ Successfully fetched session cookie!")
                return phpsessid
                
            except PlaywrightTimeoutError as e:
                logger.error(f"⏱️  Timeout error: {e}")
                return None
            except Exception as e:
                logger.error(f"❌ Error fetching cookie: {e}", exc_info=True)
                return None
            finally:
                if browser:
                    await browser.close()
                    logger.info("🔒 Browser closed")


class CookieManager:
    """Manages cookie lifecycle with automatic refresh"""
    
    def __init__(
        self,
        email: str,
        password: str,
        refresh_interval_minutes: int = 50  # Refresh before 1 hour expiry
    ):
        """
        Initialize cookie manager
        
        Args:
            email: Login email
            password: Login password
            refresh_interval_minutes: How often to refresh cookie (default: 50 min)
        """
        self.fetcher = CookieFetcher(email, password)
        self.refresh_interval = timedelta(minutes=refresh_interval_minutes)
        self.current_cookie: Optional[str] = None
        self.last_refresh: Optional[datetime] = None
        self._lock = asyncio.Lock()
        
    async def get_cookie(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get current cookie, refreshing if needed
        
        Args:
            force_refresh: Force refresh even if not expired
            
        Returns:
            Current valid cookie or None
        """
        async with self._lock:
            now = datetime.now()
            
            # Check if refresh needed
            needs_refresh = (
                force_refresh or
                self.current_cookie is None or
                self.last_refresh is None or
                (now - self.last_refresh) >= self.refresh_interval
            )
            
            if needs_refresh:
                logger.info("🔄 Refreshing session cookie...")
                new_cookie = await self.fetcher.fetch_cookie()
                
                if new_cookie:
                    self.current_cookie = new_cookie
                    self.last_refresh = now
                    logger.info(f"✅ Cookie refreshed successfully at {now}")
                else:
                    logger.error("❌ Failed to refresh cookie")
                    
            return self.current_cookie
    
    def is_expired(self) -> bool:
        """Check if current cookie is likely expired"""
        if self.last_refresh is None:
            return True
        
        now = datetime.now()
        return (now - self.last_refresh) >= self.refresh_interval


async def fetch_cookie_cli(email: str, password: str, headless: bool = True) -> Optional[str]:
    """
    Convenience function for CLI usage
    
    Args:
        email: Login email
        password: Login password
        headless: Run in headless mode
        
    Returns:
        Cookie value or None
    """
    fetcher = CookieFetcher(email, password, headless=headless)
    return await fetcher.fetch_cookie()


if __name__ == "__main__":
    # Test the cookie fetcher
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    email = os.getenv('EMAILVERIFIER_EMAIL')
    password = os.getenv('EMAILVERIFIER_PASSWORD')
    
    if not email or not password:
        print("❌ Please set EMAILVERIFIER_EMAIL and EMAILVERIFIER_PASSWORD in .env")
        exit(1)
    
    async def test():
        cookie = await fetch_cookie_cli(email, password, headless=False)
        if cookie:
            print(f"✅ Successfully fetched cookie: {cookie}")
        else:
            print("❌ Failed to fetch cookie")
    
    asyncio.run(test())
