from .base_scraper import *


class StockxScraper(BaseScraper):
    """
    Subclass of BaseScraper for scraping data from the StockX website.
    """

    def __init__(self, base_scraper):
        self.driver = base_scraper.driver

    def get_to_search_bar_to_search(
        self, search_bar_css_selector: str, timeout=2
    ) -> None:
        pass

    def run_scraper(self, search_query):
        pass
