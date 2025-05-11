from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Product, Watchlist, SearchQueue
from .serializers import ProductSerializer, WatchlistSerializer
from tracker.tasks import increment_search_count  # Import the task


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Search for a product by keyword
    @action(detail=False, methods=['get'])
    def search_or_queue(self, request):
        keyword = request.query_params.get('q')
        if not keyword:
            return Response({"error": "Missing search keyword."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the product already exists for the given keyword
        matching_products = Product.objects.filter(title__icontains=keyword)
        if matching_products.exists():
            for product in matching_products:
                increment_search_count.apply_async(args=[product.id])
            serializer = self.get_serializer(matching_products, many=True)
            return Response(serializer.data)

        # If no products found, queue the search term for future scraping
        # Create or update the search queue for the keyword
        search_queue, created = SearchQueue.objects.get_or_create(keyword=keyword, is_scraped=False)
        if created:
            message = f"'{keyword}' not found. We will notify you once it's available."
        else:
            message = f"'{keyword}' is already queued for scraping."

        return Response({"message": message})

class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username')
        if username:
            return Watchlist.objects.filter(username=username)
        return Watchlist.objects.all()

    def perform_create(self, serializer):
        username = self.request.data.get('username')
        product = self.request.data.get('product')
        desired_price = self.request.data.get('desired_price')

        if not username or not product or not desired_price:
            raise ValidationError("Username, product, and desired price are required.")

        # Prevent duplicate entry
        if Watchlist.objects.filter(username=username, product_id=product).exists():
            raise ValidationError("This product is already in the watchlist for this user.")

        serializer.save(username=username)
