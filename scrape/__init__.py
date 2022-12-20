
import config
import json
import requests
from embed.models import Article
from meilisearch import Client

UNIX_TIMESTAMP_MIN_VALUE = 0

def get_sources() -> list[str]:
    return json.loads(requests.get(config.SCRAPER_URL + "/sources").content)

def is_duplicate(article: Article, client: Client) -> bool:
    result = client.index("articles").search("", {
        "filter": [f"url = '{article['url']}'"]
    })
    return result['estimatedTotalHits'] > 0

def get_latest_published_time(source: str, client: Client):
    result = client.index("articles").search("", {
        "filter": [f"source = '{source}'"],
        "sort": [
            "publishedTime:desc"
        ]
    })
    if result["hits"]:
        return result["hits"][0]["publishedTime"]
    else:
        return UNIX_TIMESTAMP_MIN_VALUE
    
def scrape_links(source: str, offset: int) -> list[str]:
    response = requests.get(config.SCRAPER_URL + f"/links?source={source}&offset={offset}")
    if response.status_code != 200:
        raise Exception(f"Scraping links from {source} returned status code {response.status_code}")
    return json.loads(response.content)

def scrape_article(source: str, link: str):
    response = requests.get(config.SCRAPER_URL + f"/article?source={source}&url={link}")
    content = json.loads(response.content)
    if response.status_code != 200:
        raise Exception(f"Scraping article from {link} returned status code {response.status_code}: {content}")
    return content
