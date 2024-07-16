import logging
from chrome_functions import (setup_driver, get_page, get_search_bar, get_element_by_css_selector)
from csv_functions import (read_entries_from_csv, write_price_data_dict_csv)
from parse_html_soup import (is_match, remove_non_text_tags)
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
import re
import unidecode

plumblink_config = {
    "url" : "https://www.plumblink.co.za/",
    "selector" : {
        "search_bar" :  ["#search_mini_form", "input[id^=dfd-searchbox]"],
        "search_results" : "div[id^=dfd-results]",
        "search_result_card" : "df-result-products",
        "card_content" : "dfd-card-content"
    }
}

def parse_plumblink_search_result(soup, query):
    re_value = re.compile(('^'+plumblink_config['selector']['search_result_card']), re.IGNORECASE)
    result_cards = soup.find_all(id=re_value)
    # Products that came from the site search
    parsed_info = []
    for card in result_cards:
        if not(card):
            continue
        name = get_product_name(unidecode, card)
        if is_match(re, query, name):
            price = get_product_price(unidecode, card)
            link = get_product_link(card)
            parsed_info.append((name, price, link))
    return parsed_info
            
def get_product_name(decode, html_card):
    name = ""
    try:
        content = html_card.find("div", class_="dfd-card-content")
        name_tag = content.find("div", class_="dfd-card-title")
        name_raw = name_tag["title"]
        name = decode.unidecode(name_raw)
    except:
        pass
    return name
    
def get_product_price(decode , html_card):
    price = 0
    try:
        content = html_card.find("div", class_="dfd-card-content")
        price_tag = content.find("span", class_="dfd-card-price")
        price_raw = price_tag["data-value"]
        price = decode.unidecode(price_raw)
    except:
        pass
    return price

def get_product_link(html_card):
    link = ""
    try:
        content = html_card.find("div", class_="dfd-card-content")
        link_tag = content.find("a", class_="dfd-card-link")
        link = link_tag["href"]
    except:
        pass
    return link

def handle_plumblink_popups(driver):
    close_popup_tag = get_element_by_css_selector(driver, "#wpn-lightbox-close-newsletter")
    close_cookies_tag = get_element_by_css_selector(driver, ".m-button.m-decline")
    if close_popup_tag or close_cookies_tag:
        try:
            Alert(driver).dismiss()
        except:
            if close_popup_tag: close_popup_tag.click() # Close pop up
            if close_cookies_tag: close_cookies_tag.click() # Decline cookies
        
    
def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=".\\files\\plumblinksearch.log", level=logging.INFO)
    logging.info("start")
    driver = setup_driver()
    get_page(driver, plumblink_config['url'])
    # go = input("Close all the pop-up windows on the page and then press ENTER to continue ")
    driver.implicitly_wait(5) # Wait for Search bar to render
    handle_plumblink_popups(driver)
    search_bar = get_search_bar(driver, plumblink_config['selector']['search_bar'][0])
    if search_bar: search_bar.click()
    search_bar = get_search_bar(driver, plumblink_config['selector']['search_bar'][1])
    queries = read_entries_from_csv("queries.csv")
    price_data = {}
    for query in  queries:
        try:
            search_bar.clear()
            search_bar.send_keys(query)
        except AttributeError:
            search_bar = get_search_bar(driver, plumblink_config['selector']['search_bar'][1])
            if not search_bar: continue
            search_bar.clear()
            search_bar.send_keys(query)
        except:
            continue
        driver.implicitly_wait(3)  # Wait for page to finish loading
        html_results = driver.page_source
        soup = BeautifulSoup(html_results, "html.parser")
        cleaned_soup = remove_non_text_tags(soup)
        price_data[query] = parse_plumblink_search_result(cleaned_soup, query)
    write_price_data_dict_csv(price_data, "Plumblink")

if __name__ == "__main__":
    main()

