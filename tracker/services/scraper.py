import requests
from bs4 import BeautifulSoup

class ScraperEngine:
    def __init__(self, parser, product_service):
        self.parser = parser
        self.product_service = product_service

    def scrape(self, keyword):
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = 1
        while True:
            url = f"https://www.flipkart.com/search?q={keyword}&page={page}"
            response = requests.get(url, headers=headers)
            print('Response from fk',response.status_code)
            if response.status_code != 200:
                break
            soup = BeautifulSoup(response.content, 'html.parser')
            products = self.parser.parse(soup)
            if not products:
                break
            for product in products:
                self.product_service.save_product(product)
            page += 1
            if page == 3:
                break
