
import os

SCRAPER_URL = os.environ["SCRAPER_URL"]

MEILISEARCH_URL = os.environ.get("MEILISEARCH_URL", "http://localhost:7700")
MEILISEARCH_KEY = os.environ.get("MEILISEARCH_KEY", "masterKey")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")

RABBITMQ_EXCHANGE_NAME = "articles"
RABBITMQ_EMBEDDER_QUEUE_NAME = "articles_to_embed"
RABBITMQ_EMBEDDER_BINDING_KEY = "embedder"
RABBITMQ_STORER_QUEUE_NAME = "articles_to_store"
RABBITMQ_STORER_BINDING_KEY = "storer"
