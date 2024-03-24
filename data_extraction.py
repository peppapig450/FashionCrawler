import time
from typing import List

import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
from soupsieve import select


class BaseDataExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.page_source = driver.page_source
        self.soup = self.get_page_soup()

    def get_page_soup(self):
        parser = etree.HTMLParser()
        return BeautifulSoup(self.page_source, "lxml", parser=parser)

    def extract_data_to_dataframe(self, data_extraction_functions):
        """
        Extract data from the BeautifulSoup object and store it in a Pandas DataFrame.

        Args:
        - data_extraction_functions: A dictionary mapping column names to functions that extract data for those columns.

        Returns:
        - df: The Pandas DataFrame containing the extracted data.
        """
        df = pd.DataFrame(columns=data_extraction_functions.keys())
        for column, func in data_extraction_functions.items():
            df[column] = func()
        return df


class GrailedDataExtractor(BaseDataExtractor):

    def extract_data_to_dataframe(self):
        data_extraction_functions = {
            "Posted Time": self.extract_item_post_times,
            "Title": self.extract_item_titles,
            "Designer": self.extract_item_designers,
            "Size": self.extract_item_sizes,
            "Price": self.extract_item_prices,
            "Listing Link": self.extract_item_listing_link,
        }
        return super().extract_data_to_dataframe(data_extraction_functions)

    def extract_item_post_times(self):
        return list(
            map(
                lambda time: time.text.split("\xa0ago")[0],
                select(".ListingAge-module__dateAgo___xmM8y", self.soup),
            )
        )

    def extract_item_titles(self):
        return list(
            map(
                lambda title: title.text,
                select(".ListingMetadata-module__title___Rsj55", self.soup),
            )
        )

    def extract_item_designers(self):
        return list(
            map(
                lambda designer: designer.text,
                select(
                    "div.ListingMetadata-module__designerAndSize___lbEdw > p:first-child",
                    self.soup,
                ),
            )
        )

    def extract_item_sizes(self):
        return list(
            map(
                lambda size: size.text,
                select(".ListingMetadata-module__size___e9naE", self.soup),
            )
        )

    def extract_item_prices(self):
        """
        Extracts the prices of items from the BeautifulSoup object.

        Args:
        - soup: The BeautifulSoup object containing the parsed HTML.

        Returns:
        - A list of item prices.
        """
        return list(
            map(lambda price: price.text, select('[data-testid="Current"]', self.soup))
        )

    def extract_item_listing_link(self):
        """
        Extracts the listing links of items from the BeautifulSoup object.

        Args:
        - soup: The BeautifulSoup object containing the parsed HTML.

        Returns:
        - A list of item listing links.
        """
        return list(
            map(
                lambda listing_link: f"https://grailed.com{listing_link.get('href')}",
                select("a.listing-item-link", self.soup),
            )
        )


class DepopDataExtractor(BaseDataExtractor):
    def __init__(self, driver):
        self.driver = driver

    # get the soup instance we're gonna use to scrape the links off of
    def get_page_soup(self):
        parser = etree.HTMLParser
        return BeautifulSoup(self.driver.page_source, "lxml", parser=parser)

    def get_item_links(self):
        soup = self.get_page_soup()

        links = list(
            map(
                lambda item_link: f"https://depop.com{item_link.get('href')}",
                select(".styles__ProductCard-sc-4aad5806-4.ffvUlI", soup),
            )
        )[:40]

        return links

    def extract_data_from_item_links(self, links):
        all_data = []

        for link in links:
            self.driver.get(link)
            time.sleep(1)

            self.soup = self.get_page_soup()
            data = self.extract_data(self.driver.current_url)
            all_data.append(data)

        return pd.DataFrame(all_data)

    def extract_data(self, url):
        data_extraction_functions = {
            "Title": self.extract_item_title,
            "Price": self.extract_item_price,
            "Seller": self.extract_item_seller,
            "Condition": self.extract_item_condition,
            "Description": self.extract_item_description,
            "Listing Age": self.extract_item_time_posted,
            "Link": lambda: url,
        }

        extracted_data = {}
        for column, func in data_extraction_functions.items():
            extracted_data[column] = func()

        return extracted_data

    def extract_item_title(self):
        return list(
            title.text.strip()
            for title in select(
                ".ProductDetailsSticky-styles__DesktopKeyProductInfo-sc-81fc4a15-9.epoVmq  h1",
                self.soup,
            )
        )

    def extract_item_price(self) -> List[str]:
        price_elements = select(
            ".ProductDetailsSticky-styles__StyledProductPrice-sc-81fc4a15-4.dVAZDx  div  p",
            self.soup,
        )
        prices = []

        for price_element in price_elements:
            aria_label = price_element.get("aria-label", "")
            price_text = price_element.text.strip()

            if "Discounted price" == aria_label:
                prices.clear()
                prices.append(price_text)
                break
            else:
                prices.append(price_text)

        return prices

    def extract_item_seller(self):
        seller_element = select(
            "a.sc-eDnWTT.styles__Username-sc-f040d783-3.fRxqiS.WZqly", self.soup
        )
        if seller_element:
            return [seller_element[0].text.strip()]
        else:
            return []

    def extract_item_description(self):
        return list(
            description.text.strip()
            for description in select(
                ".styles__Container-sc-d367c36f-0.ffwMQV  p",
                self.soup,
            )
        )

    def extract_item_condition(self):
        attribute_elements = select(
            "div.ProductAttributes-styles__Attributes-sc-303d66c3-1.dIfGXO p", self.soup
        )
        conditions = []

        if len(attribute_elements) >= 3:
            conditions.append(attribute_elements[1].text.strip())
        elif len(attribute_elements) <= 2:
            conditions.append(attribute_elements[0].text.strip())

        return conditions

    def extract_item_size(self):
        attribute_elements = select(
            "div.ProductAttributes-styles__Attributes-sc-303d66c3-1.dIfGXO p", self.soup
        )
        size = []

        if len(attribute_elements) >= 3:
            size.append(attribute_elements[0].text.strip())

        return size

    def extract_item_time_posted(self):
        return list(
            time_posted.text.replace("Listed", "").strip()
            for time_posted in select(
                "time.sc-eDnWTT.styles__Time-sc-630c0aef-0.gpa-dDQ.bgyRJa.styles__StyledPostTime-sc-2b987745-4.fofwdp",
                self.soup,
            )
        )
