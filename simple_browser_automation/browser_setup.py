"""
Browser initialization and configuration
"""
from config import HEADLESS_MODE, STEALTH_MODE, WAIT_TIME
from helpers import print_log

try:
    if STEALTH_MODE:
        import undetected_chromedriver as uc
        chrome_options = uc.ChromeOptions()
    else:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()

    # Browser configuration
    if HEADLESS_MODE:
        chrome_options.add_argument("--headless")
    
    # Start maximized for better visibility
    chrome_options.add_argument("--start-maximized")
    
    # Disable notifications
    chrome_options.add_argument("--disable-notifications")
    
    # Performance optimization
    chrome_options.add_argument("--disable-extensions")

    print_log("Browser configuration ready")

except Exception as e:
    print_log(f"Error in browser setup: {e}")
    raise
