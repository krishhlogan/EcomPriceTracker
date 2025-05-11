from ..models import Product, PriceHistory
from .interfaces import IProductService

class ProductService(IProductService):
    def save_product(self, data):
        product, created = Product.objects.get_or_create(title=data['title'], defaults={
            'rating': data['rating'],
            'num_reviews': data['total_reviews'],
            'num_ratings': data['total_ratings'],
            'seller': data['seller'],
            'product_link': data['product_link']
        })
        if not created:
            product.rating = data['rating']
            product.num_reviews = data['total_reviews']
            product.seller = data['seller']
            product.num_ratings= data['total_ratings']
            product.product_link = data['product_link']
            product.save()
        PriceHistory.objects.create(product=product, price=data['price'])
        print('Added new product: ', data['title'])

    def update_product(self, product_info, product: Product):
        price = product_info.get('price')
        total_reviews = product_info.get('total_reviews',-1)
        total_ratings = product_info.get('total_ratings',-1)
        rating = product_info.get('rating',-1)
        product.rating = rating
        product.num_ratings = total_ratings
        product.num_reviews = total_reviews
        product.save()
        print('Successfully update product info')
        if price:
            PriceHistory.objects.create(product=product, price=price)
            print('Successfully added price history')

