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

import logging
import os
import sys
import threading
import time
import traceback
from abc import abstractmethod
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
from logging.handlers import TimedRotatingFileHandler

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


class BaseScraper:
    """
    Base class for implementing web scraping functionality.

    Attributes:
    - config (dict): Configuration settings for the web scraper.

    Methods:
    - __init__(self, config): Initializes the scraper with the provided configuration.
    - accept_cookies(self, cookie_css_selector: str) -> None:
        Accepts cookies on the website by locating and clicking the corresponding button.
    - get_search_query() -> str:
        Prompt the user to enter a search query.
    - search_for_query(self, search_query: str, search_bar_css_selector: str, submit_button_css_selector: str) -> None:
        Perform a search with the provided query.
    - type_search(self, search: str, search_bar_css_selector: str, submit_button_css_selector: str) -> None:
        Enter the provided search query into the search bar and submit the search.
    - get_to_search_bar_to_search(self, search_bar_css_selector: str, timeout=2) -> None:
        Navigate to the search bar and interact with it to initiate a search.
    - navigate_to_search_bar(self, base_url: str, search_bar_css_selector: str) -> None:
        Navigate to the search bar of the website.
    - wait_until_class_count_exceeds(self, class_name: str, min_count: int, timeout=5) -> None:
        Wait until the number of elements matching the specified class exceeds a minimum count.
    - get_chrome_driver(options):
        Initialize and return a Chrome WebDriver instance with specified options.
    - configure_driver_options(config):
        Configure the options for the Chrome WebDriver.
    - wait_for_page_load(self, class_name: str, min_count: int) -> None:
        Wait for the page to load completely.
    - run_scraper(self, search_query):
        Abstract method to run the scraper for a given search query.
    """

    def __init__(self, config):
        try:
            self.config = config
            options = self.configure_driver_options(config)
            self.driver = self.get_chrome_driver(options)
            self.logger = self.get_logger()
        except Exception as e:
            self.logger.error(
                f"An error occurred while initializing the ChromeDriver: {e}",
                exc_info=True,
            )
            raise

    def get_logger(self) -> logging.Logger:
        """
        Retrieves a logger instance for the scraper.

        This method configures a logger instance with a TimedRotatingFileHandler for log rotation.
        Log files are rotated daily, and a specified number of backup log files are retained.
        The logger is configured to log messages with DEBUG level and above.

        Returns:
            logger (logging.Logger): A logger instance configured with a TimedRotatingFileHandler.
        """

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)

        # Create a TimedRotatingFileHandler for log rotation
        log_file = os.path.join(logs_dir, "scraper.log")
        handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=7
        )  # Rotate daily, keep 7 days' worth of logs
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger

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

            ActionChains(self.driver).send_keys_to_element(
                search_bar, search
            ).send_keys(Keys.ENTER).perform()

        except (
            NoSuchElementException,
            StaleElementReferenceException,
            TimeoutException,
        ) as e:
            self.logger.error(
                f"An error occurred while searching on Grailed: {e}", exc_info=True
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

    @staticmethod
    def get_chrome_driver(options):
        """
        Initialize and return a Chrome WebDriver instance with specified options.

        Args:
        - options: An instance of ChromeOptions configured with desired browser options.

        Returns:
        - driver: A Chrome WebDriver instance ready for use.
        """
        return webdriver.Chrome(
            options=options, service=ChromeService(ChromeDriverManager().install())
        )

    @staticmethod
    def configure_driver_options(config):
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


class GrailedScraper(BaseScraper):
    """
    Subclass of BaseScraper for scraping data from the Grailed website.

    Attributes:
    - LOGIN_POPUP_SELECTOR (str): CSS selector for the login popup.
    - SEARCH_BAR_CSS_SELECTOR (str): CSS selector for the search bar.
    - SEARCH_BAR_SUBMIT_CSS_SELECTOR (str): CSS selector for the search bar submit button.
    - COOKIES_CSS_SELECTOR (str): CSS selector for the cookies acceptance button.
    - BASE_URL (str): Base URL of the Grailed website.
    - ITEM_CLASS_NAME (str): CSS class name for identifying items on the page.
    - MIN_COUNT (int): Minimum count of items to wait for during page load.

    Methods:
    - __init__(self, base_scraper): Initializes the Grailed scraper with the base scraper object.
    - run_scraper(self, search_query) -> None: Runs the Grailed scraper to search for items based on the provided search query.
    - _navigate_and_search(self, search_query: str) -> None: Navigates to the search bar and performs a search based on the provided query.
    - get_to_search_bar_to_search(self, search_bar_css_selector: str, timeout=2) -> None: Navigate to the search bar and interact with it to initiate a search.
    - _dismiss_login_popup(self, timeout: int) -> None: Dismisses the login popup within a specified timeout period.
    """

    # Selectors for various elements
    LOGIN_POPUP_SELECTOR = ".ReactModal__Content.ReactModal__Content--after-open.modal.Modal-module__authenticationModal___g7Ufu._hasHeader"
    SEARCH_BAR_CSS_SELECTOR = "#header_search-input"
    SEARCH_BAR_SUBMIT_CSS_SELECTOR = ".Button-module__button___fE9iu.Button-module__small___uF0cg.Button-module__secondary___gYP5i.Form-module__searchButton___WDphC"
    COOKIES_CSS_SELECTOR = "#onetrust-accept-btn-handler"

    BASE_URL = "https://grailed.com"

    # Item related constants
    ITEM_CLASS_NAME = "feed-item"
    MIN_COUNT = 30

    def __init__(self, base_scraper):
        self.driver = base_scraper.driver
        self.logger = base_scraper.logger

    def run_scraper(self, search_query) -> None:
        """
        Runs the Grailed scraper to search for items based on the provided search query.

        Args:
        - search_query (str): The search query to be used for searching items.

        Returns:
        - None
        """
        self._navigate_and_search(search_query)
        super().wait_for_page_load(self.ITEM_CLASS_NAME, self.MIN_COUNT)

    def _navigate_and_search(self, search_query: str) -> None:
        """
        Navigates to the search bar and performs a search based on the provided query.

        Args:
        - search_query (str): The search query to be used for searching items.

        Returns:
        - None
        """
        super().navigate_to_search_bar(self.BASE_URL, self.SEARCH_BAR_CSS_SELECTOR)
        super().search_for_query(
            search_query,
            self.SEARCH_BAR_CSS_SELECTOR,
            self.SEARCH_BAR_SUBMIT_CSS_SELECTOR,
        )

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
        try:
            self.accept_cookies(self.COOKIES_CSS_SELECTOR)

            search_bar = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, search_bar_css_selector))
            )
            search_bar.click()

            for _ in range(3):
                try:
                    self._dismiss_login_popup(timeout=2)
                    break
                except TimeoutException:
                    pass

        except (
            NoSuchElementException,
            StaleElementReferenceException,
            TimeoutException,
        ) as e:
            self.logger.error(
                f"Error interacting with Grailed search bar: {e}", exc_info=True
            )
            sys.exit(1)

    def _dismiss_login_popup(self, timeout: int) -> None:
        """
        Dismisses the login popup within a specified timeout period.

        Args:
        - timeout (int): The maximum time to wait for the login popup.

        Returns:
        - None
        """

        try:
            login_popup = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        self.LOGIN_POPUP_SELECTOR,
                    )
                )
            )

            ActionChains(self.driver).move_to_element(login_popup).pause(
                1
            ).move_by_offset(250, 0).pause(1).click()

            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

            WebDriverWait(self.driver, 10).until_not(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        self.LOGIN_POPUP_SELECTOR,
                    )
                )
            )

        except TimeoutException:
            self.logger.info("Login popup did not appear within the timeout.")


