from io_utils import IOUtils
from scraper import GrailedScraper


def main():
    config = IOUtils.parse_args()

    scraper = GrailedScraper(headless=config["headless"])

    try:
        search_query = config.get("search_query", "")
        scraper.run_grailed_scraper(search_query)
        # write the parameters for search_for_query in GrailedScraper class
    finally:
        scraper.driver.quit()


if __name__ == "__main__":
    main()
