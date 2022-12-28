
import config
import json
import requests
from embed.models import Article
from meilisearch import Client

UNIX_TIMESTAMP_MIN_VALUE = 0

def get_sources() -> list[str]:
    return json.loads(requests.get(config.SCRAPER_SOURCES_URL).content)

def is_duplicate(article: Article, client: Client) -> bool:
    result = client.index("articles").search("", {
        "filter": [f"url = '{article['url']}'"]
    })
    return result['estimatedTotalHits'] > 0

def get_latest_published_time(source: str, client: Client) -> int:
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
    response = requests.get(config.SCRAPER_LINKS_URL + f"?source={source}&offset={offset}")
    response.raise_for_status()
    return json.loads(response.content)

def scrape_article(source: str, link: str):
    response = requests.get(config.SCRAPER_ARTICLE_URL + f"?source={source}&url={link}")
    content = json.loads(response.content)
    if response.status_code != 200:
        pretty_printed_exception = json.dumps(content, indent=4)
        raise Exception(f"Scraping article from {link} returned status code {response.status_code}: \n{pretty_printed_exception}")
    return content
