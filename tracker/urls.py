from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, WatchlistViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')  # Add the basename here

urlpatterns = [
    path('', include(router.urls)),
    path('search/', ProductViewSet.as_view({'get': 'search_or_queue'})),
]
