import pytest
from scrapy.http import HtmlResponse, Request
from mobile_de_scraper.spiders.mobile_de import MobileDeSpider
from mobile_de_scraper.items import CarListingItem


@pytest.fixture
def spider():
    return MobileDeSpider()


def test_parse_extracts_listings(spider):
    html_content = b"""
    <html>
        <body>
            <script>
                window.__INITIAL_STATE__ = {
                    "search": {
                        "srp": {
                            "data": {
                                "searchResults": {
                                    "hasNextPage": true,
                                    "page": 1,
                                    "items": [
                                        {
                                            "id": "123",
                                            "relativeUrl": "/test-car-url",
                                            "shortTitle": "Volkswagen",
                                            "subTitle": "Golf",
                                            "price": {
                                                "gross": "15,000 EUR"
                                            },
                                            "attr": {
                                                "fr": "01/2020",
                                                "ml": "50,000 km",
                                                "pw": "110 kW"
                                            },
                                            "contactInfo": {
                                                "typeLocalized": "Dealer",
                                                "location": "Berlin"
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                };
            </script>
        </body>
    </html>
    """
    request = Request(url="https://suchen.mobile.de/test")
    # Middleware already reconstructed the response with the original URL
    response = HtmlResponse(
        url="https://suchen.mobile.de/test",
        body=html_content,
        request=request,
    )

    results = list(spider.parse(response))

    # One item and one pagination request
    assert len(results) == 2

    item = results[0]
    assert isinstance(item, CarListingItem)
    assert item["title"] == "Volkswagen Golf"
    assert "15,000 EUR" in item["price"]
    assert item["url"] == "https://suchen.mobile.de/test-car-url"
    assert item["registration_date"] == "01/2020"
    assert item["mileage"] == "50,000 km"

    next_request = results[1]
    assert isinstance(next_request, Request)
    assert next_request.url == "https://suchen.mobile.de/fahrzeuge/search.html?isSearchRequest=true&vc=Car&pageNumber=2"
