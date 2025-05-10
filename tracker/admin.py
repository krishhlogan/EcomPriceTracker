from django.contrib import admin
from .models import Product, PriceHistory, Watchlist, SearchQueue

# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'rating', 'num_reviews', 'last_scraped')
    search_fields = ('title', 'seller')
    list_filter = ('last_scraped',)

# Register PriceHistory model
@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('product__title',)

# Register Watchlist model
@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('username', 'product', 'desired_price', 'notify_on_drop')
    search_fields = ('username', 'product__title')
    list_filter = ('notify_on_drop',)

# Register SearchQueue model
@admin.register(SearchQueue)
class SearchQueueAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'is_scraped', 'created_at')
    list_filter = ('is_scraped',)
    search_fields = ('keyword',)
