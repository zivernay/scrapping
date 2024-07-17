import logging
from chrome_functions import setup_driver, get_page, get_search_bar
from csv_functions import read_entries_from_csv, write_price_data_dict_csv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parse_html_soup import is_match
import re
import time


plumbit_config = {
    "url": "https://plumbitonline.co.za/search",
    "selector": {
        "search_bar": "#search",
        "search_results": "row",
        "result_card": "eurus-product-box",
    },
}


def handle_plumbit_popups(driver):
    pass


def parse_plumbit_search_result(elements, query):
    parsed_info = []
    for element in elements:
        if not (element):
            continue
        name = get_product_name(element)
        if is_match(re, query, name):
            price = get_product_price(element)
            link = get_product_link(element)
            parsed_info.append((name, price, link))
    return parsed_info


def get_product_name(element):
    name_container_element = element.find_element(By.TAG_NAME, "eurus-product-box-link")
    name_element = name_container_element.find_element(By.TAG_NAME, "a")
    name = name_element.text
    return name


def get_product_price(element):
    price_container_element = element.find_element(By.TAG_NAME, "eurus-price")
    main_price_element = price_container_element.find_element(
        By.CSS_SELECTOR, "span.price_main"
    )
    decimal_price_element = price_container_element.find_element(
        By.CSS_SELECTOR, "span.price_cents"
    )
    price = main_price_element.text + decimal_price_element.text
    return price


def get_product_link(element):
    container_element = element.find_element(By.TAG_NAME, "eurus-product-box-link")
    link_element = container_element.find_element(By.TAG_NAME, "a")
    link = link_element.get_dom_attribute("href")
    return "https://plumbitonline.co.za/" + link


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=".\\files\\plumblitsearch.log", level=logging.INFO)
    logging.info("start")
    driver = setup_driver()
    get_page(driver, plumbit_config["url"])
    driver.implicitly_wait(5)  # Wait for Search bar to render
    handle_plumbit_popups(driver)
    search_bar = get_search_bar(driver, plumbit_config["selector"]["search_bar"])
    if search_bar:
        search_bar.click()
    queries = read_entries_from_csv("queries.csv")
    price_data = {}
    for query in queries:
        if driver.current_url != plumbit_config["url"]:
            get_page(driver, plumbit_config["url"])
        search_bar = get_search_bar(driver, plumbit_config["selector"]["search_bar"])
        try:
            search_bar.clear()
            search_bar.send_keys(query)
            search_bar.send_keys(Keys.ENTER)
        except:
            price_data[query] = []
            continue
        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".my-3 > span"), "Total Results:"))
            time.sleep(1.5)
        except:
            time.sleep(5)
        driver.implicitly_wait(5)
        result_elements = driver.find_elements(
            By.TAG_NAME, plumbit_config["selector"]["result_card"]
        )
        price_data[query] = parse_plumbit_search_result(result_elements, query)
    write_price_data_dict_csv(price_data, "Plumbit")


if __name__ == "__main__":
    main()
