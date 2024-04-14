from .base_scraper import *


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

    def __init__(self, config):
        super().__init__(config=config)

    def run_scraper(self, search_query) -> None:
        """
        Runs the Grailed scraper to search for items based on the provided search query.

        Args:
        - search_query (str): The search query to be used for searching items.

        Returns:
        - None
        """
        self._navigate_and_search(search_query)
        super().wait_for_page_load(self.ITEM_CLASS_NAME)
        self.logger.debug("Running Grailed Scraper.")

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
