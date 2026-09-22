import pandas as pd
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# CONFIGURE LOGGING
logging.basicConfig(
    filename="details.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Function to start Selenium
def start_driver():

    # Start Chrome browser
    driver = webdriver.Chrome()

    return driver


# Function to scrape details from one product
def scrape_product(driver, url):

    # Wait up to 10 seconds for elements to appear
    wait = WebDriverWait(driver, 10)

    # Open the product URL
    driver.get(url)

    # Create a dictionary to store this product's data
    product_data = {
        "url": url,
        "product_name": "",
        "sku": "",
        "upc": "",
        "features": "",
        "image": "",
        "specifications": ""
    }

    # Product name
    try:
        product_name = wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "h1")
            )
        ).text

        product_data["product_name"] = product_name

    except Exception as e:
        logger.error(
            "Error getting product name from %s: %s",
            url,
            e
        )


    # SKU
    try:
        sku = driver.find_element(
            By.CLASS_NAME,
            "js-product-sku"
        ).text

        product_data["sku"] = sku

    except Exception as e:
        logger.warning(
            "SKU not found for %s",
            url
        )


    # UPC
    try:
        upc = driver.find_element(
            By.CLASS_NAME,
            "js-product-upc"
        ).text

        product_data["upc"] = upc

    except Exception as e:
        logger.warning(
            "UPC not found for %s",
            url
        )


    # Features
    try:
        feature_element = driver.find_element(
            By.ID,
            "pdp-features"
        )

        feature_text = feature_element.text

        product_data["features"] = feature_text

    except Exception as e:
        logger.warning(
            "Features not found for %s",
            url
        )


    # Product image
    try:
        image = driver.find_element(
            By.CSS_SELECTOR,
            "img.plmr-c-product-info__image.js-product-img--default"
        ).get_attribute("src")

        product_data["image"] = image

    except Exception as e:
        logger.warning(
            "Image not found for %s",
            url
        )


    # Specifications
    try:
        specification_element = driver.find_element(
            By.CSS_SELECTOR,
            ".plmr-c-additional-product-specs"
        )

        specification_text = specification_element.text

        product_data["specifications"] = specification_text

    except Exception as e:
        logger.warning(
            "Specifications not found for %s",
            url
        )


    # Return all scraped information for this product
    return product_data


# Function to read product URLs from CSV
def get_urls():

    # Read the CSV file
    df = pd.read_csv("product_urls.csv")

    # Get the URLs column as a list
    urls = df["urls"].tolist()

    # Log the number of URLs
    logger.info(
        "Total product URLs loaded: %s",
        len(urls)
    )

    return urls


# Function to save scraped data to CSV
def save_data(scraped_data):

    # Create a DataFrame from the scraped data
    details_df = pd.DataFrame(scraped_data)

    # Save the data to CSV
    details_df.to_csv(
        "details.csv",
        index=False
    )

    # Log completion
    logger.info(
        "Details saved successfully. Total products: %s",
        len(details_df)
    )


# Main function
def main():

    # Get all product URLs from CSV
    urls = get_urls()

    # Start Selenium
    driver = start_driver()

    # Create a list to store scraped product data
    scraped_data = []

    # Scrape each product
    for url in urls:

        try:

            logger.info(
                "Opening URL: %s",
                url
            )

            # Scrape the current product
            product_data = scrape_product(
                driver,
                url
            )

            # Add the product data to the main list
            scraped_data.append(product_data)

            logger.info(
                "Product scraped successfully: %s",
                url
            )

        except Exception as e:

            logger.error(
                "Failed to scrape %s: %s",
                url,
                e
            )

            # Keep the failed URL in the final CSV
            scraped_data.append({
                "url": url,
                "product_name": "",
                "sku": "",
                "upc": "",
                "features": "",
                "image": "",
                "specifications": ""
            })


    # Close Selenium after scraping all products
    driver.quit()

    # Save all scraped data
    save_data(scraped_data)


# Run the main function
if __name__ == "__main__":
    main()