#!/usr/bin/env python3
# Copyright 2024 Nicholas Brady. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from data_extraction import DepopDataExtractor, GrailedDataExtractor
from io_utils import IOUtils
from scraper import DepopScraper, GrailedScraper, BaseScraper


def run_scraper(scraper, extractor, search_query):
    """
    Run the specified scraper and extract data.

    Args:
    - scraper: The scraper object.
    - extractor: The data extractor object corresponding to the scraper.
    - search_query: The search query.

    Returns:
    - pd.DataFrame: Extracted data as a DataFrame.
    """

    scraper.run_scraper(search_query)
    df = extractor.extract_data_to_dataframe()
    return df


def main():
    config = IOUtils.parse_args()
    search_query = config.get("search_query", "")

    base_scraper = BaseScraper(config)

    scrapers = {
        "depop": (DepopScraper(base_scraper), DepopDataExtractor),
        "grailed": (GrailedScraper(base_scraper), GrailedDataExtractor),
    }

    dataframes = {
        "depop": None,
        "grailed": None,
    }

    enabled_sites = [site["name"] for site in config["sites"] if site["enabled"]]
    for site in enabled_sites:
        scraper, extractor_cls = scrapers.get(site)  # type: ignore
        if scraper:
            extractor = extractor_cls(driver=base_scraper.driver)
            df = run_scraper(scraper, extractor, search_query)
            if df is not None and not df.empty:
                dataframes[site] = df

    output_filename = str(config.get("output", search_query))
    IOUtils.handle_dataframe_output(dataframes, output_filename, config)


if __name__ == "__main__":
    main()
