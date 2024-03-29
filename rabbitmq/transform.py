
import json
import pika
import sentry_sdk
import uuid

import config
from transform import embed_article, is_problematic_article, process_text_for_nlp

def callback(ch, method, properties, body):
    article = json.loads(body)

    if is_problematic_article(article):
        return

    for text_col in ["title", "description", "content"]:
        article[text_col] = process_text_for_nlp(article[text_col])
    article["embeddings"] = embed_article(article)

    article["uuid"] = str(uuid.uuid4())

    ch.basic_publish(
        exchange=config.RABBITMQ_EXCHANGE_NAME,
        routing_key=config.RABBITMQ_STORER_BINDING_KEY, 
        body=json.dumps(article, default=str),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )

    logging_prefix = config.get_logging_prefix("transform", None)
    print(f"{logging_prefix} Article embedded: {article['url']}")
    
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
    channel.queue_declare(queue=config.RABBITMQ_TRANSFORM_QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=config.RABBITMQ_EXCHANGE_NAME, 
                       queue=config.RABBITMQ_TRANSFORM_QUEUE_NAME, 
                       routing_key=config.RABBITMQ_TRANSFORMER_BINDING_KEY)
    
    print("Ready to transform articles")
    channel.basic_consume(
        queue=config.RABBITMQ_TRANSFORM_QUEUE_NAME, on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    main()
