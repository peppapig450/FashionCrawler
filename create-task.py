import sys

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def dismiss_login_popup(driver, timeout=5):
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


def get_search_query():
    if len(sys.argv) > 1:
        search_query = sys.argv[1]
    else:
        search_query = input("Enter your search query: ")

    return search_query


def accept_cookies(driver):
    try:
        cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        ActionChains(driver).double_click(cookies_button).perform()
    except TimeoutException:
        print("Timeout occured")


# maybe rewrite the search bar logic
def get_to_search_bar_to_search(driver, timeout=5):

    try:
        accept_cookies(driver)

        search_bar = driver.find_element(By.CSS_SELECTOR, "#header_search-input")
        search_bar.click()

        dismiss_login_popup(driver)

    # check if popup is still there
    except (NoSuchElementException, StaleElementReferenceException) as e:
        print(f"Error interacting with element: {e}")
        driver.quit()
    except TimeoutException:
        print("Element not found within timeout!")
        driver.quit()


def type_search(search):
    search_bar = driver.find_element(By.CSS_SELECTOR, "#header_search-input")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[title='Submit']")

    ActionChains(driver).click(search_bar).send_keys(search).click(
        submit_button
    ).perform()


# beautiful soup code
if __name__ == "__main__":
    options = Options()
    # windows specific options
    if sys.platform.startswith("win"):
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-gpu")

    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        options=options, service=ChromeService(ChromeDriverManager().install())
    )
    base_url = "https://www.grailed.com"

    driver.get(base_url)
    get_to_search_bar_to_search(driver)
    search_query = get_search_query()
    type_search(search_query)
