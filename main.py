import pandas as pd

from data_extraction import DepopDataExtractor, GrailedDataExtractor
from io_utils import IOUtils
from scraper import DepopScraper, GrailedScraper, BaseScraper


# FIXME: problems with saving the output still isnt really efficient
def run_scraper(scraper, extractor, search_query, config):
    """
    Run the specified scraper, extract data, and save it to a file.

    Args:
    - scraper: The scraper object.
    - extractor: The data extractor object corresponding to the scraper.
    - search_query: The search query.
    - config: Configuration settings.

    Returns:
    - pd.DataFrame: Extracted data as a DataFrame.
    """
    scraper.run_scraper(search_query)
    df = extractor.extract_data_to_dataframe()
    return df


def main():
    config = IOUtils.parse_args()
    search_query = config.get("search_query", "")

    base_scraper = BaseScraper()

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
            df = run_scraper(scraper, extractor, search_query, config)
            if df is not None and not df.empty:
                dataframes[site] = df

    output_filename = str(config.get("output", search_query))
    IOUtils.handle_dataframe_output(dataframes, output_filename, config)


if __name__ == "__main__":
    main()
