from bs4 import BeautifulSoup
from .interfaces import IHTMLParser

class FlipkartParser(IHTMLParser):
    def parse(self, soup):
        items = soup.select('._1AtVbE')
        parsed_items = []

        for item in items:
            title_tag = item.select_one('._4rR01T')
            price_tag = item.select_one('._30jeq3')
            rating_tag = item.select_one('._3LWZlK')
            reviews_tag = item.select_one('span._2_R_DZ span span')
            seller_tag = item.select_one('._1xb2I5')

            if not title_tag or not price_tag:
                continue

            parsed_items.append({
                'title': title_tag.text.strip(),
                'price': float(price_tag.text.strip().replace('₹', '').replace(',', '')),
                'rating': float(rating_tag.text.strip()) if rating_tag else None,
                'num_reviews': int(reviews_tag.text.split()[0].replace(',', '')) if reviews_tag else None,
                'seller': seller_tag.text.strip() if seller_tag else "Flipkart"
            })
        print('Parsed items',parsed_items)
        return parsed_items