class DepopScraper(BaseScraper):
    """
    Subclass of BaseScraper for scraping data from the Depop website.

    Attributes:
    - COOKIE_CSS_SELECTOR (str): CSS selector for the cookies button.
    - SEARCH_ICON_SELECTOR (str): CSS selector for the search icon.
    - SEARCH_BAR_SELECTOR (str): CSS selector for the search bar.
    - SUBMIT_BUTTON_SELECTOR (str): CSS selector for the submit button.
    - BACKUP_SUBMIT_BUTTON_SELECTOR (str): CSS selector for the backup submit button.
    - BASE_URL (str): Base URL of the Depop website.
    - ITEM_CLASS_NAME (str): CSS class name for identifying items on the page.
    - MIN_COUNT (int): Minimum count of items to wait for during page load.

    Methods:
    - __init__(self, base_scraper): Initializes the Depop scraper with the base scraper object.
    - run_scraper(self, search_query) -> None: Runs the Depop scraper to search for items based on the provided search query.
    - get_to_search_bar_to_search(self, search_icon_css_selector: str, timeout=2) -> None: Navigate to the search bar and interact with it to initiate a search.
    - type_search(self, search: str, search_bar_css_selector: str, submit_button_css_selector: str) -> None: Enter the provided search query into the search bar and submit the search.
    - _navigate_and_search(self, search_query: str) -> None: Navigates to the search bar and performs a search based on the provided query.
    """

    # Element selectors
    COOKIE_CSS_SELECTOR = "button.sc-hjcAab.bpwLYJ.sc-gshygS.fFJfAu"
    SEARCH_ICON_SELECTOR = "button.ButtonMinimal-sc-6a6e37b5-0.SearchBar-styles__SearchButton-sc-ac2d78a2-8.gFYYaH.dUAcFR"
    SEARCH_BAR_SELECTOR = "#searchBar__input"
    SUBMIT_BUTTON_SELECTOR = (
        "button.SearchBar-styles__SubmitButton-sc-ac2d78a2-6.gOIiyI"
    )
    BACKUP_SUBMIT_BUTTON_SELECTOR = (
        "button.SearchBar-styles__SubmitButton-sc-ac2d78a2-6.knZqMC"
    )

    BASE_URL = "https://depop.com"

    # Item related constants for page loading
    ITEM_CLASS_NAME = "styles__ProductImageGradient-sc-4aad5806-6.hzrneU"  # use image as there isn't a container for items
    MIN_COUNT = 30

    def __init__(self, base_scraper):
        self.driver = base_scraper.driver
        self.logger = base_scraper.logger

    def run_scraper(self, search_query: str) -> None:
        """
        Runs the Depop scraper to search for items based on the provided search query.

        Args:
        - search_query (str): The search query to be used for searching items.

        Returns:
        - None
        """
        self._navigate_and_search(search_query)
        super().wait_for_page_load(self.ITEM_CLASS_NAME, self.MIN_COUNT)

    def get_to_search_bar_to_search(
        self,
        search_bar_css_selector: str,
        timeout=2,
    ) -> None:
        """
        Navigate to the search bar and interact with it to initiate a search.

        Args:
        - search_icon_css_seelctor: The magnifying glass you must click to get to search bar on depop.
        - timeout: The maximum time to wait for elements to be interactable.

        Returns:
        - None
        """
        try:
            self.accept_cookies(self.COOKIE_CSS_SELECTOR)

            search_icon = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, search_bar_css_selector))
            )
            search_icon.click()

        except (
            NoSuchElementException,
            StaleElementReferenceException,
            TimeoutException,
        ) as e:
            self.logger.error(f"Error interacting with search bar: {e}", exc_info=True)
            self.driver.quit()

    def type_search(
        self,
        search: str,
        search_bar_css_selector: str,
        submit_button_css_selector: str,
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
        search_bar = self.driver.find_element(By.CSS_SELECTOR, search_bar_css_selector)

        ActionChains(self.driver).click(search_bar).send_keys(search).click(
            search_bar
        ).perform()

        # depop has 2 different possible search submit buttons depending on screen size
        # we check for both here and we use access the variable for the backup from self so that we can
        # still call the search_for_query from super
        try:
            submit_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, submit_button_css_selector)
                )
            )
            submit_button.click()
        except TimeoutException:
            try:
                submit_button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, self.BACKUP_SUBMIT_BUTTON_SELECTOR)
                    )
                )
                submit_button.click()
            except TimeoutException as exe:
                raise NoSuchElementException(
                    "Both primary and backup submit button selectors not found"
                ) from exe

    def _navigate_and_search(self, search_query: str) -> None:
        """
        Navigates to the search bar and performs a search based on the provided query.

        Args:
        - search_query (str): The search query to be used for searching items.

        Returns:
        - None
        """
        super().navigate_to_search_bar(self.BASE_URL, self.SEARCH_BAR_SELECTOR)
        super().search_for_query(
            search_query,
            self.SEARCH_BAR_SELECTOR,
            self.SUBMIT_BUTTON_SELECTOR,
        )

    @staticmethod
    def get_logger() -> logging.Logger:
        """
        Retrieves a static logger instance for the static methods in DepopScraper.

        This method configures a logger instance with a TimedRotatingFileHandler for log rotation.
        Log files are rotated daily, and a specified number of backup log files are retained.
        The logger is configured to log messages with DEBUG level and above.

        Returns:
            - logger (logging.Logger): A logger instance configured with a TimedRotatingFileHandler.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)

        # Create a TimedRotatingFileHandler for log rotation
        log_file = os.path.join(logs_dir, "scraper.log")
        handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=7
        )  # Rotate daily, keep 7 days' worth of logs
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger

    @staticmethod
    def get_page_sources_concurrently(urls):
        """
        Fetches page sources concurrently for a list of URLs using ThreadPoolExecutor.

        Args:
            - urls (list): List of URLs for which to fetch page sources.

        Returns:
            - dict: A dictionary where keys are URLs and values are the corresponding page sources.

        This method fetches page sources for a list of URLs concurrently using ThreadPoolExecutor.
        It handles potential errors during fetching, such as cancellations or exceptions, and
        provides logging for debugging purposes.

        Example:
            urls = ['https://example.com/page1', 'https://example.com/page2']
            page_sources = DepopScraper.get_page_sources_concurrently(urls)
        """

        page_sources = {}
        lock = threading.Lock()
        options = Options()
        options.add_argument("--log-level=3")

        logger = DepopScraper.get_logger()

        max_workers = 5
        backoff_delay = 2  # Initial backoff delay in seconds
        max_retries = 3

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    DepopScraper._fetch_update_page_source,
                    url,
                    page_sources,
                    lock,
                    options,
                    logger,
                    max_retries,
                    backoff_delay,
                )
                for url in urls
            ]
            try:
                for future in as_completed(futures):
                    try:
                        future.result()
                    except CancelledError:
                        logger.error("Task canceled:", exc_info=True)
                    except Exception as e:
                        logger.error(
                            f"Error fetching page source for {future.result()}: {e}",
                            exc_info=True,
                        )
                        future.cancel()
            except KeyboardInterrupt:
                # Handle keyboard interrupt at the outer level
                logger.error(
                    "KeyboardInterrupt: Cancelling remaining tasks and quitting WebDriver..."
                )
                for f in futures:
                    f.cancel()
            finally:
                for f in futures:
                    f.cancel()
        return page_sources

    @staticmethod
    def _fetch_update_page_source(
        url: str,
        page_sources,
        lock: threading.Lock,
        options: Options,
        logger: logging.Logger,
        max_retries: int,
        backoff_delay: int,
    ):
        """
        Fetches and updates the page source for a given URL.

        Args:
            url (str): The URL for which to fetch the page source.
            page_sources (dict): A dictionary to store the fetched page sources.
            lock (threading.Lock): A lock to ensure thread-safe access to shared resources.
            options (Options): Chrome options for configuring the WebDriver.
            logger (logging.Logger): Logger instance for logging messages.
            max_retries (int): Maximum number of retries in case of failure.
            backoff_delay (int): Initial backoff delay in seconds.

        This method fetches the page source for a given URL using a Chrome WebDriver.
        It retries a maximum number of times (max_retries) in case of failure.
        The backoff delay increases exponentially with each retry.
        After successfully fetching the page source, it updates the page_sources dictionary with the URL and its corresponding page source.

        """
        retries = 0
        while retries < max_retries:
            driver = DepopScraper.get_chrome_driver(options)
            # Catch various exceptions that might occur during navigation
            logger.info(f"Trying to access page_source for url {url}")
            try:
                driver.get(url)

                cookies_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, DepopScraper.COOKIE_CSS_SELECTOR)
                    )
                )
                ActionChains(driver).double_click(cookies_button).perform()

                with lock:
                    page_sources[url] = driver.page_source
                break  # Break out of the retry loop if successful
            except (WebDriverException, TimeoutException) as e:
                logger.error(f"Error fetching page source for '{url}': {e}")
                logger.debug(traceback.format_exc())
                retries += 1
                time.sleep(backoff_delay * retries)  # Increasing delay for retries
            finally:
                driver.quit()


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
