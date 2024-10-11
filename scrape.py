import requests
from bs4 import BeautifulSoup

url = 'https://maximum.md/ro/telefoane-si-gadgeturi/telefoane-si-comunicatii/smartphoneuri/'


response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='js-content product__item')

    print("\nExtracting product data:\n")
    product_list = []

    for product in products[:5]:
        name_tag = product.find('div', class_='product__item__title')
        name = name_tag.get_text(strip=True) if name_tag else "No name"

        price_tag = product.find('div', class_='product__item__price-current')
        price_text = price_tag.get_text(strip=True) if price_tag else "Price not found"

        try:
            price_mdl = int(price_text.replace(',', '').replace(' ', '').replace('lei', ''))
        except ValueError:
            price_mdl = 0

        link_tag = product.find('a', href=True)
        product_link = 'https://maximum.md' + link_tag['href'] if link_tag else "Link not found"

        if name and price_mdl and product_link and 100 <= price_mdl <= 100000:
            print(f"Product Name: {name}")
            print(f"Price: {price_mdl} MDL")
            print(f"Product Link: {product_link}")

            product_response = requests.get(product_link)
            if product_response.status_code == 200:
                product_soup = BeautifulSoup(product_response.text, 'html.parser')

                feature_list = product_soup.find('ul', class_='feature-list')
                features = {}
                if feature_list:
                    for item in feature_list.find_all('li', class_='feature-list-item'):
                        key_tag = item.find('span', class_='feature-list-item_left')
                        value_tag = item.find('span', class_='feature-list-item_right')

                        if key_tag and value_tag:
                            key = key_tag.get_text(strip=True)
                            value = value_tag.get_text(strip=True)
                            features[key] = value

                    print("\nExtracted Features:")
                    for key, value in features.items():
                        print(f"{key}: {value}")
                else:
                    print("Feature list not found on the product page.")

                product_list.append({
                    'name': name,
                    'price': price_mdl,
                    'link': product_link,
                    'features': features
                })
            else:
                print(f"Failed to retrieve details from {product_link}")

        else:
            print(f"Skipped product: {name}, Price: {price_mdl}, Link: {product_link}")

        print(f"\n===============\n")

else:
    print(f"Failed to retrieve the listing page. Status Code: {response.status_code}")
