# Copyright 2024 Nicholas Brady. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


from abc import abstractmethod
from typing import List

import pandas as pd
import soupsieve as sv
from bs4 import BeautifulSoup
from lxml import etree


class BaseDataExtractor:
    """
    Base class for extracting data from web pages and storing it in a Pandas DataFrame.

    Attributes:
    - driver: WebDriver instance used for scraping.
    - page_source: HTML source of the web page.
    - soup: BeautifulSoup object representing the parsed HTML of the web page.

    Methods:
    - __init__(self, driver): Initializes the BaseDataExtractor with the WebDriver instance.
    - get_page_soup(self): Parses the page source and returns a BeautifulSoup object.
    - extract_data_to_dataframe(self, data_extraction_functions): Abstract method to extract data from the web page and store it in a Pandas DataFrame.
    """

    def __init__(self, driver):
        self.driver = driver
        self.page_source = driver.page_source
        self.soup = self.get_page_soup()

    def get_page_soup(self):
        """
        Parse the HTML page source and return a BeautifulSoup object.

        Returns:
            - soup: BeautifulSoup object representing the parsed HTML of the web page.
        """
        parser = etree.HTMLParser()
        return BeautifulSoup(self.page_source, "lxml", parser=parser)

    @abstractmethod
    def extract_data_to_dataframe(self, data_extraction_functions):
        """
        Extract data from the BeautifulSoup object and store it in a Pandas DataFrame.

        Args:
        - data_extraction_functions: A dictionary mapping column names to functions that extract data for those columns.

        Returns:
        - df: The Pandas DataFrame containing the extracted data.
        """
        extracted_data = {}
        for column, func in data_extraction_functions.items():
            extracted_data[column] = func()

        df = pd.DataFrame.from_dict(data_extraction_functions, orient="index")
        return df


class GrailedDataExtractor(BaseDataExtractor):
    """
    GrailedDataExtractor class for extracting data from Grailed listings.

    Inherits from BaseDataExtractor.

    Methods:
        - __init__(driver): Constructor method.
        - get_page_soup(driver): Retrieves BeautifulSoup instance of the current page source.
        - extract_data_to_dataframe(): Extracts data from the page and stores it in a Pandas DataFrame.
        - extract_item_post_times(): Extracts the post times of items from the BeautifulSoup object.
        - extract_item_titles(): Extracts the titles of items from the BeautifulSoup object.
        - extract_item_designers(): Extracts the designers of items from the BeautifulSoup object.
        - extract_item_sizes(): Extracts the sizes of items from the BeautifulSoup object.
        - extract_item_prices(): Extracts the prices of items from the BeautifulSoup object.
        - extract_item_listing_link(): Extracts the listing links of items from the BeautifulSoup object.
    """

    def __init__(self, driver):
        self.driver = driver

    def get_page_soup(self, driver):
        """
        Gets the BeautifulSoup instance of the current page source.

        Returns:
            BeautifulSoup instance of the current page source.
        """
        parser = etree.HTMLParser
        return BeautifulSoup(driver.page_source, "lxml", parser=parser)

    def extract_data_to_dataframe(self):
        self.soup = self.get_page_soup(self.driver)

        data_extraction_functions = {
            "Posted Time": self.extract_item_post_times,
            "Title": self.extract_item_titles,
            "Designer": self.extract_item_designers,
            "Size": self.extract_item_sizes,
            "Price": self.extract_item_prices,
            "Listing Link": self.extract_item_listing_link,
        }

        extracted_data = {}
        for column, func in data_extraction_functions.items():
            extracted_data[column] = func()

        df = pd.DataFrame.from_dict(extracted_data, orient="columns")

        return df

    def extract_item_post_times(self):
        """
        Extracts the post times of items from the BeautifulSoup object.

        Returns:
        - A list of item post times.
        """
        extracted_item_post_times = list(
            map(
                lambda time: time.text.split("\xa0ago")[0],
                sv.select(".ListingAge-module__dateAgo___xmM8y", self.soup),
            )
        )
        return extracted_item_post_times

    def extract_item_titles(self):
        """
        Extracts the titles of items from the BeautifulSoup object.

        Returns:
        - A list of item titles.
        """
        extracted_item_titles = list(
            map(
                lambda title: title.text,
                sv.select(".ListingMetadata-module__title___Rsj55", self.soup),
            )
        )
        return extracted_item_titles

    def extract_item_designers(self):
        """
        Extracts the designers of items from the BeautifulSoup object.

        Returns:
        - A list of item designers.
        """
        extracted_item_designers = list(
            map(
                lambda designer: designer.text,
                sv.select(
                    "div.ListingMetadata-module__designerAndSize___lbEdw > p:first-child",
                    self.soup,
                ),
            )
        )
        return extracted_item_designers

    def extract_item_sizes(self):
        """
        Extracts the sizes of items from the BeautifulSoup object.

        Returns:
        - A list of item sizes.
        """
        extracted_item_sizes = list(
            map(
                lambda size: size.text,
                sv.select(".ListingMetadata-module__size___e9naE", self.soup),
            )
        )
        return extracted_item_sizes

    def extract_item_prices(self):
        """
        Extracts the prices of items from the BeautifulSoup object.

        Returns:
        - A list of item prices.
        """
        extracted_item_prices = list(
            map(
                lambda price: price.text,
                sv.select('[data-testid="Current"]', self.soup),
            )
        )
        return extracted_item_prices

    def extract_item_listing_link(self):
        """
        Extracts the listing links of items from the BeautifulSoup object.

        Returns:
        - A list of item listing links.
        """
        extracted_item_listing_links = list(
            map(
                lambda listing_link: f"https://grailed.com{listing_link.get('href')}",
                sv.select("a.listing-item-link", self.soup),
            )
        )
        return extracted_item_listing_links


