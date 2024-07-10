import logging
from csv_functions import read_entries_from_csv, write_price_data_dict_csv
from chrome_functions import setup_driver, handle_popup, get_page
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import unidecode
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


def parse_google_search_page(logger, decode_lib, soup):
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
        name = get_product_name(decode_lib, logger,card)
        price = get_product_price(decode_lib, logger, card)
        product_link = get_product_link(logger, card)
        shop = get_shop_name(decode_lib, logger, card)
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
    strings = html_card.stripped_strings
    for string in strings:
        text = decode.unidecode(string)
        try:
            price = re.search(r"(ZAR|R)\s?(\d+)(,|\.)?(\d*)?", text)
            if price:
                return price.group(0)
        except:
            logger.info("Couldn't get price")
    return 0


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
        name = name_tag.find("div", class_="VuuXrf").string
        name = unidecode.unidecode(name)
    except:
        logger.info("failed to get a name")
    return name


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

def remove_non_text_tags(logger, soup_obj):
    tags = ['script', 'img', 'style', 'svg']
    for tag in tags:
        try:
            for tag_data in soup_obj.find_all(tag):
                tag_data.decompose()
        except:
            continue
    return soup_obj
    
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
        page = get_page(driver, url)
        page_soup = BeautifulSoup(page, "html.parser")
        page_soup_filtered = remove_non_text_tags(logger, page_soup)
        res = parse_google_search_page(logger, unidecode, page_soup_filtered)
        res_filtered = filter_parsed_result_list(re, res, query)
        price_data[query] = res_filtered
        logger.info(res)
    write_price_data_dict_csv(price_data)
    logging.info("finished")


if __name__ == "__main__":
    main()
