import requests
from bs4 import BeautifulSoup

url = 'https://maximum.md/ro/telefoane-si-gadgeturi/telefoane-si-comunicatii/smartphoneuri/'


response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='js-content product__item')

    print("\nExtracting product data:\n")
    product_list = []

    for product in products:
        name_tag = product.find('div', class_='product__item__title')
        name = name_tag.get_text(strip=True) if name_tag else "No name"

        price_tag = product.find('div', class_='product__item__price-current')
        price_text = price_tag.get_text(strip=True) if price_tag else "Price not found"

        print(f"Product Name: {name}")
        print(f"Price: {price_text} MDL")
        print(f"\n=============\n")