# mobile.de Listing Scraper with ScrapeUnblocker

This project is a Scrapy spider designed to scrape car listings from mobile.de. It utilizes the ScrapeUnblocker API via a Scrapy middleware to bypass anti-bot protections.

## Project Structure

- `mobile_de_scraper/spiders/mobile_de.py`: The main spider logic for navigating and parsing mobile.de listings.
- `mobile_de_scraper/middlewares.py`: Contains the `ScrapeUnblockerMiddleware` which intercepts outgoing requests and routes them through the ScrapeUnblocker API.
- `mobile_de_scraper/items.py`: Defines the data structure for scraped car listings.
- `tests/`: Contains pytest tests for the spider and the middleware.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure ScrapeUnblocker API Key:**
   Open `mobile_de_scraper/settings.py` and replace `YOUR_API_KEY_HERE` with your actual ScrapeUnblocker API key:
   ```python
   SCRAPEUNBLOCKER_API_KEY = "YOUR_ACTUAL_API_KEY"
   ```

## Using the ScrapeUnblocker API Middleware

The `ScrapeUnblockerMiddleware` is automatically enabled in `settings.py`. 

### How it works:
1. When Scrapy generates a request to `mobile.de` (e.g. from `start_urls`), the middleware intercepts it.
2. It rewrites the URL to point to the ScrapeUnblocker API endpoint (`https://api.scrapeunblocker.com/get_page_source`).
3. It transforms the request into a POST request, appending the original target URL as a query parameter, and includes your API key in the `x-scrapeunblocker-key` HTTP header.
4. The spider parses the response as if it came directly from `mobile.de`.

To customize the ScrapeUnblocker API call (e.g., to enable JS rendering or specify a geolocation proxy), modify the `params` dictionary in `mobile_de_scraper/middlewares.py`:

```python
params = {
    "url": target_url,
    "render_js": "true", # Example: Enable JavaScript rendering
    "country": "de",     # Example: Use German proxies
}
```

## Local Development and Debugging

For development and debugging in an IDE, a helper script `work_local.py` is provided. This script allows you to run the spider directly without using the `scrapy crawl` command, making it easier to set breakpoints.

### Setting up Local Environment Variables

To avoid hardcoding your API key in the settings, you should use a `.local.env` file (which is already ignored by git):

1. Create a file named `.local.env` in the project root.
2. Add your API key to it:
   ```env
   SCRAPEUNBLOCKER_API_KEY=your_actual_api_key_here
   ```

The `work_local.py` script is configured to automatically load this file and inject the key into Scrapy's settings.

### Running Locally

To run the spider for debugging:

```bash
python work_local.py
```

## Running the Scraper via CLI

To start a standard scraping job, run the following command from the project root:

```bash
scrapy crawl mobile_de -o output.json
```
This will run the spider and save the scraped listings into an `output.json` file.

## Running Tests

Tests are written using `pytest`. Ensure you have the test dependencies installed (`pytest`, `pytest-asyncio`), then run:

```bash
pytest tests/
```
