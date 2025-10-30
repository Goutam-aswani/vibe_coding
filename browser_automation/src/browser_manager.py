import asyncio
import os
import sys
import logging
from typing import Optional, Dict
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Fix for Python 3.13+ on Windows - Playwright needs ProactorEventLoop
if sys.platform == 'win32':
    try:
        # For Python 3.8+, set the event loop policy to ProactorEventLoop
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except AttributeError:
        pass


class BrowserManager:
    """Manages browser instance and contexts for LinkedIn automation"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.headless = os.getenv("HEADLESS", "false").lower() == "true"
        self.slow_mo = int(os.getenv("SLOW_MO", "100"))
        self.timeout = int(os.getenv("TIMEOUT", "30000"))
        self.profile_path = os.getenv("BROWSER_PROFILE_PATH", "./browser_data")
        
    async def initialize(self):
        """Initialize Playwright and browser with stealth settings"""
        try:
            logger.info("Initializing browser...")
            self.playwright = await async_playwright().start()
            
            # Create profile directory if it doesn't exist
            Path(self.profile_path).mkdir(parents=True, exist_ok=True)
            
            # Launch browser with persistent context to maintain login
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ],
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation', 'notifications'],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )
            
            # Get or create page
            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()
            
            # Add additional stealth scripts to avoid detection
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = {
                    runtime: {}
                };
            """)
            
            # Set default timeout
            self.page.set_default_timeout(self.timeout)
            
            logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def ensure_logged_in(self) -> bool:
        """Check if user is logged in to LinkedIn"""
        try:
            await self.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # Check if we're on the feed (logged in) or login page
            current_url = self.page.url
            if "feed" in current_url or "mynetwork" in current_url:
                logger.info("User is already logged in")
                return True
            else:
                logger.warning("User is not logged in. Please log in manually.")
                # Wait for manual login
                logger.info("Waiting for user to log in... (timeout 120s)")
                await self.page.wait_for_url("**/feed/**", timeout=120000)
                logger.info("User logged in successfully")
                return True
                
        except Exception as e:
            logger.error(f"Login check failed: {e}")
            return False
    
    async def navigate_to_job(self, job_url: str) -> bool:
        """Navigate to a job posting"""
        try:
            logger.info(f"Navigating to job: {job_url}")
            await self.page.goto(job_url, wait_until="domcontentloaded")
            await asyncio.sleep(2)  # Human-like delay
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to job: {e}")
            return False
    
    async def take_screenshot(self, name: str) -> str:
        """Take a screenshot and return the path"""
        try:
            screenshot_dir = Path("./screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            
            screenshot_path = screenshot_dir / f"{name}.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=False)
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    async def click_easy_apply(self) -> bool:
        """Click the Easy Apply button"""
        try:
            logger.info("Looking for Easy Apply button...")
            
            # Try multiple selectors for Easy Apply button
            selectors = [
                'button.jobs-apply-button',
                'button[aria-label*="Easy Apply"]',
                'button:has-text("Easy Apply")',
                '.jobs-apply-button'
            ]
            
            for selector in selectors:
                try:
                    button = await self.page.wait_for_selector(selector, timeout=5000)
                    if button:
                        # Scroll into view
                        await button.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        
                        # Click the button
                        await button.click()
                        logger.info("Easy Apply button clicked")
                        
                        # Wait for modal to appear
                        await asyncio.sleep(2)
                        return True
                except:
                    continue
            
            logger.error("Easy Apply button not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to click Easy Apply: {e}")
            return False
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def get_page(self) -> Page:
        """Get the current page instance"""
        return self.page
