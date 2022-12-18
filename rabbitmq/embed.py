
import config
import json
import pika
import uuid
from embed import embed 


def callback(ch, method, properties, body):
    articles = json.loads(body)

    print(f"Embedding {len(articles)} articles...")
    embedded_articles = embed(articles)

    for i in range(len(embedded_articles)):
        embedded_articles[i]["uuid"] = str(uuid.uuid4())
    
    ch.basic_publish(
        exchange=config.RABBITMQ_EXCHANGE_NAME,
        routing_key=config.RABBITMQ_STORER_BINDING_KEY, 
        body=json.dumps(embedded_articles),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )
    print("Done embedding articles")
    return 

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.exchange_declare(exchange=config.RABBITMQ_EXCHANGE_NAME, exchange_type="direct")
    channel.queue_declare(queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=config.RABBITMQ_EXCHANGE_NAME, 
                       queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, 
                       routing_key=config.RABBITMQ_EMBEDDER_BINDING_KEY)
    
    print("Ready to embed articles")
    channel.basic_consume(
        queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    main()
