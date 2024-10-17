import requests
from bs4 import BeautifulSoup
from functools import reduce


url = 'https://maximum.md/ro/telefoane-si-gadgeturi/telefoane-si-comunicatii/smartphoneuri/'


response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='js-content product__item')

    #print("\nExtracting product data:\n")
    product_list = []

    for product in products[:5]:
        name_tag = product.find('div', class_='product__item__title')
        name = name_tag.get_text(strip=True) if name_tag else "No name"

        price_tag = product.find('div', class_='product__item__price-current')
        price_text = price_tag.get_text(strip=True) if price_tag else "Price not found"

        try:
            price_mdl = int(price_text.replace('lei', ''))
        except ValueError:
            price_mdl = 0

        link_tag = product.find('a', href=True)
        product_link = 'https://maximum.md' + link_tag['href'] if link_tag else "Link not found"


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

            else:
                print("Feature list not found on the product page.")

            product_list.append({
                'name': name,
                'price': price_mdl,
                'link': product_link,
                'features': features
            })

            filtered_products = list(filter(lambda x: 10000 <= x['price'] <= 20000, product_list))

            eur_conversion_rate = 0.052
            products_in_eur = list(
                map(lambda x: {**x, 'price_eur': round(x['price'] * eur_conversion_rate, 2)}, filtered_products))

            prices_in_eur = [i['price_eur'] for i in products_in_eur]
            total_price_eur = reduce(lambda x, y: x + y, prices_in_eur)

        else:
            print(f"Failed to retrieve details from {product_link}")

else:
    print(f"Failed to retrieve the listing page. Status Code: {response.status_code}")

print("\nFiltered Products:")
for product in products_in_eur:
    print(f"Name: {product['name']}\nPrice: {product['price']} MDL\nPrice in EUR: {product['price_eur']}")
    for key, value in product['features'].items():
        print(f"{key}: {value}")
    print("\n=====================\n")

print(f"\nTotal Price of Filtered Products in EUR: {total_price_eur}")