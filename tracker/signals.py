# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SearchQueue
from .tasks import scheduled_scrape

@receiver(post_save, sender=SearchQueue)
def trigger_scrape_on_add(sender, instance, created, **kwargs):
    print('Signal received',sender,instance,created)
    if created:
        scheduled_scrape.delay()  # Call the Celery task asynchronously
