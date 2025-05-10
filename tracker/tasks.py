from celery import shared_task
from .models import Watchlist, SearchQueue
from .services.scraper import ScraperEngine
from .services.product_service import ProductService
from .services.html_parser import FlipkartParser

@shared_task
def scheduled_scrape():
    keywords = list(Watchlist.objects.values_list('product__title', flat=True))
    queued_keywords = list(SearchQueue.objects.filter(is_scraped=False).values_list('keyword', flat=True))

    engine = ScraperEngine(parser=FlipkartParser(), product_service=ProductService())

    for keyword in set(keywords + queued_keywords):
        engine.scrape(keyword)
        SearchQueue.objects.filter(keyword=keyword).update(is_scraped=True)
