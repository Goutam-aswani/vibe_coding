"""
Login Automation Bot - Main Implementation
Demonstrates core Selenium patterns for login automation
"""
import time
from selenium.webdriver.common.keys import Keys
from config import (
    USERNAME, PASSWORD, LOGIN_URL, HEADLESS_MODE, 
    STEALTH_MODE, CLICK_DELAY, WAIT_TIME
)
from helpers import print_log, smart_delay, close_browser
from element_finder import (
    find_element_by_id, find_element_by_xpath, 
    find_clickable_element, wait_for_url_change
)


class LoginBot:
    """
    Login automation bot for web applications
    """
    
    def __init__(self):
        """Initialize the bot with browser"""
        self.driver = None
        self.setup_browser()
    
    def setup_browser(self):
        """
        Setup and initialize Chrome WebDriver
        """
        try:
            if STEALTH_MODE:
                import undetected_chromedriver as uc
                chrome_options = uc.ChromeOptions()
                if HEADLESS_MODE:
                    chrome_options.add_argument("--headless")
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-extensions")
                
                self.driver = uc.Chrome(options=chrome_options)
            else:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                
                chrome_options = Options()
                if HEADLESS_MODE:
                    chrome_options.add_argument("--headless")
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-extensions")
                
                self.driver = webdriver.Chrome(options=chrome_options)
            
            print_log("✓ Browser initialized successfully")
            
        except Exception as e:
            print_log(f"✗ Error initializing browser: {e}")
            raise
    
    def navigate_to_login(self):
        """
        Navigate to the login page
        """
        try:
            print_log(f"→ Navigating to: {LOGIN_URL}")
            self.driver.get(LOGIN_URL)
            time.sleep(3)  # Wait for page to load
            print_log("✓ Login page loaded")
            return True
        except Exception as e:
            print_log(f"✗ Error navigating to login: {e}")
            return False
    
    def enter_username(self):
        """
        Enter username in the login form
        Tries multiple selectors (LinkedIn uses ID 'username')
        """
        try:
            print_log("→ Entering username...")
            
            # Try finding by ID (common approach)
            username_field = find_element_by_id(self.driver, "username")
            
            if not username_field:
                # Try alternative XPath if ID not found
                print_log("  Trying alternative selector...")
                username_field = find_element_by_xpath(
                    self.driver, 
                    "//input[@name='session_key' or @placeholder='Email or phone']"
                )
            
            if username_field:
                # Clear field first, then type
                username_field.clear()
                smart_delay(0.5)
                username_field.send_keys(USERNAME)
                smart_delay(CLICK_DELAY)
                print_log(f"✓ Username entered: {USERNAME}")
                return True
            else:
                print_log("✗ Could not find username field")
                return False
                
        except Exception as e:
            print_log(f"✗ Error entering username: {e}")
            return False
    
    def enter_password(self):
        """
        Enter password in the login form
        """
        try:
            print_log("→ Entering password...")
            
            # Try finding by ID (common approach)
            password_field = find_element_by_id(self.driver, "password")
            
            if not password_field:
                # Try alternative XPath
                print_log("  Trying alternative selector...")
                password_field = find_element_by_xpath(
                    self.driver,
                    "//input[@type='password']"
                )
            
            if password_field:
                password_field.clear()
                smart_delay(0.5)
                password_field.send_keys(PASSWORD)
                smart_delay(CLICK_DELAY)
                print_log("✓ Password entered")
                return True
            else:
                print_log("✗ Could not find password field")
                return False
                
        except Exception as e:
            print_log(f"✗ Error entering password: {e}")
            return False
    
    def click_login_button(self):
        """
        Click the login/sign-in button
        """
        try:
            print_log("→ Clicking login button...")
            
            # Try finding by XPath with text "Sign in"
            login_button = find_clickable_element(
                self.driver,
                "//button[@type='submit' and contains(text(), 'Sign in')]"
            )
            
            if not login_button:
                # Try alternative selectors
                print_log("  Trying alternative selector...")
                login_button = find_clickable_element(
                    self.driver,
                    "//button[contains(text(), 'Sign in') or contains(text(), 'Login')]"
                )
            
            if login_button:
                smart_delay(0.5)
                login_button.click()
                smart_delay(CLICK_DELAY)
                print_log("✓ Login button clicked")
                return True
            else:
                print_log("✗ Could not find login button")
                return False
                
        except Exception as e:
            print_log(f"✗ Error clicking login button: {e}")
            return False
    
    def wait_for_login_success(self, timeout: int = 15) -> bool:
        """
        Wait for login to complete by checking URL change
        """
        try:
            print_log("→ Waiting for login to complete...")
            initial_url = self.driver.current_url
            
            # Wait for URL to change
            if wait_for_url_change(self.driver, initial_url, timeout):
                time.sleep(2)  # Extra wait for page to fully load
                print_log(f"✓ Login successful! Current URL: {self.driver.current_url}")
                return True
            else:
                print_log("✗ Login did not complete - URL did not change")
                return False
                
        except Exception as e:
            print_log(f"✗ Error waiting for login: {e}")
            return False
    
    def execute_login(self) -> bool:
        """
        Execute the complete login sequence
        Returns: True if login successful, False otherwise
        """
        print_log("\n" + "="*60)
        print_log("STARTING LOGIN AUTOMATION")
        print_log("="*60 + "\n")
        
        # Step 1: Navigate to login page
        if not self.navigate_to_login():
            return False
        
        smart_delay(1)
        
        # Step 2: Enter username
        if not self.enter_username():
            return False
        
        smart_delay(1)
        
        # Step 3: Enter password
        if not self.enter_password():
            return False
        
        smart_delay(1)
        
        # Step 4: Click login button
        if not self.click_login_button():
            return False
        
        # Step 5: Wait for login to complete
        if not self.wait_for_login_success():
            return False
        
        print_log("\n" + "="*60)
        print_log("LOGIN COMPLETED SUCCESSFULLY!")
        print_log("="*60 + "\n")
        
        return True
    
    def keep_browser_open(self, seconds: int = 30):
        """
        Keep browser open for specified duration
        Useful for manual inspection after automation
        """
        try:
            print_log(f"→ Keeping browser open for {seconds} seconds...")
            time.sleep(seconds)
            print_log("✓ Time's up, closing browser...")
        except KeyboardInterrupt:
            print_log("\n→ Browser closed by user (Ctrl+C)")
    
    def close(self):
        """
        Close the browser
        """
        close_browser(self.driver)


def main():
    """
    Main entry point
    """
    bot = LoginBot()
    
    try:
        # Execute login
        success = bot.execute_login()
        
        if success:
            # Keep browser open for inspection (optional)
            bot.keep_browser_open(seconds=10)
        
    except Exception as e:
        print_log(f"Fatal error: {e}")
    
    finally:
        bot.close()


if __name__ == "__main__":
    main()
