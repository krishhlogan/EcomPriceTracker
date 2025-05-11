import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_price_tracker.settings')
app = Celery('ecom_price_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'scrape_watchlist_every_2_hours': {
        'task': 'tracker.tasks.scrape_watchlisted_products',
        'schedule': crontab(minute=0, hour='*/2'),
    },
    'scrape_popular_products_every_3_hours': {
        'task': 'tracker.tasks.scrape_popular_products',
        'schedule': crontab(minute=30, hour='*/3'),
    },
    'scrape_search_queue_every_hour': {
        'task': 'tracker.tasks.scrape_search_queue',
        'schedule': crontab(minute=0, hour='*'),
    },
}