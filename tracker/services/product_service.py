from ..models import Product, PriceHistory
from .interfaces import IProductService

class ProductService(IProductService):
    def save_product(self, data):
        product, created = Product.objects.get_or_create(title=data['title'], defaults={
            'rating': data['rating'],
            'num_reviews': data['num_reviews'],
            'num_ratings': data['num_ratings'],
            'seller': data['seller'],
            'product_link': data['product_link']
        })
        if not created:
            product.rating = data['rating']
            product.num_reviews = data['num_reviews']
            product.seller = data['seller']
            product.num_ratings= data['num_ratings']
            product.product_link = data['product_link']
            product.save()
        PriceHistory.objects.create(product=product, price=data['price'])
        print('Added new product: ', data['title'])
