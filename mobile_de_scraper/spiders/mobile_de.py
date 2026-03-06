import json
import re
import scrapy
from mobile_de_scraper.items import CarListingItem


class MobileDeSpider(scrapy.Spider):
    name = "mobile_de"
    allowed_domains = ["mobile.de", "api.scrapeunblocker.com"]

    def start_requests(self):
        # Example search URL for cars on mobile.de
        start_urls = [
            "https://suchen.mobile.de/fahrzeuge/search.html?isSearchRequest=true&vc=Car"
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # The data is cleanly provided in a JSON object within a script tag
        script_data = response.xpath(
            "//script[contains(text(), 'window.__INITIAL_STATE__')]/text()"
        ).get()

        if not script_data or "window.__INITIAL_STATE__ =" not in script_data:
            self.logger.warning("Could not find window.__INITIAL_STATE__ in response")
            return

        # Extract the JSON payload
        json_part = script_data.split("window.__INITIAL_STATE__ =")[1]
        
        # Remove anything after the JSON payload (e.g., other window variables like window.__PUBLIC_CONFIG__)
        if "window.__PUBLIC_CONFIG__" in json_part:
            json_part = json_part.split("window.__PUBLIC_CONFIG__")[0]
        
        json_part = json_part.strip()
        if json_part.endswith(";"):
            json_part = json_part[:-1]

        try:
            data = json.loads(json_part)
            items = data.get("search", {}).get("srp", {}).get("data", {}).get("searchResults", {}).get("items", [])

            for item_data in items:
                # Sometimes there are ad slots mixed in the items list
                if "type" in item_data and item_data["type"] == "inlineAdvertising":
                    continue

                # Page1Ads wrap their actual items in another list
                if item_data.get("type") == "page1Ads":
                    listings = item_data.get("items", [])
                else:
                    listings = [item_data]

                for listing in listings:
                    if not listing.get("id"):
                        continue

                    item = CarListingItem()

                    # URL construction
                    rel_url = listing.get("relativeUrl")
                    if rel_url:
                        item["url"] = f"https://suchen.mobile.de{rel_url}"
                    else:
                        item["url"] = ""

                    item["title"] = f"{listing.get('shortTitle', '')} {listing.get('subTitle', '')}".strip()
                    item["price"] = listing.get("price", {}).get("gross", "")

                    attributes = listing.get("attr", {})
                    item["registration_date"] = attributes.get("fr", "")
                    item["mileage"] = attributes.get("ml", "")
                    item["power"] = attributes.get("pw", "")

                    contact_info = listing.get("contactInfo", {})
                    item["seller_type"] = contact_info.get("typeLocalized", "")
                    item["location"] = contact_info.get("location", "")

                    yield item

            # Handle Pagination (checking if hasNextPage is true)
            search_results = data.get("search", {}).get("srp", {}).get("data", {}).get("searchResults", {})
            if search_results.get("hasNextPage"):
                current_page = search_results.get("page", 1)
                next_page_url = f"https://suchen.mobile.de/fahrzeuge/search.html?isSearchRequest=true&vc=Car&pageNumber={current_page + 1}"
                yield scrapy.Request(url=next_page_url, callback=self.parse)

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON: {e}")

