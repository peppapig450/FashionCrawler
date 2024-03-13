import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
from soupsieve import select


def get_page_soup(driver):
    page_source = driver.page_source
    parser = etree.HTMLParser()
    return BeautifulSoup(page_source, "lxml", parser=parser)


def extract_item_post_times(soup):
    """
    Extracts the post times of items from the BeautifulSoup object.

    Args:
    - soup: The BeautifulSoup object containing the parsed HTML.

    Returns:
    - A list of post times.
    """
    return list(
        map(
            lambda time: time.text.split("\xa0ago")[0],
            select(".ListingAge-module__dateAgo___xmM8y", soup),
        )
    )


def extract_item_titles(soup):
    """
    Extracts the titles of items from the BeautifulSoup object.

    Args:
    - soup: The BeautifulSoup object containing the parsed HTML.

    Returns:
    - A list of item titles.
    """
    return list(
        map(
            lambda title: title.text,
            select(".ListingMetadata-module__title___Rsj55", soup),
        )
    )


def extract_item_designers(soup):
    """
    Extracts the designers of items from the BeautifulSoup object.

    Args:
    - soup: The BeautifulSoup object containing the parsed HTML.

    Returns:
    - A list of item designers.
    """
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
    """
    Extracts the sizes of items from the BeautifulSoup object.

    Args:
    - soup: The BeautifulSoup object containing the parsed HTML.

    Returns:
    - A list of item sizes.
    """
    return list(
        map(
            lambda size: size.text,
            select(".ListingMetadata-module__size___e9naE", soup),
        )
    )


def extract_item_prices(soup):
    """
    Extracts the prices of items from the BeautifulSoup object.

    Args:
    - soup: The BeautifulSoup object containing the parsed HTML.

    Returns:
    - A list of item prices.
    """
    return list(map(lambda price: price.text, select('[data-testid="Current"]', soup)))


def extract_item_listing_link(soup):
    """
    Extracts the listing links of items from the BeautifulSoup object.

    Args:
    - soup: The BeautifulSoup object containing the parsed HTML.

    Returns:
    - A list of item listing links.
    """
    return list(
        map(
            lambda listing_link: "https://grailed.com" + listing_link.get("href"),
            select("a.listing-item-link", soup),
        )
    )


def extract_data_to_dataframe(soup, data_extraction_functions):
    """
    Extract data from the BeautifulSoup object and store it in a Pandas DataFrame.

    Args:
    - soup: The BeautifulSoup object containing the parsed HTML.
    - data_extraction_functions: A dictionary mapping column names to functions that extract data for those columns.

    Returns:
    - df: The Pandas DataFrame containing the extracted data.
    """
    df = pd.DataFrame(columns=data_extraction_functions.keys())
    for column, func in data_extraction_functions.items():
        df[column] = func()
    return df
