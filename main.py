import asyncio

from aiohttp import ClientSession
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


async def test_depop_item_links(DepopDataExtractor, driver):
    depop_extractor = DepopDataExtractor

    async with ClientSession() as session:
        item_links = await depop_extractor.extract_item_links(session, driver)

        return item_links


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
        # links = asyncio.run(test_depop_item_links(extractor, dscraper.driver))
        links = extractor.get_item_links()
        print(links)

        # extractor = GrailedDataExtractor(driver=gscraper.driver)
        # df = extractor.extract_data_to_dataframe()

        output_filename = config.get("output", search_query)
        # IOUtils.save_output_to_file(df, output_filename, config)

    finally:
        dscraper.driver.quit()
        pass


if __name__ == "__main__":
    main()
