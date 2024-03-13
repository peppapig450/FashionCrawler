from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from scraper import BaseScraper


class GrailedScraper(BaseScraper):
    LOGIN_POPUP_SELECTOR = ".ReactModal__Content.ReactModal__Content--after-open.modal.Modal-module__authenticationModal___g7Ufu._hasHeader"
    BASE_URL = "https://grailed.com"
    SEARCH_BAR_CSS_SELECTOR = "#header_search-input"
    SEARCH_BAR_SUBMIT_CSS_SELECTOR = "button[title='Submit']"
    ITEM_CLASS_NAME = "feed-item"
    MIN_COUNT = 30
    COOKIES_ID = "onetrust-accept-btn-handler"

    def __init__(self, headless):
        super().__init__(headless)

    def run_grailed_scraper(self, search_query: str) -> None:
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
            self.accept_cookies(self.COOKIES_ID)

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
                        ".ReactModal__Content.ReactModal__Content--after-open.modal.Modal-module__authenticationModal___g7Ufu._hasHeader",
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
                        By.CLASS_NAME,
                        "ReactModal__Overlay.ReactModal__Overlay--after-open.modal-overlay",
                    )
                )
            )

        except TimeoutException:
            print("Login popup did not appear within the timeout.")
