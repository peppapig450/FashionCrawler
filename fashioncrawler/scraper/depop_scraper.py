import threading
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed

from .base_scraper import *


class DepopScraper(BaseScraper):
    """
    Subclass of BaseScraper for scraping data from the Depop website.

    Attributes:
        COOKIE_CSS_SELECTOR (str):
            CSS selector for the cookies button.
        SEARCH_ICON_SELECTOR (str):
            CSS selector for the search icon.
        SEARCH_BAR_SELECTOR (str):
            CSS selector for the search bar.
        SUBMIT_BUTTON_SELECTOR (str):
            CSS selector for the submit button.
        BACKUP_SUBMIT_BUTTON_SELECTOR (str):
            CSS selector for the backup submit button.
        BASE_URL (str):
            Base URL of the Depop website.
        ITEM_CLASS_NAME (str):
            CSS class name for identifying items on the page.
        MIN_COUNT (int):
            Minimum count of items to wait for during page load.

    Methods:
        __init__(self, base_scraper):
            Initializes the Depop scraper with the base scraper object.
        run_scraper(self, search_query) -> None:
            Runs the Depop scraper to search for items based on the provided search query.
        get_to_search_bar_to_search(
            self,
            search_bar_css_selector: str,
            timeout=2
        ) -> None:
            Navigate to the search bar and interact with it to initiate a search.
        type_search(
            self,
            search: str,
            search_bar_css_selector: str,
            submit_button_css_selector: str
        ) -> None:
            Enter the provided search query into the search bar and submit the search.
        _navigate_and_search(self, search_query: str) -> None:
            Navigates to the search bar and performs a search based on the provided query.
        get_logger() -> logging.Logger:
            Retrieves a static logger instance for the static methods in DepopScraper.
        get_page_sources_concurrently(urls):
            Fetches page sources concurrently for a list of URLs using ThreadPoolExecutor.
        _fetch_update_page_source(
            url: str,
            page_sources,
            lock: threading.Lock,
            options: Options,
            logger: logging.Logger,
            max_retries: int,
            backoff_delay: int
        ):
            Fetches and updates the page source for a given URL.
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

    logger = logger_config.configure_logger()

    def __init__(self, config):
        super().__init__(config=config)

    def run_scraper(self, search_query: str) -> None:
        """
        Runs the Depop scraper to search for items based on the provided search query.

        Args:
        - search_query (str): The search query to be used for searching items.

        Returns:
        - None
        """
        self._navigate_and_search(search_query)
        super().wait_for_page_load(self.ITEM_CLASS_NAME)

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

    def _sort_by_newest(self, current_url: str):
        new_url = current_url + "&sort=newlyListed"
        print(current_url)
        self.driver.get(new_url)

    @staticmethod
    def get_static_chrome_driver(options):
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
        super().wait_until_class_count_exceeds(self.ITEM_CLASS_NAME, 30, timeout=3)
        self._sort_by_newest(self.driver.current_url)

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

        logger = DepopScraper.logger

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
            driver = DepopScraper.get_static_chrome_driver(options)
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
                logger.debug(f"Error fetching page source for '{url}': {e}")
                retries += 1
                time.sleep(backoff_delay * retries)  # Increasing delay for retries
            finally:
                driver.quit()
