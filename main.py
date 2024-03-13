from io_utils import IOUtils
from scraper import GrailedScraper
from data_extraction import GrailedDataExtractor


def main():
    config = IOUtils.parse_args()

    scraper = GrailedScraper(headless=config["headless"])

    try:
        search_query = config.get("search_query", "")
        scraper.run_grailed_scraper(search_query)
        extractor = GrailedDataExtractor(driver=scraper.driver)
        df = extractor.extract_data_to_function()

        output_filename = config.get("output", "output")
        IOUtils.save_output_to_file(df, output_filename, config)

    finally:
        scraper.driver.quit()


if __name__ == "__main__":
    main()
