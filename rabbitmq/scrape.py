
import json
import config
import pika
import sys
from meilisearch import Client 
from scrape import get_sources, scrape_links, scrape_articles, is_duplicate


OFFSET_INCREMENT = 10

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
    supported_sources = get_sources()
    if source not in supported_sources:
        raise Exception("Please provide a correct source as a system argument! Supported sources: " + ", ".join(supported_sources))
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=config.RABBITMQ_EXCHANGE_NAME, exchange_type="direct")
    channel.queue_declare(queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=config.RABBITMQ_EXCHANGE_NAME, 
                       queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, 
                       routing_key=config.RABBITMQ_EMBEDDER_BINDING_KEY)
    # NOTE: Is it necessary to declare & bind the exchange and queue in both sending and receiving scripts?

    client = Client(config.MEILISEARCH_URL, config.MEILISEARCH_KEY)

    links = get_links_of_new_articles(source, client, config.NUM_ARTICLES_PER_SCRAPE)
    articles = scrape_articles(source, links)

    print(f"Sending {len(articles)} articles...")
    channel.basic_publish(
        exchange=config.RABBITMQ_EXCHANGE_NAME, 
        routing_key=config.RABBITMQ_EMBEDDER_BINDING_KEY, 
        body=json.dumps(articles),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )
    print("Articles sent")

    connection.close()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        source = sys.argv[1]
        main(source)
    else:
        raise Exception("Usage: python -m rabbitmq.scrape <source>")
