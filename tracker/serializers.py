from rest_framework import serializers
from .models import Product, PriceHistory, Watchlist

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'timestamp']

class ProductSerializer(serializers.ModelSerializer):
    price_history = PriceHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'seller', 'rating', 'num_reviews', 'price_history', 'num_ratings', 'product_link']

class WatchlistSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()
    class Meta:
        model = Watchlist
        fields = ['id', 'username', 'product', 'product_details' ,'desired_price', 'notify_on_drop']

    def get_product_details(self, obj):
        product = obj.product
        latest_price_entry = PriceHistory.objects.filter(product=product).order_by('-timestamp').first()
        latest_price = latest_price_entry.price if latest_price_entry else None
        return {
            'id': product.id,
            'title': product.title,
            'price': latest_price,
            'product_link': product.product_link
        }
