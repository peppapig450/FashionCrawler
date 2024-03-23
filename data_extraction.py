import asyncio

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
from soupsieve import select


class BaseDataExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.page_source = driver.page_source
        self.soup = self.get_page_soup()

    def get_page_soup(self):
        parser = etree.HTMLParser()
        return BeautifulSoup(self.page_source, "lxml", parser=parser)

    def extract_data_to_dataframe(self, data_extraction_functions):
        """
        Extract data from the BeautifulSoup object and store it in a Pandas DataFrame.

        Args:
        - data_extraction_functions: A dictionary mapping column names to functions that extract data for those columns.

        Returns:
        - df: The Pandas DataFrame containing the extracted data.
        """
        df = pd.DataFrame(columns=data_extraction_functions.keys())
        for column, func in data_extraction_functions.items():
            df[column] = func()
        return df


class GrailedDataExtractor(BaseDataExtractor):

    def extract_data_to_dataframe(self):
        data_extraction_functions = {
            "Posted Time": self.extract_item_post_times,
            "Title": self.extract_item_titles,
            "Designer": self.extract_item_designers,
            "Size": self.extract_item_sizes,
            "Price": self.extract_item_prices,
            "Listing Link": self.extract_item_listing_link,
        }
        return super().extract_data_to_dataframe(data_extraction_functions)

    def extract_item_post_times(self):
        return list(
            map(
                lambda time: time.text.split("\xa0ago")[0],
                select(".ListingAge-module__dateAgo___xmM8y", self.soup),
            )
        )

    def extract_item_titles(self):
        return list(
            map(
                lambda title: title.text,
                select(".ListingMetadata-module__title___Rsj55", self.soup),
            )
        )

    def extract_item_designers(self):
        return list(
            map(
                lambda designer: designer.text,
                select(
                    "div.ListingMetadata-module__designerAndSize___lbEdw > p:first-child",
                    self.soup,
                ),
            )
        )

    def extract_item_sizes(self):
        return list(
            map(
                lambda size: size.text,
                select(".ListingMetadata-module__size___e9naE", self.soup),
            )
        )

    def extract_item_prices(self):
        """
        Extracts the prices of items from the BeautifulSoup object.

        Args:
        - soup: The BeautifulSoup object containing the parsed HTML.

        Returns:
        - A list of item prices.
        """
        return list(
            map(lambda price: price.text, select('[data-testid="Current"]', self.soup))
        )

    def extract_item_listing_link(self):
        """
        Extracts the listing links of items from the BeautifulSoup object.

        Args:
        - soup: The BeautifulSoup object containing the parsed HTML.

        Returns:
        - A list of item listing links.
        """
        return list(
            map(
                lambda listing_link: f"https://grailed.com{listing_link.get('href')}",
                select("a.listing-item-link", self.soup),
            )
        )


class DepopDataExtractor(BaseDataExtractor):
    def __init__(self, driver):
        self.driver = driver

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    # get the soup instance we're gonna use to scrape the links off of
    def get_page_soup(self, driver):
        self.page_source = driver.page_source()
        parser = etree.HTMLParser
        return BeautifulSoup(self.page_source, "lxml", parser=parser)

    # soup for each individual link?
    async def get_individual_soup(self, html):
        parser = etree.HTMLParser()
        return BeautifulSoup(html, "lxml", parser=parser)

    # get the item links that we're going to scrape from
    async def extract_item_links(self, session, driver):
        soup = await self.get_individual_soup(driver.page_source)

        links = list(
            map(
                lambda item_link: f"https://depop.com{item_link.get('href')}",
                select(".styles__ProductCard-sc-4aad5806-4.ffvUlI", soup),
            )
        )[:40]

        return links

    pass
