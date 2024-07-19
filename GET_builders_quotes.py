import logging
from chrome_functions import setup_driver, get_page, is_active_element, click_element, get_element_by_css_selector
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


def parse_builders_search_result(results_element, query):
    parsed_info = []
    cards = []
    if results_element:
        children = results_element.find_elements(By.CSS_SELECTOR, 'div[data-testid="label-rating"]')
        cards = [child.find_element(By.XPATH, "..") for child in children]
    else: return parsed_info
    for card in cards:
        if not card:
            continue
        name = get_product_name(card)
        if is_match(re, query, name):
            price = get_product_price(card)
            link = get_product_link(card)
            parsed_info.append((name, price, link))
    return parsed_info
    
def get_product_name(card):
    name_element = get_element_by_css_selector(card,'div[data-testid="label-wishListProductName"]')
    if name_element:
        return name_element.text
    return None
    

def get_product_price(card):
    price_element = get_element_by_css_selector(card, 'div[data-testid="discounted-wishListProductPrice"]>span')
    if price_element:
        return price_element.text
    return None

def get_product_link(card):
    link_element = get_element_by_css_selector(card, 'a[role="link"]')
    base_url = builders_config['url']
    if link_element:
        full_url = base_url + link_element.get_dom_attribute("href")
        return full_url
    return base_url
    

def get_active_element(driver, css_selector):
    elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
    for element in reversed(elements):
        if is_active_element(element):
            return element
    return None

    
def get_results_container(driver):
    results_box = get_active_element(driver, '#react-app div[data-testid="scroll-container"]')
    result_header = get_element_by_css_selector(results_box, 'h1[role="heading"]>span')
    has_loaded = None
    if result_header:
        result_header_string = result_header.text
        has_loaded = re.search(r'\(\d+\sproducts\)', result_header_string, re.IGNORECASE)
    if not has_loaded:
        time.sleep(3)
        results_box = get_active_element(driver, '#react-app div[data-testid="scroll-container"]')
        result_header = get_element_by_css_selector(results_box, 'h1[role="heading"]>span')
        if result_header:
            result_header_string = result_header.text
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
        price_data[query] = parse_builders_search_result(results_container, query)
    write_price_data_dict_csv(price_data, "Builders")


if __name__ == "__main__":
    main()
