import pytest
from scrapy.http import Request, HtmlResponse
from scrapy.exceptions import NotConfigured
from scrapy.spiders import Spider
from mobile_de_scraper.middlewares import ScrapeUnblockerMiddleware
import urllib.parse


class MockSettings:
    def __init__(self, d):
        self.d = d

    def get(self, k):
        return self.d.get(k)


class MockCrawler:
    def __init__(self, settings_dict):
        self.settings = MockSettings(settings_dict)


class MockSpider(Spider):
    name = "mock"

    def parse(self, response):
        yield {"url": response.url}


def test_middleware_requires_api_key():
    crawler = MockCrawler({})
    with pytest.raises(NotConfigured):
        ScrapeUnblockerMiddleware.from_crawler(crawler)


def test_middleware_modifies_request():
    crawler = MockCrawler({"SCRAPEUNBLOCKER_API_KEY": "test_key"})
    middleware = ScrapeUnblockerMiddleware.from_crawler(crawler)
    spider = MockSpider()

    original_url = "https://suchen.mobile.de/test"
    request = Request(url=original_url)

    # Process request
    new_request = middleware.process_request(request, spider)

    assert new_request is not None
    assert new_request.url.startswith("https://api.scrapeunblocker.com/get_page_source")
    assert new_request.method == "POST"
    assert new_request.callback == middleware._handle_unblocker_response

    parsed_url = urllib.parse.urlparse(new_request.url)
    qs = urllib.parse.parse_qs(parsed_url.query)

    assert b"x-scrapeunblocker-key" in new_request.headers
    assert new_request.headers[b"x-scrapeunblocker-key"] == b"test_key"
    assert qs["url"][0] == original_url
    assert new_request.meta["original_url"] == original_url
    assert new_request.meta["original_callback"] == spider.parse


def test_middleware_ignores_already_processed_request():
    crawler = MockCrawler({"SCRAPEUNBLOCKER_API_KEY": "test_key"})
    middleware = ScrapeUnblockerMiddleware.from_crawler(crawler)
    spider = MockSpider()

    # Request already pointing to API
    api_url = "https://api.scrapeunblocker.com/get_page_source?url=https%3A%2F%2Fsuchen.mobile.de%2Ftest"
    request = Request(
        url=api_url, 
        method="POST",
        headers={"x-scrapeunblocker-key": "test_key"}
    )

    # Should return None, meaning process normally
    new_request = middleware.process_request(request, spider)

    assert new_request is None


def test_middleware_handle_unblocker_response():
    crawler = MockCrawler({"SCRAPEUNBLOCKER_API_KEY": "test_key"})
    middleware = ScrapeUnblockerMiddleware.from_crawler(crawler)
    spider = MockSpider()

    # Create the meta context just as process_request does
    original_url = "https://suchen.mobile.de/test"
    meta = {"original_url": original_url, "original_callback": spider.parse}

    # Simulate response from API
    api_response = HtmlResponse(
        url="https://api.scrapeunblocker.com/get_page_source?...",
        body=b"<html>hello</html>",
        request=Request(url="https://api.scrapeunblocker.com/...", meta=meta),
    )

    # Handle the response
    results = list(middleware._handle_unblocker_response(api_response))

    assert len(results) == 1
    # Check that spider.parse received a response with the original URL
    assert results[0]["url"] == original_url
