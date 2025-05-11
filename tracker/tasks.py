from celery import shared_task
from .models import Watchlist, SearchQueue, Product
from .services.scraper import ScraperEngine
from .services.product_service import ProductService
from .services.html_parser import FlipkartParser

@shared_task
def scheduled_scrape():
    keywords = list(Watchlist.objects.values_list('product__title', flat=True))
    queued_keywords = list(SearchQueue.objects.filter(is_scraped=False).values_list('keyword', flat=True))
    print('Processing keywords',keywords+queued_keywords)
    # print('Keywords to be processed',[word.product.title for word in keywords] + [word.keyword for word in queued_keywords])
    engine = ScraperEngine(parser=FlipkartParser(), product_service=ProductService())

    for keyword in set(keywords + queued_keywords):
        engine.scrape(keyword)
        SearchQueue.objects.filter(keyword=keyword).update(is_scraped=True)

@shared_task
def increment_search_count(product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.search_count += 1
        product.save()
    except Product.DoesNotExist:
        print(f'Product does not exist in db: {product_id}')
        pass  # Handle the case where the product doesn't exist
