from abc import abstractmethod
from typing import List

import pandas
import soupsieve as sv
from bs4 import BeautifulSoup
from lxml import etree

from fashioncrawler.utils.logger_config import configure_logger


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

        df = pandas.DataFrame.from_dict(data_extraction_functions, orient="index")
        return df
