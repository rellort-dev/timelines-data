
import json
import pika
import sentry_sdk
from meilisearch import Client

import config
from scrape import is_duplicate

def callback(ch, method, properties, body):
    client = Client(config.MEILISEARCH_URL, config.MEILISEARCH_KEY)

    article = json.loads(body)
    logging_prefix = config.get_logging_prefix("store_to_db", None)
    if is_duplicate(article, client):
        print(f"{logging_prefix} Duplicate detected: {article['url']}")
        return

    client.index("articles").add_documents(article)

    print(f"{logging_prefix} Article stored: {article['url']}")
    
def main():
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        traces_sample_rate=1.0
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.exchange_declare(exchange=config.RABBITMQ_EXCHANGE_NAME, exchange_type="direct")
    channel.queue_declare(queue=config.RABBITMQ_STORER_QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=config.RABBITMQ_EXCHANGE_NAME, 
                       queue=config.RABBITMQ_STORER_QUEUE_NAME, 
                       routing_key=config.RABBITMQ_STORER_BINDING_KEY)
    
    channel.basic_consume(
        queue=config.RABBITMQ_STORER_QUEUE_NAME, on_message_callback=callback, auto_ack=True
    )
    print("Ready to store articles")
    channel.start_consuming()

if __name__ == "__main__":
    main()
