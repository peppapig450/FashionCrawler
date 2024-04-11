import logging
import sys
import time
from abc import abstractmethod

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import fashioncrawler.utils.logger_config as logger_config


class BaseScraper:
    """
    Base class for implementing web scraping functionality.

    Attributes:
        config (dict):
            Configuration settings for the web scraper.

    Methods:
        __init__(self, config):
            Initializes the scraper with the provided configuration.

        accept_cookies(self, cookie_css_selector: str) -> None:
            Accepts cookies on the website by locating and clicking the corresponding button.

        get_search_query() -> str:
            Prompt the user to enter a search query.

        search_for_query(self, search_query: str, search_bar_css_selector: str, submit_button_css_selector: str) -> None:
            Perform a search with the provided query.

        type_search(self, search: str, search_bar_css_selector: str, submit_button_css_selector: str) -> None:
            Enter the provided search query into the search bar and submit the search.

        get_to_search_bar_to_search(self, search_bar_css_selector: str, timeout=2) -> None:
            Navigate to the search bar and interact with it to initiate a search.

        navigate_to_search_bar(self, base_url: str, search_bar_css_selector: str) -> None:
            Navigate to the search bar of the website.

        wait_until_class_count_exceeds(self, class_name: str, min_count: int, timeout=5) -> None:
            Wait until the number of elements matching the specified class exceeds a minimum count.

        get_chrome_driver(options):
            Initialize and return a Chrome WebDriver instance with specified options.

        configure_driver_options(config):
            Configure the options for the Chrome WebDriver.

        wait_for_page_load(self, class_name: str, min_count: int) -> None:
            Wait for the page to load completely.

        run_scraper(self, search_query):
            Abstract method to run the scraper for a given search query.

        get_logger(self) -> logging.Logger:
            Retrieves a logger instance for the scraper.
    """

    def __init__(self, config):
        self.config = config
        self.logger = self.get_logger()
        self.driver = self.get_chrome_driver(config)

    def get_chrome_driver(self, config):
        """
        Initialize and return a Chrome WebDriver instance with specified options.

        Args:
        - options: An instance of ChromeOptions configured with desired browser options.

        Returns:
        - driver: A Chrome WebDriver instance ready for use.
        """
        options = self.configure_driver_options(config)
        return webdriver.Chrome(
            options=options, service=ChromeService(ChromeDriverManager().install())
        )

    def configure_driver_options(self, config):
        """
        Configure the options for the Chrome WebDriver.

        Returns:
        - options: The configured ChromeOptions instance.
        """
        options = Options()

        if sys.platform.startswith("win"):
            options.add_argument("--log-level=3")

        options.add_argument("--disable-blink-features=AutomationControlled")

        if config["headless"]:
            options.add_argument("--headless=new")

        return options

    def get_logger(self) -> logging.Logger:
        """
        Retrieves a logger instance for the scraper.

        Returns:
            logger (logging.Logger): A logger instance configured with a TimedRotatingFileHandler.
        """
        return logger_config.configure_logger()

    def accept_cookies(self, cookie_css_selector: str) -> None:
        """
        Accepts cookies on the website by locating and clicking the corresponding button.

        Args:
        - cookies_css_selector (str): The CSS selector for the cookies button.

        Returns:
        - None
        """
        try:
            cookies_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, cookie_css_selector))
            )
            ActionChains(self.driver).double_click(cookies_button).perform()
        except TimeoutException:
            self.logger.warning("Timeout occured while accepting cookies")

    @staticmethod
    def get_search_query() -> str:
        """
        Prompt the user to enter a search query.

        Returns:
        - The search query entered by the user.
        """
        search_query = input("Enter your search query: ")
        return search_query

    def search_for_query(
        self,
        search_query: str,
        search_bar_css_selector: str,
        submit_button_css_selector: str,
    ) -> None:
        """
        Perform a search with the provided query.

        Args:
        - search_query: The search query to be performed.
        - search_bar_css_selector: The CSS selector for the search bar.
        - submit_button_css_selector: The CSS selector for the submit button.

        Returns:
        - None
        """
        if search_query:
            self.type_search(
                search_query,
                search_bar_css_selector,
                submit_button_css_selector,
            )
        else:
            search_query = self.get_search_query()
            self.type_search(
                search_query, search_bar_css_selector, submit_button_css_selector
            )

    def type_search(
        self, search: str, search_bar_css_selector: str, submit_button_css_selector: str
    ) -> None:
        """
        Enter the provided search query into the search bar and submit the search.

        Args:
        - search: The search query to be entered into the search bar.
        - search_bar_css_selector: The CSS selector for the search bar.
        - submit_button_css_selector: The CSS selector for the submit button.

        Returns:
        - None
        """

        try:
            search_bar = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, search_bar_css_selector))
            )

            if type(self).__name__ == "GrailedScraper":
                ActionChains(self.driver).send_keys_to_element(
                    search_bar, search
                ).send_keys(Keys.ENTER).perform()

            else:
                submit_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, submit_button_css_selector)
                    )
                )
                ActionChains(self.driver).click(search_bar).send_keys(search).click(
                    submit_button
                ).perform()

        except (
            NoSuchElementException,
            StaleElementReferenceException,
            TimeoutException,
        ) as e:
            self.logger.error(
                f"An error occurred while searching on a search bar.: {e}",
                exc_info=True,
            )

    @abstractmethod
    def get_to_search_bar_to_search(
        self, search_bar_css_selector: str, timeout=2
    ) -> None:
        """
        Navigate to the search bar and interact with it to initiate a search.

        Args:
        - search_bar_css_selector: The CSS selector for the search bar.
        - timeout: The maximum time to wait for elements to be interactable.

        Returns:
        - None
        """

    def navigate_to_search_bar(
        self, base_url: str, search_bar_css_selector: str
    ) -> None:
        """
        Navigate to the search bar of the website.

        Args:
        - base_url: The base URL of the website.
        - search_bar_css_selector: The CSS selector for the search bar.

        Returns:
        - None
        """
        self.driver.get(base_url)
        self.get_to_search_bar_to_search(search_bar_css_selector)

    def wait_until_class_count_exceeds(
        self, class_name: str, min_count: int, timeout=5
    ) -> None:
        """
        Wait until the number of elements matching the specified class exceeds a minimum count.

        Args:
        - class_name: The CSS class name of the elements to count.
        - min_count: The minimum number of elements to wait for.
        - timeout: The maximum time to wait for the condition to be met.

        Returns:
        - None
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: len(
                    self.driver.find_elements(By.CSS_SELECTOR, f".{class_name}")
                )
                > min_count
            )
            # TODO: Explore logging the scraper instead of the class name or associating classes with scraper.
            self.logger.info(
                f"Number of elements matching class '{class_name} exceeded {min_count}."
            )
        except TimeoutException:
            self.logger.warning(
                f"Timeout occured while waiting for class count to exceed {min_count}."
            )

    def wait_for_page_load(self, class_name: str, min_count: int) -> None:
        """
        Wait for the page to load completely.

        Args:
        - class_name: The CSS class name of an element to wait for.
        - min_count: The minimum number of elements to wait for.

        Returns:
        - None
        """
        self.wait_until_class_count_exceeds(class_name, min_count)

    @abstractmethod
    def run_scraper(self, search_query):
        """
        Abstract method to run the scraper for a given search query.

        Args:
            search_query (str): The search query to be used for scraping.
        """
