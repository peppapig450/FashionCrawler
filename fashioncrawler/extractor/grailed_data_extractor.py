from .base_data_extractor import *


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

    def __init__(self, driver=None):
        """
        Initializes a GrailedDataExtractor object.

        Args:
            driver: Selenium WebDriver instance for interacting with the web pages.
        """
        if driver:
            super().__init__(driver)
            self.driver = driver
        else:
            super().__init__(driver)

    def get_page_soup(self, page_source):
        """
        Gets the BeautifulSoup instance of the current page source.

        Returns:
            BeautifulSoup instance of the current page source.
        """
        parser = etree.HTMLParser
        return BeautifulSoup(page_source, "lxml", parser=parser)

    def extract_data_to_dataframe(self):
        self.soup = self.get_page_soup(self.driver.page_source)
        self.logger.debug("Beginning Grailed data extraction.")

        data_extraction_functions = {
            "Title": self.extract_item_titles,
            "Price": self.extract_item_prices,
            "Designer": self.extract_item_designers,
            "Size": self.extract_item_sizes,
            "Posted Time": self.extract_item_post_times,
            "Listing Link": self.extract_item_listing_link,
        }

        extracted_data = {}
        for column, func in data_extraction_functions.items():
            extracted_data[column] = func()

        df = pandas.DataFrame.from_dict(extracted_data)
        self.logger.debug("Grailed data extraction completed.")

        return df

    def extract_item_post_times(self):
        """
        Extracts the post times of items from the BeautifulSoup object.

        Returns:
        - A list of item post times.
        """
        extracted_item_post_times = list(
            map(
                lambda time: time.text.split("\xa0ago")[0].replace("about ", "")
                + " ago",
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
                lambda listing_link: f"https://grailed.com{listing_link.get('href')}".split(
                    "?"
                )[
                    0
                ],
                sv.select("a.listing-item-link", self.soup),
            )
        )
        return extracted_item_listing_links
