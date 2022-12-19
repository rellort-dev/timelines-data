
import config
import pika
from meilisearch import Client
from meilisearch.errors import MeiliSearchCommunicationError


def callback(ch, method, properties, body):
    print("Storing articles...")
    client = Client(config.MEILISEARCH_URL, config.MEILISEARCH_KEY)
    client.index("articles").add_documents(body)
    print("Articles stored")

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.exchange_declare(exchange=config.RABBITMQ_EXCHANGE_NAME, exchange_type="direct")
    channel.queue_declare(queue=config.RABBITMQ_STORER_QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=config.RABBITMQ_EXCHANGE_NAME, 
                       queue=config.RABBITMQ_STORER_QUEUE_NAME, 
                       routing_key=config.RABBITMQ_STORER_BINDING_KEY)
    
    print("Ready to store articles")
    channel.basic_consume(
        queue=config.RABBITMQ_STORER_QUEUE_NAME, on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    main()
