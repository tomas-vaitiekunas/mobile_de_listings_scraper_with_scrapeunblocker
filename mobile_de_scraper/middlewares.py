import json
import urllib.parse
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse


class ScrapeUnblockerMiddleware:
    def __init__(self, api_key):
        self.api_key = api_key
        # Example API endpoint for ScrapeUnblocker
        self.api_url = "https://api.scrapeunblocker.com/get_page_source"

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get("SCRAPEUNBLOCKER_API_KEY")
        if not api_key:
            raise NotConfigured("SCRAPEUNBLOCKER_API_KEY is not set in settings")
        return cls(api_key)

    def process_request(self, request, spider):
        # Don't process if it's already going to the ScrapeUnblocker API
        if self.api_url in request.url:
            return None

        # Build the new URL for ScrapeUnblocker API
        target_url = request.url
        params = {
            "url": target_url,
            "render_js": "true",
            "proxy_type": "residential",
        }

        # We replace the request URL with the ScrapeUnblocker API URL
        new_url = f"{self.api_url}?{urllib.parse.urlencode(params)}"

        headers = request.headers.copy()
        headers["x-scrapeunblocker-key"] = self.api_key

        original_callback = request.callback or spider.parse
        meta = request.meta.copy()
        meta["original_url"] = target_url
        meta["original_callback"] = original_callback
        meta["handle_httpstatus_all"] = True

        # Return a new request, preserving original target URL in meta
        return request.replace(
            url=new_url,
            method="POST",
            headers=headers,
            body=b"",
            callback=self._handle_unblocker_response,
            meta=meta,
            dont_filter=True,
        )

    def _handle_unblocker_response(self, response):
        original_url = response.meta.get("original_url")
        original_callback = response.meta.get("original_callback")

        # Convert the API response into an HtmlResponse for the original URL
        new_response = HtmlResponse(
            url=original_url,
            body=response.body,
            encoding=response.encoding,
            request=response.request,
            status=response.status,
            headers=response.headers,
        )

        result = original_callback(new_response)
        if result:
            yield from result
