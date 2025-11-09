"""
Element finding and interaction utilities
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from config import WAIT_TIME
from helpers import print_log, scroll_to_element


def find_element_by_id(driver, element_id: str):
    """
    Find element by ID
    - Returns: WebElement if found, None otherwise
    """
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        scroll_to_element(driver, element)
        print_log(f"Found element with ID: {element_id}")
        return element
    except TimeoutException:
        print_log(f"Timeout: Could not find element with ID: {element_id}")
        return None


def find_element_by_xpath(driver, xpath: str):
    """
    Find element by XPath
    - Returns: WebElement if found, None otherwise
    """
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        scroll_to_element(driver, element)
        print_log(f"Found element with XPath")
        return element
    except TimeoutException:
        print_log(f"Timeout: Could not find element with XPath: {xpath}")
        return None


def find_element_by_class(driver, class_name: str):
    """
    Find element by Class Name
    - Returns: WebElement if found, None otherwise
    """
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        scroll_to_element(driver, element)
        print_log(f"Found element with class: {class_name}")
        return element
    except TimeoutException:
        print_log(f"Timeout: Could not find element with class: {class_name}")
        return None


def find_clickable_element(driver, xpath: str):
    """
    Find element and wait until it's clickable
    - Returns: WebElement if clickable, None otherwise
    """
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        scroll_to_element(driver, element)
        print_log(f"Found clickable element")
        return element
    except TimeoutException:
        print_log(f"Timeout: Element not clickable: {xpath}")
        return None


def wait_for_url_change(driver, current_url: str, timeout: int = WAIT_TIME) -> bool:
    """
    Wait for URL to change from current URL
    - Returns: True if URL changed, False if timeout
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.url_changes(current_url)
        )
        print_log(f"URL changed to: {driver.current_url}")
        return True
    except TimeoutException:
        print_log(f"Timeout: URL did not change")
        return False
