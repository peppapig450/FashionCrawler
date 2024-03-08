#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys

import pandas as pd
import yaml
from bs4 import BeautifulSoup
from lxml import etree
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
from soupsieve import select
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


def generate_unique_filename(filename):
    """
    Generate a unique filename by appending a number to the base filename if it already exists.

    Args:
    - filename: The original filename to be checked and modified if necessary.

    Returns:
    - The unique filename.
    """
    base_filename, extension = os.path.splitext(filename)
    match = re.match(r"^(.*)_?(\d+)$", base_filename)
    if match:
        base_filename = match.group(1)
        count = int(match.group(2)) + 1
        new_filename = f"{base_filename}_{count}{extension}"
    else:
        new_filename = f"{base_filename}_1{extension}"

    if os.path.exists(new_filename):
        return generate_unique_filename(new_filename)
    else:
        return new_filename


def save_as_json(df, filename):
    with open(f"{filename}.json", "w", encoding="utf-8") as json_file:
        json.dump(df.to_dict(orient="records"), json_file, indent=4)


def save_as_csv(df, filename):
    df.to_csv(f"{filename}.csv", index=False)


def save_as_yaml(df, filename):
    with open(f"{filename}.yaml", "w", encoding="utf-8") as yaml_file:
        yaml.safe_dump(df.to_dict(orient="records"), yaml_file)


def accept_cookies(driver):
    try:
        cookies_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        ActionChains(driver).double_click(cookies_button).perform()
    except TimeoutException:
        print("Timeout occured")


def get_to_search_bar_to_search(driver, timeout=2):
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


def wait_until_class_count_exceeds(driver, class_name, min_count, timeout=10):
    def class_count_exceeds(driver):
        elements = driver.find_elements(By.CSS_SELECTOR, f".{class_name}")
        return len(elements) > min_count

    try:
        WebDriverWait(driver, timeout).until(class_count_exceeds)
        print(f"Number of elements matching class '{class_name}' exceeded {min_count}.")
    except TimeoutException:
        print(f"Timeout occurred while waiting for class count to exceed {min_count}.")


def extract_item_post_times(soup):
    return list(
        map(
            lambda time: time.text.split("\xa0ago")[0],
            select(".ListingAge-module__dateAgo___xmM8y", soup),
        )
    )


def extract_item_titles(soup):
    return list(
        map(
            lambda title: title.text,
            select(".ListingMetadata-module__title___Rsj55", soup),
        )
    )


def extract_item_designers(soup):
    return list(
        map(
            lambda designer: designer.text,
            select(
                "div.ListingMetadata-module__designerAndSize___lbEdw > p:first-child",
                soup,
            ),
        )
    )


def extract_item_sizes(soup):
    return list(
        map(
            lambda size: size.text,
            select(".ListingMetadata-module__size___e9naE", soup),
        )
    )


def extract_item_prices(soup):
    return list(map(lambda price: price.text, select('[data-testid="Current"]', soup)))


def extract_item_listing_link(soup):
    return list(
        map(
            lambda listing_link: "https://grailed.com" + listing_link.get("href"),
            select("a.listing-item-link", soup),
        )
    )


def main():
    args = parse_args()
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
    if args.search:
        type_search(driver, args.search)
    else:
        search_query = get_search_query()
        type_search(driver, search_query)

    wait_until_class_count_exceeds(driver, "feed-item", 30)
    page_source = driver.page_source
    parser = etree.HTMLParser()
    soup = BeautifulSoup(page_source, "lxml", parser=parser)

    data_extraction_functions = {
        "Posted Time": lambda: extract_item_post_times(soup),
        "Title": lambda: extract_item_titles(soup),
        "Designer": lambda: extract_item_designers(soup),
        "Size": lambda: extract_item_sizes(soup),
        "Price": lambda: extract_item_prices(soup),
        "Listing Link": lambda: extract_item_listing_link(soup),
    }

    df = pd.DataFrame(columns=data_extraction_functions.keys())  # type: ignore
    for column, func in data_extraction_functions.items():
        df[column] = func()

    driver.quit()

    output_filename = args.output if args.output else "output"

    if os.path.exists(output_filename):
        output_filename = generate_unique_filename(output_filename)

    if args.json:
        save_as_json(df, output_filename)
    elif args.csv:
        save_as_csv(df, output_filename)
    elif args.yaml:
        save_as_yaml(df, output_filename)
    else:
        print(df)


if __name__ == "__main__":
    main()
