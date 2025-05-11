from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
from .models import Watchlist, SearchQueue, Product
from .services.scraper import ScraperEngine
from .services.product_service import ProductService
from .services.html_parser import FlipkartParser


def get_scraper():
    return ScraperEngine(parser=FlipkartParser(), product_service=ProductService())


@shared_task
def scrape_watchlisted_products():
    engine = get_scraper()
    product_ids = Watchlist.objects.values_list('product_id', flat=True).distinct()
    products = Product.objects.filter(id__in=product_ids)

    for product in products:
        if product.product_link:
            print(f"Scraping watchlisted product: {product.title}")
            engine.scrape_product_url(product.product_link)


@shared_task
def scrape_popular_products():
    engine = get_scraper()
    products = Product.objects.all()

    for product in products:
        if should_scrape(product):
            print(f"Scraping popular product: {product.title}")
            if product.product_link:
                engine.scrape_product_url(product.product_link)
            else:
                engine.scrape(product.title)  # fallback


@shared_task
def scrape_search_queue():
    engine = get_scraper()
    queue_items = SearchQueue.objects.filter(is_scraped=False)

    for item in queue_items:
        print(f"Scraping search queue keyword: {item.keyword}")
        engine.scrape(item.keyword)
        item.is_scraped = True
        item.save()


@shared_task
def increment_search_count(product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.search_count += 1
        product.save()
    except Product.DoesNotExist:
        print(f'Product does not exist in db: {product_id}')


def should_scrape(product):
    if product.search_count >= 50:
        return (now() - product.last_scraped) > timedelta(hours=1)
    elif product.search_count >= 10:
        return (now() - product.last_scraped) > timedelta(hours=6)
    else:
        return (now() - product.last_scraped) > timedelta(days=1)
