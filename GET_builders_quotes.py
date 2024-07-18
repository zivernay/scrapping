import logging
from chrome_functions import setup_driver, get_page, get_search_bar, click_element
from csv_functions import read_entries_from_csv, write_price_data_dict_csv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parse_html_soup import is_match
import re
import time

builders_config = {"url": "https://www.builders.co.za/"}


def handle_builders_popups(driver):
    element = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div"
    )
    click_element(element)
    return not element.is_displayed


def parse_builders_search_result(results_element):
    pass


def search(driver, query):
    search_url = builders_config["url"] + "search/?text=" + query
    get_page(driver, search_url)
    return driver


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
        driver = search(driver, query)
        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(
                EC.text_to_be_present_in_element(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/div[1]/div/h1/span",
                    ),
                    "products",
                )
            )
            time.sleep(1)
        except:
            time.sleep(5)
        driver.implicitly_wait(5)
        results_element = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[2]/div",
        )
        price_data[query] = parse_builders_search_result(results_element)
    write_price_data_dict_csv(price_data, "Builders")


if __name__ == "__main__":
    main()
