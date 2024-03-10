import sys
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


def get_search_query():
    """
    Prompt the user to enter a search query.

    Returns:
    - The search query entered by the user.
    """
    search_query = input("Enter your search query: ")
    return search_query


def accept_cookies(driver):
    """
    Accepts cookies on the website by locating and clicking the corresponding button.

    Args:
    - driver: The Selenium WebDriver instance.

    Returns:
    - None
    """
    try:
        cookies_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        ActionChains(driver).double_click(cookies_button).perform()
    except TimeoutException:
        print("Timeout occurred while accepting cookies.")


def get_to_search_bar_to_search(driver, timeout=2):
    """
    Navigate to the search bar and interact with it to initiate a search.

    Args:
    - driver: The Selenium WebDriver instance.
    - timeout: The maximum time to wait for elements to be interactable.

    Returns:
    - None
    """
    try:
        accept_cookies(driver)

        search_bar = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#header_search-input"))
        )
        search_bar.click()

        for _ in range(3):
            try:
                dismiss_login_popup(driver, timeout=2)
                break
            except TimeoutException:
                pass

    except (
        NoSuchElementException,
        StaleElementReferenceException,
        TimeoutException,
    ) as e:
        print(f"Error interacting with search bar: {e}")
        driver.quit()


def type_search(driver, search):
    """
    Enter the provided search query into the search bar and submit the search.

    Args:
    - driver: The Selenium WebDriver instance.
    - search: The search query to be entered into the search bar.

    Returns:
    - None
    """
    search_bar = driver.find_element(By.CSS_SELECTOR, "#header_search-input")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[title='Submit']")

    ActionChains(driver).click(search_bar).send_keys(search).click(
        submit_button
    ).perform()


def wait_until_class_count_exceeds(driver, class_name, min_count, timeout=10):
    """
    Wait until the number of elements matching the specified class exceeds a minimum count.

    Args:
    - driver: The Selenium WebDriver instance.
    - class_name: The CSS class name of the elements to count.
    - min_count: The minimum number of elements to wait for.
    - timeout: The maximum time to wait for the condition to be met.

    Returns:
    - None
    """

    def class_count_exceeds(driver):
        elements = driver.find_elements(By.CSS_SELECTOR, f".{class_name}")
        return len(elements) > min_count

    try:
        WebDriverWait(driver, timeout).until(class_count_exceeds)
        print(f"Number of elements matching class '{class_name}' exceeded {min_count}.")
    except TimeoutException:
        print(f"Timeout occurred while waiting for class count to exceed {min_count}.")


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


def search_for_query(driver, search_query):
    """
    Perform a search with the provided query.

    Args:
    - driver: The Selenium WebDriver instance.
    - search_query: The search query to be performed.

    Returns:
    - None
    """
    if search_query:
        type_search(driver, search_query)
    else:
        search_query = get_search_query()
        type_search(driver, search_query)


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
