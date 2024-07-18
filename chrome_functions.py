import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)


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


def get_search_bar(driver, selector):
    """
    Use selector  to find searchbars on websites
    @inputs : driver, selector
    @returns: searchbar handle
    """
    search_bar = None
    try:
        search_bar = driver.find_element(By.CSS_SELECTOR, selector)
    except:
        search_bar = find_search_bar_common_keywords(driver)
    return search_bar


def find_search_bar_common_keywords(driver):
    """
    Use common keyword  to find searchbars on websites
    @inputs : driver, selector
    @returns: searchbar handle
    """
    search_bar = None
    search_bar_identifiers = [
        (By.NAME, "q"),
        (By.NAME, "search"),
        (By.ID, "search"),
        (By.CSS_SELECTOR, 'input[type="search"]'),
        (By.CSS_SELECTOR, 'input[type="text"]'),
    ]

    for by, value in search_bar_identifiers:
        try:
            search_bar = driver.find_element(by, value)
            if search_bar:
                break
        except:
            continue
    return


def get_element_by_css_selector(driver, selector):
    element = None
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        pass
    return element


def click_element(element):
    if element and element.is_enabled() and element.is_displayed():
        element.click()
        return True
    return False
