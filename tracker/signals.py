# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SearchQueue
from tracker.tasks import scrape_search_queue

@receiver(post_save, sender=SearchQueue)
def trigger_scrape_on_add(sender, instance, created, **kwargs):
    print('Signal received',sender,instance,created)
    if created:
        scrape_search_queue.delay()  # Call the Celery task asynchronously
