import os

BOT_NAME = "mobile_de_scraper"

SPIDER_MODULES = ["mobile_de_scraper.spiders"]
NEWSPIDER_MODULE = "mobile_de_scraper.spiders"

# ScrapeUnblocker API Key - replace with your actual key
SCRAPEUNBLOCKER_API_KEY = os.environ.get("SCRAPEUNBLOCKER_API_KEY")

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "mobile_de_scraper.middlewares.ScrapeUnblockerMiddleware": 543,
}

ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
