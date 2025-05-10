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
        fields = ['id', 'title', 'seller', 'rating', 'num_reviews', 'price_history']

class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ['id', 'username', 'product', 'desired_price', 'notify_on_drop']
