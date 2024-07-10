import logging
from csv_functions import read_entries_from_csv, write_price_data_dict_csv
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from scrap import read_entries_from_csv
from scrap import setup_driver
import time
import random
import unidecode
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)
import re


def build_google_search_url(
        urlencode,
        logger,
    query,
    language="en",
    domain="co.za",
    region="ZA",
    exact_query="",
    exclude="",
    any_of_the_words="",
    start="",
    end="",
    filetype="",
    date_released="all",
    where_to_search="any",
    sitesearch="",
):
    """
    Creates a Google search URL with specified parameters.

    Args:
        query: The search query string.
        language: The language code for search results (default: "en").
        region: The Google search region code (default: "ZA").

    Returns:
        A string containing the complete Google search URL.
    """
    base_url = "https://www.google." + domain + "/search?"
    url_params = {
        "hl": language,
        "as_q": query,
        "as_epq": exact_query,
        "as_oq": any_of_the_words,
        "as_eq": exclude,
        # "as_nlo": start,
        # "as_nhi": end,
        "lr": "lang_" + language,  # Combine language and parameter name
        "cr": "country" + region,  # Combine country and parameter name
        # "as_qdr": date_released,  # Date released
        # "as_sitesearch": sitesearch,  # Empty for whole web search
        # "as_occt": where_to_search,
        # "as_filetype": filetype,  # Empty for no file type restriction
    }
    # Encode parameters for URL inclusion
    encoded_params = urlencode(url_params)
    url = base_url + encoded_params
    logger.info(url)
    return url


def parse_google_search_page(bs4, logger, page):
    soup = bs4(page, "html5lib", from_encoding="UTF-8")
    search_results_div = soup.find("div", id="rso")
    if search_results_div == None:
        logger.info("The results page was empty")
        return
    search_results_cards = search_results_div.find_all("div", class_="MjjYud")
    if len(search_results_cards) == 0:
        logger.info("Result cards not found")
        return
    parsed_info = []
    for card in search_results_cards:
        name = get_product_name(card)
        price = get_product_price(card)
        product_link = get_product_link(card)
        shop = get_shop_name(card)
        parsed_info.append((name, price, product_link, shop))
    return parsed_info


def get_product_name(decode, logger, html_card):
    name = ""
    try:
        name = html_card.find("h3").string
        name = decode.unidecode(name)
        name = name.replace("Search results for:", "")
        name = name.replace("'", "")
    except:
        logger.info("failed to find the name")
    return name


def get_product_price(decode, logger, html_card):
    price = 0
    text = html_card.get_text()
    text = decode.unidecode(text)
    try:
        price = re.search(r"(ZAR|R)\s?(\d+)(,|.)?(\d*)?", text)
        return price.group(0)
    except:
        logger.info("Couldn't get price")
    return price


def get_product_link(logger, html_card):
    link = ""
    try:
        link_tag = html_card.find("a")
        link = link_tag["href"]
    except:
        logger.info("Failed to extract link")
    return link


def get_shop_name(decode, logger, html_card):
    name = ""
    try:
        name_tag = html_card.find("div", class_="CA5RN")
        name_tag = name_tag.find("div", class_="VuuXrf")
        name = name_tag.get_text()
        name = unidecode.unidecode(name)
    except:
        logger.info("failed to get a name")
    return name


def get_page(driver, time_module, rand_module, url):
    driver.get(url)
    time_module.sleep(rand_module.uniform(0, 2))  # Random delay to mimic human behavior
    driver.implicitly_wait(2)  # Wait up to 30 seconds
    return driver.page_source


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


def is_match(re_module, text1: str, text2: str):
    """Compare to the first text to the second one by checking if all the keywords are in the second text"""
    words = re_module.findall(r"\w*", text1)
    for word in words:
        if len(word) <= 1:
            continue
        if not (word.lower() in text2.lower()):
            return False
    return True


def filter_parsed_result_list(re, arr: list, query: str):
    filtered_data = []
    for data in arr:
        if is_match(re, query, data[0]):
            filtered_data.append(data)
    return filtered_data




def main():
    logger = logging.getLogger(__name__)
    driver = setup_driver()
    logging.basicConfig(filename="gsearch.log", level=logging.INFO)
    logging.info("start")
    csv_file_path = "queries.csv"
    queries = read_entries_from_csv(csv_file_path)
    driver.get(build_google_search_url(urlencode, logger, "test"))
    handle_popup(driver, logger)
    price_data = {}
    for query in queries:
        url = build_google_search_url(urlencode, logger, query)
        r = get_page(driver, time, random, url)
        res = parse_google_search_page(BeautifulSoup, logger, r)
        res_filtered = filter_parsed_result_list(re, res, query)
        price_data[query] = res_filtered
        logger.info(res)
    write_price_data_dict_csv(price_data)
    logging.info("finished")


# if __main__ == "__main__":
main()
