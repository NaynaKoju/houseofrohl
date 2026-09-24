import json
from dbconnect.connector import get_connection

# Function to insert product data into MySQL
def insert_product(product_data):

    # Get database connection
    connection = get_connection()

    # Create cursor
    cursor = connection.cursor()

    query = """
        INSERT INTO products
        (url, product_name, sku, upc, features, image, specifications)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    features = json.dumps(
        product_data["features"]
    )

    values = (
        product_data["url"],
        product_data["product_name"],
        product_data["sku"],
        product_data["upc"],
        features,
        product_data["image"],
        product_data["specifications"]
    )

    cursor.execute(
        query,
        values
    )

    connection.commit()

    cursor.close()
    connection.close()

