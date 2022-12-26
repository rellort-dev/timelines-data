
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SCRAPER_URL = os.environ["SCRAPER_URL"]
NUM_ARTICLES_PER_SCRAPE = int(os.environ.get("NUM_ARTICLES_PER_SCRAPE", 50))

MEILISEARCH_URL = os.environ.get("MEILISEARCH_URL", "http://localhost:7700")
MEILISEARCH_KEY = os.environ.get("MEILISEARCH_KEY", "masterKey")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")

RABBITMQ_EXCHANGE_NAME = "articles"
RABBITMQ_EMBEDDER_QUEUE_NAME = "articles_to_embed"
RABBITMQ_EMBEDDER_BINDING_KEY = "embedder"
RABBITMQ_STORER_QUEUE_NAME = "articles_to_store"
RABBITMQ_STORER_BINDING_KEY = "storer"

SENTRY_DSN = os.environ["SENTRY_DSN"]

def get_logging_prefix(type: str, source: str):
    if type == "scrape":
        if not source:
            raise Exception("Logging prefix for scrape.py must include a source.")
        return f"[scrape.py {source} | {datetime.now()}]"
    elif type == "embed":
        return f"[embed.py | {datetime.now()}]"
    elif type == "store_to_db":
        return f"[store_to_db.py | {datetime.now()}]"
    else:
        raise Exception("Valid types: scrape, embed, store_to_db")
