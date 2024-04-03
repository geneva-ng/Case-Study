""" This script fills a ChromaDB collection with vector embeddings from a large 
    selection of products from a baseURL category page. Each of the functions 
    is annotated individually below for your convenience."""

from vector_store import VectorStore
from openai import OpenAI 
import os
import json
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
load_dotenv()

# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
# )

# SINGLE-PAGE STEP 1: scrape raw product data from a single product page 
def scrape(url):
    """
    Scrapes text from specified classes at the given URL and returns it as a single string.
    
    :param url: URL of the prodyct page to scrape.
    :return: A single string containing all the scraped text, with no newlines.
    """
    hardcoded_classes = ["mb-4", "qna__question js-qnaResponse"]  # Hardcoded classes to search for
    combined_text = []
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for class_name in hardcoded_classes:
            elements = soup.find_all(class_=class_name)
            for element in elements:
                combined_text.append(element.get_text(strip=True))
        return ' '.join(combined_text)
    else:
        return f"Failed to retrieve the webpage. Status code: {response.status_code}"

# SINGLE-PAGE STEP 2: parse scraped content into a natural language paragraph summary of a product's details
def parse(input_string, client):
    """
    Processes the raw web-scraped data into natural language for it's future embedding to be accurate. 

    :param input_string: raw data scraped from the product page.
    :return: A string response that's a natural language paragraph version of the raw data
    """
    one_line_string = ' '.join(input_string.strip().split())

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Read this text, and return it in a continuous line of properly spaced and formatted text, according to English conventions."},
            {"role": "user", "content": one_line_string},
        ]
    )
    return response.choices[0].message.content

# SINGLE-PAGE STEP 3: jsonify that product summary paragraph to later feed into ChromaDB
def to_json(input_string):
    """
    Creates a JSON-structured string with a single field named 'text' that maps to the product information.
    
    :param input_string: The string to be included in the JSON structure.
    :return: A string representing the JSON structure.
    """
    data = {"text": input_string}
    json_structure = json.dumps(data, indent=4)
    return json_structure

# COMPLETE SINGLE-PAGE SCRAPE: combines above functions to go from a single product URL to a single JSON
def url_to_json(url, client):
    raw_data = scrape(url)
    paragraph = parse(raw_data, client)  
    return to_json(paragraph)

# SOURCE SET OF PRODUCTS FROM ONE CATEGORY: start with a product category baseURL and end with a set of all product pages that stem from that baseURL. 
def get_product_links(baseURL, recursion_depth_level):
    """
    Takes a base URL for a product category and returns a set of product links.

    :param baseURL: base URL for product category
    :param recursion_depth_level: max depth to search for product links starting from baseURL
    :return: a python set of product links
    """
    print("Sourcing product links from category...")

    parsed_url = urlparse(baseURL)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    category_segment = parsed_url.path.split('/')[-1]
    category_keyword = category_segment.replace("-Parts.htm", "") + "-"

    product_links = set()
    visited_links = set()

    # ensure link is absolute and well-formed
    def make_absolute(href):
        # Correctly join the base URL and href to handle missing slashes or relative paths
        return urljoin(base_url, href)

    # validate URL to prevent adding problematic formats
    def is_valid_url(url):
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme) and bool(parsed.netloc)
        except ValueError:
            return False

    # stop recursion if max depth reached or URL was visited
    def scrape_links(url, current_depth):
        if current_depth > recursion_depth_level or url in visited_links or not is_valid_url(url):
            return
        visited_links.add(url)

        # fetch and parse the page content to find all links on the page
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            href = link.get('href')
            if href and "#" not in href:
                absolute_href = make_absolute(href)
                if "SourceCode=18" in href and is_valid_url(absolute_href):
                    product_links.add(absolute_href)
                elif category_keyword in href and "SourceCode=18" not in href and is_valid_url(absolute_href):
                    scrape_links(absolute_href, current_depth + 1)

        time.sleep(1)  # delay to respect the server

    # begin scraping process
    scrape_links(baseURL, 0)

    return product_links

# CREATE DATABASE OF PRODUCTS: start with a baseURL and end with a database in the correct format to feed into the populate_vectors() function to populate ChromaDB
def create_product_database(baseURL, recursion_depth, client):
    data = []
    urls = get_product_links(baseURL, recursion_depth)

    print("Creating dataset from product links...")

    for url in urls:
        json_obj = url_to_json(url, client)  
        data.append(json.loads(json_obj))
        print("created json")
    
    print("Successfully created dataset from category URL.")
    return data

def main():

    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    catgeory_baseURL = "https://www.partselect.com/Refrigerator-Parts.htm"  # indicate your product category's baseURL
    vec_store_name = "PartSelect"  # specify the name of the ChromaDB collection you'd like to create or add to

    vector_store = VectorStore(vec_store_name)
    data = create_product_database(catgeory_baseURL, 0, client)
    vector_store.populate_vectors(data)
    print("ChromaDB has been successfully populated with your new data.")

if __name__ == "__main__":
    main()