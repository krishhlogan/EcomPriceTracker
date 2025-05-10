from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=255, unique=True)
    seller = models.CharField(max_length=255, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    num_reviews = models.IntegerField(null=True, blank=True)
    last_scraped = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - Rs.{self.price} on {self.timestamp}"

class Watchlist(models.Model):
    username = models.CharField(max_length=255)  # Storing username directly
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    desired_price = models.DecimalField(max_digits=10, decimal_places=2)
    notify_on_drop = models.BooleanField(default=True)

    class Meta:
        unique_together = ('username', 'product')  # Ensure one product per user

class SearchQueue(models.Model):
    keyword = models.CharField(max_length=255, unique=True)
    is_scraped = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
