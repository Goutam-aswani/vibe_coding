"""
Helper functions for browser automation
"""
import time
from random import uniform
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_log(message: str) -> None:
    """
    Print and log messages
    """
    logger.info(message)
    print(message)


def smart_delay(base_delay: float = 1.0) -> None:
    """
    Add a randomized delay to simulate human behavior
    - Prevents bot detection
    - base_delay: minimum delay in seconds
    """
    random_delay = base_delay + uniform(0.2, 0.8)
    time.sleep(random_delay)


def scroll_to_element(driver, element) -> None:
    """
    Scroll element into view using JavaScript
    - Smooth center-aligned scrolling
    """
    driver.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "smooth"});', element)


def close_browser(driver) -> None:
    """
    Safely close the browser
    """
    try:
        driver.quit()
        print_log("Browser closed successfully")
    except Exception as e:
        print_log(f"Error closing browser: {e}")
