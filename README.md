# EcomPriceTracker

🛍️ Project Overview
This project is built around the core idea of enabling users to search for products and track price drops effectively.

🔎 When a user searches for a product:

If a matching product is found, its search count is incremented.

If not found, the keyword is queued in the SearchQueue with an is_scraped=False flag for future scraping.

🕒 A background job (e.g., Celery Beat or cron) periodically processes the search queue, scraping product data from Flipkart and adding new entries to the database.

⭐ Users can also add products to their watchlist, specifying a desired price.

When the product's price drops below the desired threshold, the system triggers a notification (currently logged to the console).

📈 Products are regularly updated based on their search frequency, using a last_scraped_at timestamp to control scraping intervals.


Add below to .env file on root level
```dtd
DEBUG=True
SECRET_KEY='django-insecure-1y14h*h$_ap1uyuut%+h!byb0v$d3hlrdsyac!hm@x$4_zksj9'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
stage='dev'
```

For running celery worker (ignore --pool=solo on non-windows machine)
```commandline
celery -A ecom_price_tracker worker --pool=solo --loglevel=info
```

For running celery beat (for scheduling tasks)
```commandline
celery -A ecom_price_tracker beat --loglevel=info
```

For Running api server

```commandline
python manage.py runserver
```

```markdown
Note:
This need to be replaced with a wsgi server for production deployment

```

Searching an item in db or raising a request to scrap
This api, searches and returns products if they exists, else it queues for scheduled scraping.

```markdown
curl --location 'http://127.0.0.1:8000/api/search/?q=pixel'
```

Watchlist of a user
This api list down the watch list of a user, along with product info and latest price.
```markdown
curl --location 'http://localhost:8000/api/watchlist/?username=krishna123'
```

Add to watchlist
This api, adds products to watchlist, so that it can be scrapped at regular intervals to detect price drop.

```markdown
curl --location 'http://localhost:8000/api/watchlist/' \
--header 'Content-Type: application/json' \
--data '{
    "username": "krishna123",
    "product": 382,
    "desired_price": "3000.00",
    "notify_on_drop": "true"
  }'
```