class DepopDataExtractor(BaseDataExtractor):
    """
    Class for extracting data from Depop.

    Inherits from BaseDataExtractor.

    Attributes:
        driver: Selenium WebDriver instance for interacting with the web pages.

    Methods:
        - __init__(driver): Initializes a DepopDataExtractor object.
        - get_page_soup(): Gets the BeautifulSoup instance of the current page source.
        - extract_data_to_dataframe(): Extracts data from item links and returns a DataFrame.
        - get_item_links(): Retrieves a list of item links from the current page.
        - extract_data_from_item_links(links): Extracts data from a list of item links.
        - extract_data(url): Extracts data from a single item page.
        - extract_item_title(): Extracts the title of the item.
        - extract_item_price(): Extracts the price of the item.
        - extract_item_seller(): Extracts the seller of the item.
        - extract_item_description(): Extracts the description of the item.
        - extract_item_condition(): Extracts the condition of the item.
        - extract_item_size(): Extracts the size of the item.
        - extract_item_time_posted(): Extracts the time when the item was listed.
    """

    def __init__(self, driver):
        """
        Initializes a DepopDataExtractor object.

        Args:
            driver: Selenium WebDriver instance for interacting with the web pages.
        """
        self.driver = driver

    # get the soup instance we're gonna use to scrape the links off of
    def get_page_soup(self, page_source=None):
        """
        Gets the BeautifulSoup instance of the current page source.

        Returns:
            BeautifulSoup instance of the current page source.
        """
        parser = etree.HTMLParser

        if page_source:
            return BeautifulSoup(page_source, "lxml", parser=parser)
        else:
            return BeautifulSoup(self.driver.page_source, "lxml", parser=parser)

    def extract_data_to_dataframe(self):
        """
        Extracts data from item links obtained by `get_item_links` method and returns a DataFrame.

        This method retrieves item links using the `get_item_links` method, then extracts
        data from these links using the `extract_data_from_item_links` method. The extracted
        data is returned as a DataFrame.

        Returns:
        - pandas.DataFrame: Extracted data as a DataFrame.

        Example:
            extractor = DepopDataExtractor(driver)
            dataframe = extractor.extract_data_to_dataframe()
        """
        item_links = self.get_item_links()
        df = self.extract_data_from_item_links(item_links)
        return df

    def get_item_links(self):
        """
        Retrieves a list of item links from the current page.

        Returns:
            List of item links extracted from the current page.
        """
        soup = self.get_page_soup()

        links = list(
            map(
                lambda item_link: f"https://depop.com{item_link.get('href')}",
                sv.select(".styles__ProductCard-sc-4aad5806-4.ffvUlI", soup),
            )
        )[:40]

        return links

    def extract_data_from_item_links(self, links):
        """
        Extracts data from a list of item links.

        Args:
            links: List of item links.

        Returns:
            DataFrame containing extracted data from the item links.
        """
        all_data = []

        for link in links:
            self.driver.get(link)
            time.sleep(0.5)

        for url, source in page_sources.items():
            if source:
                item_data = self.extract_data(source, url)
                all_data.append(item_data)

        return pd.DataFrame(all_data)

    def extract_data(self, url):
        """
        Extracts data from a single item page.

        Args:
            url: URL of the item page.

        Returns:
            Dictionary containing extracted data from the item page.
        """
        self.soup = self.get_page_soup(page_source)

        data_extraction_functions = {
            "Title": self.extract_item_title,
            "Price": self.extract_item_price,
            "Seller": self.extract_item_seller,
            "Size": self.extract_item_size,
            "Condition": self.extract_item_condition,
            "Description": self.extract_item_description,
            "Listing Age": self.extract_item_time_posted,
            "Listing Link": lambda: url,
        }

        extracted_data = {}
        for column, func in data_extraction_functions.items():
            extracted_data[column] = func()

        return extracted_data

    def extract_item_title(self) -> List[str]:
        """
        Extracts the title of the item.

        Returns:
            List containing the title of the item.
        """
        return list(
            title.text.strip()
            for title in sv.select(
                "div.ProductDetailsSticky-styles__DesktopKeyProductInfo-sc-17bd7b59-9.bKazye > h1",
                self.soup,
            )
        )

    def extract_item_price(self) -> List[str]:
        """
        Extracts the price of the item.

        Returns:
            List containing the price of the item.
        """
        prices = []

        # select both the discount and full prices if they exist using pseudo-class
        price_elements = sv.select(
            'div.ProductDetailsSticky-styles__StyledProductPrice-sc-17bd7b59-4.qJnzl > div > p:is([aria-label="Full price"], [aria-label="Discounted price"], [aria-label="Price"])',
            self.soup,
        )

        for price_element in price_elements:
            if price_element.get("aria-label") in ("Full price", "Price"):
                prices.append(price_element.text.strip())
                return prices
            elif price_element.get("aria-label") == "Discounted price":
                prices.append(price_element.text.strip())
                return prices

        return prices

    def extract_item_seller(self) -> List[str]:
        """
        Extracts the seller of the item.

        Returns:
            List containing the seller of the item.
        """
        seller_element = sv.select(
            "a.sc-eDnWTT.styles__Username-sc-f040d783-3.fRxqiS.WZqly", self.soup
        )
        if seller_element:
            return [seller_element[0].text.strip()]
        else:
            return []

    def extract_item_description(self):
        """
        Extracts the description of the item.

        Returns:
            List containing the description of the item.
        """
        return list(
            description.text.strip()
            for description in sv.select(
                ".styles__Container-sc-d367c36f-0.ffwMQV > p",
                self.soup,
            )
        )

    def extract_item_condition(self) -> List[str]:
        """
        Extracts the condition of the item.

        Returns:
            List containing the condition(s) of the item.
        """
        attribute_elements = sv.select(
            "div.ProductAttributes-styles__Attributes-sc-303d66c3-1.dIfGXO > p",
            self.soup,
        )
        conditions = []

        if len(attribute_elements) >= 3:
            conditions.append(attribute_elements[1].text.strip())
        elif len(attribute_elements) <= 2:
            conditions.append(attribute_elements[0].text.strip())

        return conditions

    def extract_item_size(self):
        """
        Extracts the size of the item.

        Returns:
            List containing the size of the item.
        """
        attribute_elements = sv.select(
            "div.ProductAttributes-styles__Attributes-sc-303d66c3-1.dIfGXO > p",
            self.soup,
        )
        size = []

        if len(attribute_elements) >= 3:
            size.append(attribute_elements[0].text.strip())

        return size

    def extract_item_time_posted(self):
        """
        Extracts the time when the item was listed.

        Returns:
            List containing the time of when the item was listed.
        """
        return list(
            map(
                lambda time_posted: time_posted.text.replace("Listed", "").strip(),
                sv.select("time[datetime]", self.soup),
            )
        )
