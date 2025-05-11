from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Product, Watchlist, SearchQueue, PriceHistory
from .serializers import ProductSerializer, WatchlistSerializer, PriceHistorySerializer
from tracker.tasks import increment_search_count  # Import the task


class ProductPagination(PageNumberPagination):
    page_size = 10  # Set the number of results per page
    page_size_query_param = 'page_size'
    max_page_size = 100

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
        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(matching_products, request)

        if paginated_products:
            for product in matching_products:
                increment_search_count.apply_async(args=[product.id])
            if paginated_products:
                serializer = self.get_serializer(paginated_products, many=True)
                return paginator.get_paginated_response(serializer.data)

        # If no products found, queue the search term for future scraping
        # Create or update the search queue for the keyword
        search_queue, created = SearchQueue.objects.get_or_create(keyword=keyword, is_scraped=False)
        if created:
            message = f"'{keyword}' not found. We will notify you once it's available."
        else:
            message = f"'{keyword}' is already queued for scraping."

        return Response({"message": message})

    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        try:
            product = self.get_object()
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

        history = PriceHistory.objects.filter(product=product).order_by('-timestamp')
        serializer = PriceHistorySerializer(history, many=True)
        return Response(serializer.data)

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
            Response(
                {"error": "Username, product, and desired price are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent duplicate entry
        if Watchlist.objects.filter(username=username, product_id=product).exists():
            Response(
                {"error": "This product is already in the watchlist for this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(username=username)
        return Response(
            {"message": "Product added to watchlist.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
