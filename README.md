# data.readtimelines.com

# Usage
`transform.py` and `load.py` are consumers written as persistent scripts, i.e. they keep running in the background, waiting to receive new articles. 

`extract.py` is a producer written as a normal python script. You can run it manually to scrape 50 articles (this amount is configurable) from a source. However, it is usually run periodically using a CRON job. 

To test the data pipeline, 
1. Provide the `SCRAPER_URL` as an environment variable.
2. Run a Meilisearch instance, and provide the `MEILISEARCH_URL` and `MEILISEARCH_KEY`.
3. Run a RabbitMQ instance, and provide the `RABBITMQ_HOST`.
4. Run each of the following commands on three different terminals. Note that `embed.py` and `load.py` has to be started before `extract.py` is run.
  ```
  python -m rabbitmq.transform  # Run this on terminal 1
  python -m rabbitmq.load  # Run this on terminal 2
  python -m rabbitmq.extract <source>  # Run this on terminal 3
  ```
 
