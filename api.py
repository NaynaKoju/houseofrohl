import requests
import pandas as pd
import logging
import json


# configuring logging
logging.basicConfig(
    filename="api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Function to get products from a specific API page
def get_products(page):

    # API URL
    url = "https://cuuo4s.a.searchspring.io/api/search/search.json"

    # Parameters required by the API
    params = {
        "ajaxCatalog": "v3",
        "resultsFormat": "native",
        "siteId": "cuuo4s",
        "filter.categories_hierarchy": "Kitchen>Faucets",
        "q": "",
        "page": page,
        "bgfilter.discontinued": "NO"
    }

    # Send GET request to the API
    response = requests.get(url, params=params)

    # Check if the request was successful
    response.raise_for_status()

    # Log successful request
    logger.info("Page %s collected successfully", page)

    # Convert the JSON response into a Python dictionary
    data = response.json()

    # Get the list of products from the response
    products = data["results"]

    # Get pagination information
    pagination = data["pagination"]

    # Return products and pagination information
    return products, pagination


# Get the first page and pagination information
products, pagination = get_products(1)

# Get the total number of pages from the API
total_pages = pagination["totalPages"]

# Store products from the first page
all_products = products


# Go through every remaining page
for page in range(2, total_pages + 1):

    # Get the products from the current page
    products, pagination = get_products(page)

    # Add the products from the current page to the main list
    all_products.extend(products)


# Check how many products we collected
logger.info("Total products collected: %s", len(all_products))


# Create a DataFrame from all API products
df = pd.json_normalize(all_products)


# Store the variant information
json_data = []


# Go through the JSON data of every product
for product_json in df["json"]:

    # Replace HTML encoded quotation marks
    product_json = product_json.replace("&quot;", '"')

    # Convert the JSON string into a Python list
    variant_data = json.loads(product_json)

    # Add the variants to the list
    json_data.extend(variant_data)


# Convert the variant data into a DataFrame
normalized_df = pd.json_normalize(json_data)


# Add the website domain to the relative variant URLs
normalized_df["urls"] = (
    "https://houseofrohl.com" + normalized_df["product_url"]
)


# Check how many variant URLs we collected
logger.info(
    "Total variant URLs collected: %s",
    len(normalized_df)
)


# Save the variant URLs to CSV
normalized_df["urls"].to_csv(
    "product_urls.csv",
    index=False
)


# Log completion
logger.info("URLs saved to product_urls.csv")