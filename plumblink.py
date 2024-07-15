import logging
from chrome_functions import (setup_driver, get_page, get_search_bar, get_element_by_css_selector)
from csv_functions import read_entries_from_csv
from bs4 import BeautifulSoup

plumblink_config = {
    "url" : "https://www.plumblink.co.za/",
    "selector" : {
        "search_bar" :  ["#search_mini_form", "input[id^=dfd-searchbox]"],
        "search_results" : "div[id^=dfd-results]",
        "search_result_card" : "div[id^=df-result-products]"
    }
}

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=".\\files\\plumblinksearch.log", level=logging.INFO)
    logging.info("start")
    driver = setup_driver()
    get_page(driver, plumblink_config['url'])
    search_bar = get_search_bar(driver, plumblink_config['selector']['search_bar'][0])
    search_bar.click()
    search_bar = get_search_bar(driver, plumblink_config['selector']['search_bar'][1])
    queries = read_entries_from_csv("queries.csv")
    for query in  queries:
        search_bar.clear()
        search_bar.send_keys(query)
        results = get_element_by_css_selector(driver, plumblink_config['selector']['search_results'])
        driver.implicitly_wait(2)  # Wait up to 30 seconds
        html_results = driver.page_source
        soup = BeautifulSoup(html_results, "lxml")
    print(soup.text)

if __name__ == "__main__":
    main()

def plumbLinkSearchResultParser(html):
    """
    Parses the provided HTML to extract all product information including names and prices.

    Args:
        html (str): The HTML content as a string.

    Returns:
        list: A list of dictionaries, each containing:
            - name (str): The name of the product.
            - price (str): The price of the product.
            - found (bool): A boolean indicating if the values were found.
    """
    # Initialize the BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all product cards
    product_cards = soup.select('div.dfd-card div.dfd-card-content')

    # Initialize the list to hold all product information
    products = []
    
    for card in product_cards:
        # Initialize default values for each product
        product_info = {
            'name': None,
            'price': None,
            'found': False
        }
        
        # Extract product name
        name_tag = card.find('div', class_='dfd-card-title')
        if name_tag:
            product_info['name'] = name_tag.text.strip()

        # Extract product price
        price_tag = card.find('span', class_='dfd-card-price')
        if price_tag:
            product_info['price'] = price_tag.text.strip()

        # Set the 'found' flag if both name and price were found
        if product_info['name'] and product_info['price']:
            product_info['found'] = True
        
        # Add the product info to the list
        products.append(product_info)
    
    return products


