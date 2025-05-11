import requests
from bs4 import BeautifulSoup
import re

class FlipkartParser:
    @staticmethod
    def clean_price(price_tag):
        price = (
            int(re.sub(r'[^\d]', '', price_tag.get_text()))
            if price_tag else None
        )
        return price

    @staticmethod
    def clean_review_rating_count(review_text):
        match = re.search(r'([\d,]+)\s+Ratings.*?([\d,]+)\s+Reviews', review_text)
        total_ratings = total_reviews = -1
        if match:
            total_ratings = int(match.group(1).replace(',', ''))
            total_reviews = int(match.group(2).replace(',', ''))
        return [total_reviews, total_ratings]

    def parse(self, soup: BeautifulSoup):
        product_blocks = soup.select('div._75nlfW')
        print(f"Total containers found: {len(product_blocks)}")
        parsed_items = []

        for block in product_blocks:
            product_link_tag = block.select_one('a[href*="pid"]')
            if not product_link_tag:
                continue

            relative_link = product_link_tag['href']
            product_url = f"https://www.flipkart.com{relative_link}"

            seller = self.get_seller_name(product_url)

            title_tag = block.select_one('div.KzDlHZ') or block.select_one('a.s1Q9rs')
            price_tag = block.select_one('div.Nx9bqj._4b5DiR')
            rating_tag = block.select_one('div.XQDdHH')
            review_summary_tag = block.select_one('span.Wphh3N')

            # Clean values
            price = FlipkartParser.clean_price(price_tag=price_tag)

            total_ratings = None
            total_reviews = None

            if review_summary_tag:
                review_text = review_summary_tag.get_text()
                total_reviews,total_ratings = self.clean_review_rating_count(review_text)

            parsed_items.append({
                'title': title_tag.get_text(strip=True) if title_tag else 'N/A',
                'price': price,
                'rating': rating_tag.get_text(strip=True) if rating_tag else -1,
                'total_ratings': total_ratings,
                'total_reviews': total_reviews,
                'seller': seller,
                'product_link': product_url
            })

        return parsed_items

    @staticmethod
    def get_seller_name(product_url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            resp = requests.get(product_url, headers=headers)
            if resp.status_code == 200:
                product_soup = BeautifulSoup(resp.content, 'html.parser')
                seller_tag = product_soup.find('div', {'id': 'sellerName'})
                print(product_url,seller_tag)
                return seller_tag.get_text(strip=True) if seller_tag else 'N/A'
        except Exception as e:
            print("Error fetching seller:", e)
        return 'N/A'

    def parse_product_page(self, product_soup: BeautifulSoup):
        price_tag = product_soup.find('div', {'class': 'Nx9bqj CxhGGd'})
        price = FlipkartParser.clean_price(price_tag)
        rating_tag = product_soup.find('div', {'class': 'XQDdHH'})
        rating = rating_tag.get_text(strip=True)
        reviews_tag = product_soup.find('span', {'class': 'Wphh3N'})
        total_reviews, total_ratings = FlipkartParser.clean_review_rating_count(reviews_tag.get_text())
        return {'price': price, 'rating': rating, 'total_reviews': total_reviews, 'total_rating': total_ratings}

#
# def scrape_flipkart(keyword):
#     headers = {'User-Agent': 'Mozilla/5.0'}
#     url = f"https://www.flipkart.com/search?q={keyword}"
#     response = requests.get(url, headers=headers)
#     if response.status_code != 200:
#         print("Failed to fetch search results.")
#         return []
#
#     soup = BeautifulSoup(response.content, 'html.parser')
#     parser = FlipkartParser()
#     return parser.parse(soup)
#
# if __name__ == "__main__":
#     keyword = input("Enter a product keyword to search: ")
#     products = scrape_flipkart(keyword)
#     for i, product in enumerate(products, start=1):
#         print(f"{i}. {product}")
