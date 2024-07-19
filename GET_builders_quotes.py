import logging
from chrome_functions import setup_driver, get_page, is_active_element, click_element
from csv_functions import read_entries_from_csv, write_price_data_dict_csv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parse_html_soup import is_match
import re
import time

builders_config = {"url": "https://www.builders.co.za/",
                   "selector":
                       {"search_bar": '.css-175oi2r.r-bnwqim > input[aria-labelledby="searchValue"]'}
                       }


def handle_builders_popups(driver):
    element = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div"
    )
    click_element(element)
    return not element.is_displayed


def parse_builders_search_result(results_element):
    pass


def get_active_element(driver, css_selector):
    elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
    for element in reversed(elements):
        if is_active_element(element):
            return element
    return None

def get_results_container(driver):
    results_box = get_active_element(driver, '#react-app div[data-testid="scroll-container"]')
    result_header_string = results_box.find_element(By.CSS_SELECTOR, 'h1[role="heading"]>span').text
    has_loaded = re.search(r'\(\d+\sproducts\)', result_header_string, re.IGNORECASE)
    if not has_loaded:
        time.sleep(3)
        results_box = get_active_element(driver, '#react-app div[data-testid="scroll-container"]')
        result_header_string = results_box.find_element(By.CSS_SELECTOR, 'h1[role="heading"]>span').string
        has_loaded = re.search(r'\(\d+\sproducts\)', result_header_string, re.IGNORECASE)
        if has_loaded:
            return results_box
    else:
        return results_box
    return None


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=".\\files\\builderssearch.log", level=logging.INFO)
    logging.info("start")
    driver = setup_driver()
    driver.implicitly_wait(10)
    get_page(driver, builders_config["url"])
    handle_builders_popups(driver)
    queries = read_entries_from_csv("queries.csv")
    price_data = {}
    for query in queries:
        search_box = get_active_element(driver, '#react-app div[data-testid="SearchBox"]')
        try:
            search_bar = search_box.find_element(By.CSS_SELECTOR, 'input[aria-labelledby="searchValue"]')
            search_bar.send_keys("_")
            clear_search_bar = search_box.find_element(By.CSS_SELECTOR, 'div[data-testid="searchClearButton"] svg')
            clear_search_bar.click()
            search_bar.send_keys(query)
            search_bar.send_keys(Keys.ENTER)
        except:
            price_data[query] = []
            continue
        results_container = get_results_container(driver)
        price_data[query] = parse_builders_search_result(results_container)
    write_price_data_dict_csv(price_data, "Builders")


if __name__ == "__main__":
    main()
