
import config
import json
import pandas as pd
import pika
import sentry_sdk
import uuid
from embed import remove_problematic_articles, process_text_columns_for_displaying, process_text_columns_for_nlp, embed_column


def callback(ch, method, properties, body):
    articles = json.loads(body)
    print(f"Embedding {len(articles)} articles...")

    if len(articles) == 0:
        print("Done embedding articles")
        return 

    df = pd.DataFrame.from_records(articles)
    if "error" in df:  # due to from_records
        df = df.drop(columns=["error", "stacktrace"])

    df = remove_problematic_articles(df, columns_to_check=['title', 'description', 'content'])
    df["text"] = df.title + ' ' + df.description + ' ' + df.content
    df = process_text_columns_for_nlp(df, columns=['text'])
    df = process_text_columns_for_displaying(df, columns=['title', 'description'])

    df = embed_column(df, column="text")
    df = df.drop(columns=["text"])
    df["uuid"] = [str(uuid.uuid4()) for _ in range(len(df.index))]  
    # iterating over a range is more efficient than a NumPy array

    embedded_articles = df.to_dict(orient='records')

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
    sentry_sdk.init(
        dsn="https://72dcd0f50d5e40fda890cce86cd02b00@o4504354060369920.ingest.sentry.io/4504354063450114",
        traces_sample_rate=1.0
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
    
    print("Ready to embed articles")
    channel.basic_consume(
        queue=config.RABBITMQ_EMBEDDER_QUEUE_NAME, on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    main()
