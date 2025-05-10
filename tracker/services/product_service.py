from ..models import Product, PriceHistory
from .interfaces import IProductService

class ProductService(IProductService):
    def save_product(self, data):
        product, created = Product.objects.get_or_create(title=data['title'], defaults={
            'rating': data['rating'],
            'num_reviews': data['num_reviews'],
            'seller': data['seller']
        })
        if not created:
            product.rating = data['rating']
            product.num_reviews = data['num_reviews']
            product.seller = data['seller']
            product.save()
        PriceHistory.objects.create(product=product, price=data['price'])
        print('Added new product: ', data['title'])
