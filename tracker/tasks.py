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
    print('Running scrape watchlisted products')
    engine = get_scraper()

    watchlisted = Watchlist.objects.select_related('product').all()

    for item in watchlisted:
        print('item',item)
        product = item.product

        if product.product_link:
            print(f"Scraping watchlisted product: {product.title}")
            product_info = engine.scrape_from_url(product.product_link)

            # Notify if price is below target
            scraped_price = product_info.get("price")
            scraped_price = 25000.00
            if scraped_price is not None and item.desired_price is not None:
                if scraped_price <= item.desired_price:
                    print(f"🔔 ALERT: {product.title} has dropped to ₹{scraped_price}, "
                          f"which is below your target ₹{item.desired_price}")

            # Update the product in DB
            engine.product_service.update_product(product_info, product)


@shared_task
def scrape_popular_products():
    print('Scrape popular products')
    engine = get_scraper()
    products = Product.objects.all()

    for product in products:
        if should_scrape(product):
            print(f"Scraping popular product: {product.title}")
            if product.product_link:
                product_info =  engine.scrape_from_url(product.product_link)
                engine.product_service.update_product(product_info, product)
            else:
                engine.scrape(product.title)  # fallback


@shared_task
def scrape_search_queue():
    print('Scraping search queue')
    engine = get_scraper()
    queue_items = SearchQueue.objects.filter(is_scraped=False)

    for item in queue_items:
        print(f"Scraping search queue keyword: {item.keyword}")
        engine.scrape(item.keyword)
        item.is_scraped = True
        item.save()


@shared_task
def increment_search_count(product_id):
    print('Incrementing search count')
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
