
import json
import pika
import sentry_sdk
import sys
from dateutil import parser
from meilisearch import Client 

import config
from scrape import get_sources, scrape_article, scrape_links, is_duplicate, get_latest_published_time


OFFSET_INCREMENT = 10

# NOTE: limit must be in multiples of 10
def get_links_of_new_articles(source, client, limit=50):
    if limit > 100:
        raise ValueError("Scraper is limited to a maximum of 100 links")
    
    result = []
    offset = 0
    failed_offsets = []

    while len(result) <= limit:
        try:
            links = scrape_links(source, offset)
            if is_duplicate(links[-1], client) or len(result) + 10 > limit:
                break
            result += links
        except Exception as e:
            print(f"Scraping links from source={source} and offset={offset} raised an exception:")
            print(e)
            failed_offsets.append(str(offset))
        offset += OFFSET_INCREMENT
    
    if failed_offsets:
        print(f"Some requests to the link scraper failed. Failed offsets: {', '.join(failed_offsets)}")
   
    for link in links:
        if is_duplicate(link, client) or limit <= len(result):
            break
        result.append(link)

    return result

def main(source):
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        traces_sample_rate=1.0
    )
    
    supported_sources = get_sources()
    if source not in supported_sources:
        raise Exception("Please provide a correct source as a system argument! Supported sources: " + ", ".join(supported_sources))
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=config.RABBITMQ_EXCHANGE_NAME, exchange_type="direct")
    channel.queue_declare(queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=config.RABBITMQ_EXCHANGE_NAME, 
                       queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, 
                       routing_key=config.RABBITMQ_EMBEDDER_BINDING_KEY)

    client = Client(config.MEILISEARCH_URL, config.MEILISEARCH_KEY)
    latest_published_time = get_latest_published_time(source, client)
    
    offset = 0
    num_failures = 0
    while offset < config.NUM_ARTICLES_PER_SCRAPE:
        links = scrape_links(source, offset)
        for link in links:
            try:
                article = scrape_article(source, link)
            except Exception as e:
                print(f"Scraping {link} raised an exception: ")
                print(e)
                num_failures = 0
                continue

            iso_time = article["publishedTime"]
            unix_timestamp = int(parser.parse(iso_time).timestamp())
            article["publishedTime"] = unix_timestamp
            article["source"] = source
            
            if article["publishedTime"] < latest_published_time:
                print(f"Scraped a total of {offset} articles! (minus the failures)")
                return
            
            channel.basic_publish(
                exchange=config.RABBITMQ_EXCHANGE_NAME, 
                routing_key=config.RABBITMQ_EMBEDDER_BINDING_KEY, 
                body=json.dumps(article),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            print(f"Scraped {link}!")
        offset += 10
    print(f"source={source}, attempted to scrape {offset} links, "
          + f"{offset - num_failures} successes {num_failures} failures")

    connection.close()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        source = sys.argv[1]
        main(source)
    else:
        raise Exception("Usage: python -m rabbitmq.scrape <source>")
