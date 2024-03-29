# data.readtimelines.com

# Architecture

!["Architecture Diagram"](images/architecture.png)

- ETL pipeline is built with Python and RabbitMQ.
- Every step is logged to Sentry.
- The scraper service (extract stage) is scheduled to run every 5 minutes on various sources. It calls a serverless scraper function that scrapes articles in parallel.
- Articles are fed into a message queue to ensure no data loss if the tranform/load stage fails.
- In the embedding service, the articles are embedded using `all-MiniLM-L6-v2`, which provides a good balance between performance and hardware requirements/speed.
- Finally, the articles are stored in a Meilisearch instance, which is a lightweight fulltext search engine originally designed for fast client-facing search. However, our scale and speed requirements fit Meilisearch perfectly, and it's lightweight nature helps us to save on cost.
