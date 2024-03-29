import sys
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class BaseScraper:
    def __init__(self):
        try:
            options = self.configure_driver_options()
            self.driver = self.get_chrome_driver(options)
        except Exception as e:
            print(f"An error occurred while initializing the ChromeDriver: {e}")
            raise

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
            print("Timeout occured while accepting cookies.")

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
        search_bar = self.driver.find_element(By.CSS_SELECTOR, search_bar_css_selector)
        submit_button = self.driver.find_element(
            By.CSS_SELECTOR, submit_button_css_selector
        )

        ActionChains(self.driver).click(search_bar).send_keys(search).click(
            submit_button
        ).perform()

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
        pass

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
        self, class_name: str, min_count: int, timeout=10
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
            print(
                f"Number of elements matching class '{class_name}' exceeded {min_count}."
            )
        except TimeoutException:
            print(
                f"Timeout occurred while waiting for class count to exceed {min_count}."
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
    def configure_driver_options():
        """
        Configure the options for the Chrome WebDriver.

        Returns:
        - options: The configured ChromeOptions instance.
        """
        options = Options()

        if sys.platform.startswith("win"):
            options.add_argument("--log-level=3")

        options.add_experimental_option("detach", True)
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
        pass


class GrailedScraper(BaseScraper):
    # Selectors for various elements
    LOGIN_POPUP_SELECTOR = ".ReactModal__Content.ReactModal__Content--after-open.modal.Modal-module__authenticationModal___g7Ufu._hasHeader"
    SEARCH_BAR_CSS_SELECTOR = "#header_search-input"
    SEARCH_BAR_SUBMIT_CSS_SELECTOR = "button[title='Submit']"
    COOKIES_CSS_SELECTOR = "#onetrust-accept-btn-handler"

    BASE_URL = "https://grailed.com"

    # Item related constants
    ITEM_CLASS_NAME = "feed-item"
    MIN_COUNT = 30

    # TODO: what if on init we pass the search query and neccessary things to each class and run the scrapers like that
    def __init__(self):
        super().__init__()

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
            print(f"Error interacting with search bar: {e}")
            self.driver.quit()

    def _dismiss_login_popup(self, timeout: int) -> None:
        """
        Dismisses the login popup within a specified timeout period.

        Args:
        - timeout (int): The maximum time to wait for the login popup.

        Returns:
        - None
        """

        # TODO: dont modularize this for now it's slower for some reason
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
            print("Login popup did not appear within the timeout.")


class DepopScraper(BaseScraper):
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

    def run_scraper(self, search_query) -> None:
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
        search_icon_css_selector: str,
        timeout=2,
    ) -> None:
        """
        Navigate to the search bar and interact with it to initiate a search.

        Args:
        - search_icon_css_seelctor: The magnifying glass you must click to get to search bar on depop.
        - search_bar_css_selector: The CSS selector for the search bar.
        - timeout: The maximum time to wait for elements to be interactable.

        Returns:
        - None
        """
        try:
            self.accept_cookies(self.COOKIE_CSS_SELECTOR)

            search_icon = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, search_icon_css_selector))
            )
            search_icon.click()

        except (
            NoSuchElementException,
            StaleElementReferenceException,
            TimeoutException,
        ) as e:
            print(f"Error interacting with search bar: {e}")
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
        except TimeoutException:
            try:
                submit_button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, self.BACKUP_SUBMIT_BUTTON_SELECTOR)
                    )
                )
            except TimeoutException:
                pass
                # raise NoSuchElementException("Both primary and backup submit button selectors not found")
                # TODO: add proper logging later

        submit_button.click()

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
