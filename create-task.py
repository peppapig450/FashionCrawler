#!/usr/bin/env python3

import argparse
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

        # TODO maybe add if statements here

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


# rewrite this to use the click or argparse package -> DONE
# --search, -s flag | --json, -j flag, --csv, -c flag, --output, -o flag for file output
def get_search_query():
    search_query = input("Enter your search query: ")

    return search_query


def parse_args():
    parser = argparse.ArgumentParser(
        description="Grailed scraper for Final Create Task"
    )

    search_group = parser.add_argument_group("Search options")
    output_group = parser.add_argument_group("Output options")
    driver_group = parser.add_argument_group("Driver options")

    search_group.add_argument(
        "-s", "--search", help="Search query to scrape for", type=str
    )
    output_group.add_argument(
        "-j", "--json", help="Output as JSON", action="store_true"
    )
    output_group.add_argument("-c", "--csv", help="Output as CSV", action="store_true")
    output_group.add_argument(
        "-y", "--yaml", help="Output as YAML", action="store_true"
    )
    output_group.add_argument("-o", "--output", help="Output file name", type=str)
    driver_group.add_argument(
        "--headless", help="Run ChromeDriver in headless mode", action="store_true"
    )

    return parser.parse_args()


def accept_cookies(driver):
    try:
        cookies_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        ActionChains(driver).double_click(cookies_button).perform()
    except TimeoutException:
        print("Timeout occured")


def get_to_search_bar_to_search(driver, timeout=5):
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

    # check if popup is still there
    except (
        NoSuchElementException,
        StaleElementReferenceException,
        TimeoutException,
    ) as e:
        print(f"Error interacting with search bar: {e}")
        driver.quit()


# optimize this ?
def type_search(driver, search):
    search_bar = driver.find_element(By.CSS_SELECTOR, "#header_search-input")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[title='Submit']")

    ActionChains(driver).click(search_bar).send_keys(search).click(
        submit_button
    ).perform()


# TODO beautiful soup code (use lxml)


def main():
    args = parse_args()
    search_query = args.search

    options = Options()

    if sys.platform.startswith("win"):
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-gpu")

    if args.headless:
        options.add_argument("--headless")

    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        options=options, service=ChromeService(ChromeDriverManager().install())
    )

    base_url = "https://www.grailed.com"

    driver.get(base_url)
    get_to_search_bar_to_search(driver)

    # Use search query if provided otherwise ask for input
    if search_query:
        type_search(driver, search_query)
    else:
        search_query = get_search_query()
        type_search(driver, search_query)


if __name__ == "__main__":
    main()
