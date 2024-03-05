from selenium import webdriver
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.by import By

import sys


def dismiss_login_popup(driver, timeout=5):
    try:
        login_popup = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ReactModal__Overlay ReactModal__Overlay--after-open modal-overlay"))
        )

       # ActionChains(driver).move_to_element(login_popup).move_by_offset(0, 300).click().perform()
        script = """
        var elementToRemove = document.querySelector('.ReactModalPortal');
        elementToRemove && elementToRemove.remove();
        """
        driver.execute_script(script)

        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "ReactModal__Overlay.ReactModal__Overlay--after-open.modal-overlay"))
        )


    except TimeoutException:
        print("Login popup did not appear within the timeout.")


def get_search_query():
    if len(sys.argv > 1):
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


def get_to_search_bar_to_search(driver, timeout=5):

    try:
        wait = WebDriverWait(driver, timeout)

        accept_cookies(driver)

        # driver.execute_script("document.querySelector('.ReactModal__Overlay').style.display = 'none';")
        #  ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        search_bar = driver.find_element(By.CSS_SELECTOR, "#header_search-input")
        search_bar.click()

    # check if popup is still there
    except (NoSuchElementException, StaleElementReferenceException) as e:
        print(f"Error interacting with element: {e}")
        driver.quit()
    except TimeoutException:
        print("Element not found within timeout!")
        driver.quit()


def type_search(search):
    search_bar = driver.find_element(By.CSS_SELECTOR, "#header_search-input")
    ActionChains(driver).send_keys_to_element(search_bar, search).perform()


if __name__ == "__main__":
    options = Options()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        options=options, service=ChromeService(ChromeDriverManager().install())
    )
    base_url = "https://www.grailed.com"

    driver.get(base_url)
    get_to_search_bar_to_search(driver)
    search_query = get_search_query()
