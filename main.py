from data_extraction import (
    extract_data_to_dataframe,
    extract_item_designers,
    extract_item_listing_link,
    extract_item_post_times,
    extract_item_prices,
    extract_item_sizes,
    extract_item_titles,
    get_page_soup,
)
from io_utils import generate_unique_filename, parse_args, save_output_to_file
from scraping import (
    configure_driver_options,
    dismiss_login_popup,
    get_chrome_driver,
    get_search_query,
    navigate_to_search_page,
    search_for_query,
    wait_for_page_load,
)


def main():
    args = parse_args()
    options = configure_driver_options(args.headless)

    driver = get_chrome_driver(options)

    try:
        base_url = "https://grailed.com"
        navigate_to_search_page(driver, base_url)

        search_query = args.search if args.search else get_search_query()
        search_for_query(driver, search_query)

        wait_for_page_load(driver, "feed-item", min_count=30)

        soup = get_page_soup(driver)

        data_extraction_functions = {
            "Posted Time": lambda: extract_item_post_times(soup),
            "Title": lambda: extract_item_titles(soup),
            "Designer": lambda: extract_item_designers(soup),
            "Size": lambda: extract_item_sizes(soup),
            "Price": lambda: extract_item_prices(soup),
            "Listing Link": lambda: extract_item_listing_link(soup),
        }

        df = extract_data_to_dataframe(soup, data_extraction_functions)

        output_filename = generate_unique_filename(
            args.output if args.output else search_query.replace(" ", "_")
        )

        save_output_to_file(df, output_filename, args)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
