
import config
import json
import requests
from meilisearch import Client

from transform.models import Article

def get_sources() -> list[str]:
    return json.loads(requests.get(config.SCRAPER_SOURCES_URL).content)

def is_duplicate(article: Article, client: Client) -> bool:
    result = client.index("articles").search("", {
        "filter": [f"url = '{article['url']}'"]
    })
    return result['estimatedTotalHits'] > 0

def scrape_links(source: str) -> list[str]:
    response = requests.get(config.SCRAPER_LINKS_URL + f"?source={source}")
    response.raise_for_status()
    return json.loads(response.content)

def scrape_article(url: str) -> Article:
    response = requests.get(config.SCRAPER_ARTICLE_URL + f"?&url={url}")
    content = json.loads(response.content)
    response.raise_for_status()
    return content
