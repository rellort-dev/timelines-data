
import json
import pika
import sentry_sdk
import sys
from datetime import datetime
from dateutil import parser

import config
from scrape import get_sources, scrape_article, scrape_links


def log_results(source: str, num_new_articles: int, num_failures: int) -> None:
    if num_new_articles < 0 or num_failures < 0:
        raise ValueError("num_new_articles and num_failures cannot be smaller than 0")
    if num_failures > num_new_articles:
        raise ValueError("num_failures cannot be larger than num_new_articles")
    
    logging_prefix = config.get_logging_prefix("scrape", source)
    num_successes = num_new_articles - num_failures

    print(
        f"{logging_prefix} {num_new_articles} new articles, "
        + f"{num_successes} successes, {num_failures} failures"
    )

def main(source):
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        traces_sample_rate=1.0
    )
    
    supported_sources = get_sources()
    if source not in supported_sources:
        logging_prefix = config.get_logging_prefix("scrape", source)
        supported_sources_str = ", ".join(supported_sources)
        raise Exception(
            f"{logging_prefix} An incorrect source was provided. "
            + f"Supported sources: {supported_sources_str}"
        )
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=config.RABBITMQ_EXCHANGE_NAME, exchange_type="direct")
    channel.queue_declare(queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=config.RABBITMQ_EXCHANGE_NAME, 
                       queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, 
                       routing_key=config.RABBITMQ_EMBEDDER_BINDING_KEY)

    num_failures = 0
    logging_prefix = f"[scrape.py {source}|{datetime.now()}]"

    links = scrape_links(source)
    for link in links:
        try:
            article = scrape_article(link)
        except Exception as e:
            print(logging_prefix + " " + str(e))
            num_failures += 1
            continue

        iso_time = article["publishedTime"]
        unix_timestamp = int(parser.parse(iso_time).timestamp())
        article["publishedTime"] = unix_timestamp
        article["source"] = source
        
        channel.basic_publish(
            exchange=config.RABBITMQ_EXCHANGE_NAME, 
            routing_key=config.RABBITMQ_EMBEDDER_BINDING_KEY, 
            body=json.dumps(article),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

    num_new_articles = len(links)
    log_results(source, num_new_articles, num_failures)
    connection.close()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        source = sys.argv[1]
        main(source)
    else:
        raise Exception("Usage: python -m rabbitmq.scrape <source>")
