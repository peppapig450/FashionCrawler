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

    def __init__(self, headless):
        super().__init__(headless)

    def get_to_search_bar_to_search(self, search_bar_css_selector, timeout=2):
        """
        Navigate to the search bar and interact with it to initiate a search.

        Args:
        - search_bar_css_selector: The CSS selector for the search bar.
        - timeout: The maximum time to wait for elements to be interactable.

        Returns:
        - None
        """
        try:
            self.accept_cookies(self.driver)

            search_bar = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, search_bar_css_selector))
            )
            search_bar.click()

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

    def dismiss_login_popup(self, timeout=5):
        """
        Dismisses the login popup within a specified timeout period.

        Args:
        - timeout: The maximum time to wait for the login popup.

        Returns:
        - None
        """
        try:
            login_popup = self._wait_for_login_popup(timeout)
            self._close_login_popup(login_popup)
            self._wait_for_login_popup_to_disappear()

        except TimeoutException:
            print("Login popup did not appear within the timeout.")

    def _wait_for_login_popup(self, timeout):
        """
        Wait for the login popup to appear.

        Args:
            timeout (int): The maximum time to wait for the login popup.

        Returns:
            WebElement: The login popup element.
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.LOGIN_POPUP_SELECTOR))
        )

    def _close_login_popup(self, login_popup):
        """
        Close the login popup.

        Args:
            login_popup (WebElement): The login popup element.

        Returns:
            None
        """
        ActionChains(self.driver).move_to_element(login_popup).pause(1).move_by_offset(
            250, 0
        ).pause(1).click().pause(1).send_keys(Keys.ESCAPE).perform()

    def _wait_for_login_popup_to_disappear(self):
        """
        Wait for the login popup to disappear.

        Returns:
            None
        """
        return WebDriverWait(self.driver, 15).until_not(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    "ReactModal__Overlay.ReactModal__Overlay--after-open.modal-overlay",
                )
            )
        )
