# data.readtimelines.com

# Usage
`embed.py` and `store_to_db.py` are consumers written as persistent scripts, i.e. they keey running in the background, waiting to receive new articles. 

`scrape.py` is a producer written as a normal python script. You can run it manually to scrape 50 articles (this amount is configurable) from a source. However, it is usually run periodically using a CRON job. 

To test the data pipeline, 
1. Provide the `SCRAPER_URL` as an environment variable.
2. Run a Meilisearch instance, and provide the `MEILISEARCH_URL` and `MEILISEARCH_KEY`.
3. Run a RabbitMQ instance, and provide the `RABBITMQ_HOST`.
4. Run each of the following commands on three different terminals. Note that `embed.py` and `store_to_db.py` has to be started before `scrape.py` is run.
  ```
  python -m rabbitmq.embed  # Run this on terminal 1
  python -m rabbitmq.store_to_db  # Run this on terminal 2
  python -m rabbitmq.scrape <source>  # Run this on terminal 3
  ```
 
