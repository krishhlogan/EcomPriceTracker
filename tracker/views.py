from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Watchlist, SearchQueue
from .serializers import ProductSerializer, WatchlistSerializer

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
        # Filter by username
        username = self.request.query_params.get('username')
        if username:
            return Watchlist.objects.filter(username=username)
        return Watchlist.objects.all()

    def perform_create(self, serializer):
        # Create watchlist entry with the provided username
        username = self.request.data.get('username')
        if not username:
            raise ValueError("Username is required for creating a watchlist entry.")
        serializer.save(username=username)
