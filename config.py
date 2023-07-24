
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SCRAPER_URL = os.environ["SCRAPER_URL"]
SCRAPER_SOURCES_URL = SCRAPER_URL + "/sources"
SCRAPER_LINKS_URL = SCRAPER_URL + "/links"
SCRAPER_ARTICLE_URL = SCRAPER_URL + "/article"

MEILISEARCH_URL = os.environ.get("MEILISEARCH_URL", "http://localhost:7700")
MEILISEARCH_KEY = os.environ.get("MEILISEARCH_KEY", "")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")

RABBITMQ_EXCHANGE_NAME = "articles"
RABBITMQ_TRANSFORM_QUEUE_NAME = "transform"
RABBITMQ_TRANSFORMER_BINDING_KEY = "transformer"
RABBITMQ_LOAD_QUEUE_NAME = "load"
RABBITMQ_STORER_BINDING_KEY = "loader"

DIGITALOCEAN_ACCESS_TOKEN = os.environ["DIGITALOCEAN_ACCESS_TOKEN"]
DIGITALOCEAN_MEILISEARCH_DROPLET_ID = os.environ["DIGITALOCEAN_MEILISEARCH_DROPLET_ID"]

SENTRY_DSN = os.environ["SENTRY_DSN"]

def get_logging_prefix(type: str, source: str):
    if type == "extract":
        if not source:
            raise Exception("Logging prefix for extract.py must include a source.")
        return f"[extract.py {source} | {datetime.now()}]"
    elif type == "transform":
        return f"[transform.py | {datetime.now()}]"
    elif type == "load":
        return f"[load.py | {datetime.now()}]"
    else:
        raise Exception("Valid types: scrape, transform, load")
