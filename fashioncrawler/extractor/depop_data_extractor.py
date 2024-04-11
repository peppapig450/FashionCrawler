from fashioncrawler.scraper.depop_scraper import DepopScraper

from .base_data_extractor import *


# TODO: Extract the info about how many ppl have it in their bags etc
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

    def __init__(self, driver=None):
        """
        Initializes a DepopDataExtractor object.

        Args:
            driver: Selenium WebDriver instance for interacting with the web pages.
        """
        if driver:
            super().__init__(driver)
            self.driver = driver
        else:
            super().__init__(driver)

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

    def extract_data_to_dataframe(self) -> pandas.DataFrame:
        """
        Extracts data from item links obtained by `get_item_links` method and returns a DataFrame.

        This method retrieves item links using the `get_item_links` method, then extracts
        data from these links using the `extract_data_from_item_links` method. The extracted
        data is returned as a DataFrame.

        Returns:
        - pandas.DataFrame: Extracted data as a DataFrame.

        Example:
            extractor = DepopandasataExtractor(driver)
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
        self.logger.debug("Retrieving Depop item links.")
        soup = self.get_page_soup()

        links = list(
            map(
                lambda item_link: f"https://depop.com{item_link.get('href')}",
                sv.select(".styles__ProductCard-sc-4aad5806-4.ffvUlI", soup),
            )
        )[:40]

        self.logger.debug(f"Found {len(links)} item links.")
        return links

    def extract_data_from_item_links(self, links):
        """
        Extracts data from a list of item links.

        Args:
            links: List of item links.

        Returns:
            DataFrame containing extracted data from the item links.
        """
        all_data = {
            "Title": [],
            "Price": [],
            "Seller": [],
            "Size": [],
            "Condition": [],
            "Description": [],
            "Posted Time": [],
            "Listing Link": [],
        }

        page_sources = DepopScraper.get_page_sources_concurrently(links)

        for url, source in page_sources.items():
            if source:
                item_data = self.extract_data(source, url)
                for key, value in item_data.items():
                    if key == "Listing Link":
                        all_data[key].append(value)
                    else:
                        all_data[key].extend(value)
            else:
                self.logger.error(
                    f"Failed to retrieve page source for listing link: {url}"
                )

        self.logger.debug("Extraction from item links completed.")
        return pandas.DataFrame.from_dict(all_data)

    def extract_data(self, page_source, url):
        """
        Extracts data from a single item page.

        Args:
            url: URL of the item page.

        Returns:
            Dictionary containing extracted data from the item page.
        """
        self.logger.debug(f"Extracting data from item page: {url}")
        self.soup = self.get_page_soup(page_source)

        data_extraction_functions = {
            "Title": self.extract_item_title,
            "Price": self.extract_item_price,
            "Seller": self.extract_item_seller,
            "Size": self.extract_item_size,
            "Condition": self.extract_item_condition,
            "Description": self.extract_item_description,
            "Posted Time": self.extract_item_time_posted,
            "Listing Link": lambda: url,
        }

        extracted_data = {}
        for column, func in data_extraction_functions.items():
            extracted_data[column] = func()

        self.logger.debug("Data extraction from item page completed.")
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
            return [""]

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

        if attribute_elements:
            if len(attribute_elements) >= 3:
                conditions.append(attribute_elements[1].text.strip())
            elif len(attribute_elements) <= 2:
                conditions.append(attribute_elements[0].text.strip())
        else:
            conditions.append("")

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
        else:
            size.append("")

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
