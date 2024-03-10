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
    def __init__(self, headless):
        options = self.configure_driver_options(headless)
        self.driver = self.get_chrome_driver(options)

    @abstractmethod
    def accept_cookies(self, cookies_id):
        """
        Accepts cookies on the website by locating and clicking the corresponding button.

        Args:
        - cookies_id: The ID of the cookies button.

        Returns:
        - None
        """
        try:
            cookies_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.ID, cookies_id))
            )
            ActionChains(self.driver).double_click(cookies_button).perform()
        except TimeoutException:
            print("Timeout occured while accepting cookies.")

    @staticmethod
    def get_search_query():
        """
        Prompt the user to enter a search query.

        Returns:
        - The search query entered by the user.
        """
        search_query = input("Enter your search query: ")
        return search_query

    def search_for_query(
        self, search_query, search_bar_css_selector, submit_button_css_selector
    ):
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
                search_query, search_bar_css_selector, submit_button_css_selector
            )
        else:
            search_query = self.get_search_query()
            self.type_search(
                search_query, search_bar_css_selector, submit_button_css_selector
            )

    def type_search(self, search, search_bar_css_selector, submit_button_css_selector):
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
    def dismiss_login_popup(self, timeout=2):
        """
        Dismisses the login popup within a specified timeout period.

        Args:
        - timeout: The maximum time to wait for the login popup.

        Returns:
        - None
        """
        pass

    def get_to_search_bar_to_search(
        self, search_bar_css_selector, timeout=2, dismiss_login_popup=False
    ):
        """
        Navigate to the search bar and interact with it to initiate a search.

        Args:
        - search_bar_css_selector: The CSS selector for the search bar.
        - timeout: The maximum time to wait for elements to be interactable.
        - dismiss_login_popup: Whether to dismiss the login popup if present. Defaults to False.

        Returns:
        - None
        """
        try:
            self.accept_cookies(self.driver)

            search_bar = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, search_bar_css_selector))
            )
            search_bar.click()

            if dismiss_login_popup:
                for _ in range(3):
                    try:
                        self.dismiss_login_popup(timeout=2)
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

    def wait_until_class_count_exceeds(self, class_name, min_count, timeout=10):
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
    def configure_driver_options(headless):
        """
        Configure the options for the Chrome WebDriver.

        Args:
        - headless: Boolean value indicating whether to run Chrome in headless mode.

        Returns:
        - options: The configured ChromeOptions instance.
        """
        options = Options()

        if sys.platform.startswith("win"):
            options.add_argument("--log-level=3")

        if headless:
            options.add_argument("--headless")

        options.add_experimental_option("detach", True)
        return options
    
    @abstractmethod
    def navigate_


def dismiss_login_popup(driver, timeout=5):
    """
    Dismisses the login popup within a specified timeout period.

    Args:
    - driver: The Selenium WebDriver instance.
    - timeout: The maximum time to wait for the login popup.

    Returns:
    - None
    """
    try:
        login_popup = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".ReactModal__Content.ReactModal__Content--after-open.modal.Modal-module__authenticationModal___g7Ufu._hasHeader",
                )
            )
        )

        ActionChains(driver).move_to_element(login_popup).pause(1).move_by_offset(
            250, 0
        ).pause(1).click()

        ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        WebDriverWait(driver, 15).until_not(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    "ReactModal__Overlay.ReactModal__Overlay--after-open.modal-overlay",
                )
            )
        )

    except TimeoutException:
        print("Login popup did not appear within the timeout.")


def navigate_to_search_page(driver, base_url):
    """
    Navigate to the search page of the website.

    Args:
    - driver: The Selenium WebDriver instance.
    - base_url: The base URL of the website.

    Returns:
    - None
    """
    driver.get(base_url)
    get_to_search_bar_to_search(driver)


def wait_for_page_load(driver, class_name, min_count):
    """
    Wait for the page to load completely.

    Args:
    - driver: The Selenium WebDriver instance.
    - class_name: The CSS class name of an element to wait for.
    - min_count: The minimum number of elements to wait for.

    Returns:
    - None
    """
    wait_until_class_count_exceeds(driver, class_name, min_count)
