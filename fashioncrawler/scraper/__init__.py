"""
Fashion Crawler Package
=======================

This package provides functionality for web scraping fashion-related websites.

Modules:
- base_scraper: Provides a base class with functionality for web scraping using Selenium.
- grailed_scraper: Implements a scraper for the Grailed website.
- depop_scraper: Implements a scraper for the Depop website.
- stockx_scraper: Implements a scraper for the StockX website.
"""

from .base_scraper import BaseScraper
from .grailed_scraper import GrailedScraper
from .depop_scraper import DepopScraper
from .stockx_scraper import StockxScraper
