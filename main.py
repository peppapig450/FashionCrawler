from re import search
from io_utils import IOUtils
from scraper import DepopScraper, GrailedScraper
from data_extraction import GrailedDataExtractor


def run_scraper(scraper, extractor, search_query, output_filename, config):
    """
    Run the specified scraper, extract data, and save it to a file.

    Args:
    - scraper: The scraper object.
    - extractor: The data extractor object corresponding to the scraper.
    - search_query: The search query.
    - output_filename: The output filename.
    - config: Configuration settings.

    Returns:
    - None
    """
    try:
        scraper.run_scraper(search_query)
        df = extractor.extract_data_to_dataframe()
        IOUtils.save_output_to_file(df, output_filename, config)
    finally:
        scraper.driver.quit()


def main():
    config = IOUtils.parse_args()
    search_query = config.get("search_query", "")

    # TODO: figure out how we're gonna run each websites scraper
    grailed_scraper = GrailedScraper(headless=config["headless"])
    depop_scraper = DepopScraper(headless=config["headless"])

    # not perfect way to do this but its a start I guess.
    run_scraper(
        grailed_scraper,
        GrailedDataExtractor(driver=grailed_scraper.driver),
        search_query,
        config.get("output", f"{search_query}_grailed"),
        config,
    )


if __name__ == "__main__":
    main()
