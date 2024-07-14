import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (NoSuchElementException, ElementClickInterceptedException)

def setup_driver():
    """
    Setup Chrome browser for surfing
    """
    driver = webdriver.Chrome()
    return driver

def handle_popup(driver, logger):
    try:
        # reject_button = driver.find_element(By.CSS_SELECTOR, 'input.basebutton.button[type="submit"][value="Reject all"]')
        reject_button = driver.find_element(By.CSS_SELECTOR, "#W0wltc > div")
        reject_button.click()
    except:
        logger.info("Failed to find the button")
        # List of texts to look for in the popup
        texts_to_look_for = ["Reject all", "Reject", "Cancel"]

        # List of tags to search for these texts
        tags_to_search = ["button", "input", "a", "span", "div"]

        # Iterate over each tag
        for tag in tags_to_search:
            try:
                # Find all elements with the given tag
                elements = driver.find_elements(By.TAG_NAME, tag)

                # Iterate over each element
                for element in elements:
                    # Check if the element text matches any of the texts to look for
                    for text in texts_to_look_for:
                        if text.lower() in element.text.lower():
                            try:
                                element.click()
                                logger.info(f"Clicked the element with text: {text}")
                                return True  # Exit the function after clicking
                            except (
                                ElementClickInterceptedException,
                                NoSuchElementException,
                            ) as e:
                                logger.warning(f"Could not click the element: {e}")
            except NoSuchElementException:
                logger.debug(f"No elements found with tag: {tag}")

    logger.info("No matching element found to reject the pop-up.")
    return False

def get_page(driver, url):
    driver.get(url)
    time.sleep(random.uniform(0, 2))  # Random delay to mimic human behavior
    driver.implicitly_wait(2)  # Wait up to 30 seconds
    return driver.page_source
