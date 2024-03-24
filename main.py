from io_utils import IOUtils
from scraper import DepopScraper, GrailedScraper
from data_extraction import GrailedDataExtractor, DepopDataExtractor


# FIXME: problems with saving the output still isnt really efficient
# FIXME: also spawns some a random blank window
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


def extract_depop_data(extractor):
    depop_extractor = extractor

    item_links = depop_extractor.get_item_links()

    df = depop_extractor.extract_data_from_item_links(item_links)

    return df


def main():
    config = IOUtils.parse_args()
    search_query = config.get("search_query", "")

    # TODO: figure out how we're gonna run each websites scraper
    # create a dictionary ? list
    # or pass config with the enabled sites to run_scraper or another method and handle from there.
    # gscraper = GrailedScraper()  # This spawns empty window for some reason
    dscraper = DepopScraper()

    try:
        search_query = config.get("search_query", "")
        # gscraper.run_scraper(search_query)
        dscraper.run_scraper(search_query)
        extractor = DepopDataExtractor(driver=dscraper.driver)

        df = extract_depop_data(extractor)
        print(df)

        # extractor = GrailedDataExtractor(driver=gscraper.driver)
        # df = extractor.extract_data_to_dataframe()

        output_filename = config.get("output", search_query)
        # IOUtils.save_output_to_file(df, output_filename, config)

    finally:
        # dscraper.driver.quit()
        pass


if __name__ == "__main__":
    main()
