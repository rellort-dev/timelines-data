
import pytest
import requests
import responses
from rabbitmq.scrape import log_results
from scrape import get_sources, scrape_article, scrape_links, is_duplicate

import config

@pytest.mark.parametrize(
    "source, num_new_articles, num_failures, message_postfix",
    [
        ("aljazeera", 10, 2, "10 new articles, 8 successes, 2 failures"),
        ("apnews", 0, 0, "0 new articles, 0 successes, 0 failures"),
        ("reuters", 2, 0, "2 new articles, 2 successes, 0 failures"),
    ]
)
def test_log_results(source, num_new_articles, num_failures, message_postfix, capfd):
    log_results(source, num_new_articles, num_failures)
    out, err = capfd.readouterr()
    assert message_postfix in out

@pytest.mark.parametrize(
    "source, num_new_articles, num_failures, exception",
    [
        ("aljazeera", 5, 10, ValueError),
        ("apnews", 0, 1, ValueError),
        ("reuters", -1, 10, ValueError),
        ("nytimes", 10, -1, ValueError),
        ("wapo", -2, -5, ValueError),
    ]
)
def test_log_results_invalid_inputs_cause_exception(source, num_new_articles, num_failures, exception):
    with pytest.raises(exception):
        log_results(source, num_new_articles, num_failures)

@responses.activate
@pytest.mark.parametrize(
    "server_response_json, expected_result", 
    [
        (["foo.com", "bar.com"], ["foo.com", "bar.com"]),
        (["foo.com"], ["foo.com"]),
        ([], []),
    ]
)
def test_get_sources(server_response_json, expected_result):
    responses.add(
        responses.GET, 
        config.SCRAPER_SOURCES_URL,
        json=server_response_json,
        status=200
    )
    assert get_sources() == expected_result

@responses.activate
@pytest.mark.parametrize(
    "source, links", 
    [
        ("apnews", ["a.com", "b.com", "c.com"]),
        ("nytimes", ["a.com"])
    ]
)
def test_scrape_links(source, links):
    request_url = config.SCRAPER_LINKS_URL + f"?source={source}"
    responses.add(
        responses.GET,
        request_url,
        json=links,
        status=200
    )
    assert scrape_links(source) == links

@responses.activate
@pytest.mark.parametrize(
    "source, response_status_code", 
    [
        ("apnews", 400),
        ("aljazeera", 404),
        ("nytimes", 500),
    ]
)
def test_scrape_links_invalid_status_code_raises_exception(source, response_status_code):
    request_url = config.SCRAPER_LINKS_URL + f"?source={source}"
    responses.add(
        responses.GET,
        request_url,
        status=response_status_code
    )
    with pytest.raises(requests.exceptions.HTTPError):
        scrape_links(source)

@responses.activate
@pytest.mark.parametrize(
    "link, article",
    [
        ("a.com", {"title": "Trump tweeted something", "content": "People responded"}),
        ("b.com", {"title": "Putin tweeted something", "content": "People responded"}),
        ("c.com", {"title": "Xi tweeted something", "content": "People responded"}),
    ]
)
def test_scrape_article(link, article):
    request_url = config.SCRAPER_ARTICLE_URL + f"?url={link}"
    responses.add(
        responses.GET, 
        request_url,
        json=article,
        status=200
    )
    assert scrape_article(link) == article

@responses.activate
@pytest.mark.parametrize(
    "link, response_status_code",
    [
        ("a.com", 400),
        ("b.com", 404),
        ("c.com", 500),
    ]
)
def test_scrape_article_invalid_status_code_raises_exception(link, response_status_code):
    request_url = config.SCRAPER_ARTICLE_URL + f"?url={link}"
    responses.add(
        responses.GET,
        request_url,
        json=dict(),
        status=response_status_code
    )
    with pytest.raises(requests.exceptions.HTTPError):
        scrape_article(link) 
    