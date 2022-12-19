
import config
import json
import requests
from embed.models import RawArticle
from meilisearch import Client
from meilisearch.errors import MeiliSearchCommunicationError

def get_sources() -> list[str]:
    return json.loads(requests.get(config.SCRAPER_URL + "/sources").content)

def is_duplicate(url: str, client: Client) -> bool:
    try:
        result = client.index("articles").search("", {
            "filter": [f"url = '{url}'"]
        })
    except MeiliSearchCommunicationError:
        raise Exception("Check your connection with the MeiliSearch instance")

    return result['estimatedTotalHits'] > 0

def scrape_links(source: str, offset: int) -> list[str]:
    response = requests.get(config.SCRAPER_URL + f"/links?source={source}&offset={offset}")
    if response.status_code != 200:
        raise Exception(f"Scraping links from {source} returned status code {response.status_code}")
    return json.loads(response.content)

# TODO: Skip failed articles, and log + notify which articles failed
def scrape_articles(source: str, links: list[str]) -> list[RawArticle]:
    result = []

    for link in links:
        try:
            response = requests.get(config.SCRAPER_URL + f"/article?source={source}&url={link}").content
            article = json.loads(response)
            result.append(article)
        except Exception as e:
            raise Exception(f"Scraping articles from {link} ({source}) raised an exception: {e}")

    return result
