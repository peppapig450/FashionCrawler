"""
IO Utils Module
=======================

This module provides utility functions for handling input/output operations and command-line argument parsing.

Copyright 2024 Nick. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Classes:
- IOUtils: A utility class for handling input/output operations and command-line argument parsing.

Methods:
- parse_args(): Parse command-line arguments and configuration settings.
- _load_config(config_file): Load configuration settings from a YAML file.
- _enable_sites(config, site_names): Enable specific sites in the configuration.
- _disable_sites(config, site_names): Disable specific sites in the configuration.
- _get_output_format(args): Determine the output format based on command-line arguments.
- _update_config_with_options(config, args): Update the configuration with command-line options.
- handle_dataframe_output(dataframes, output_filename, config): Save DataFrames to a file based on the specified output format.
- _save_as_json(dataframes, filename): Save DataFrames to a JSON file.
- _save_as_csv(dataframes, filename): Save DataFrames to a CSV file.
- _save_as_yaml(dataframes, filename): Save DataFrames to a YAML file.
- _print_out_dataframes(dataframes): Print out the DataFrames.
"""

import argparse
import json
import os
import time
from threading import Thread
from typing import List

import yaml
from weasyprint import HTML, CSS


# TODO: Explore class methods for using filename and context
class IOUtils:
    """
    A utility class for handling input/output operations and command-line argument parsing.

    Methods:
    - parse_args(): Parse command-line arguments and configuration settings.
    - _load_config(config_file): Load configuration settings from a YAML file.
    - _enable_sites(config, site_names): Enable specific sites in the configuration.
    - _disable_sites(config, site_names): Disable specific sites in the configuration.
    - _get_output_format(args): Determine the output format based on command-line arguments.
    - _update_config_with_options(config, args): Update the configuration with command-line options.
    - handle_dataframe_output(dataframes, output_filename, config): Save DataFrames to a file based on the specified output format.
    - _save_as_json(dataframes, filename): Save DataFrames to a JSON file.
    - _save_as_csv(dataframes, filename): Save DataFrames to a CSV file.
    - _save_as_yaml(dataframes, filename): Save DataFrames to a YAML file.
    - _print_out_dataframes(dataframes): Print out the DataFrames.
    """

    @staticmethod
    def parse_args():
        """
        Parse command-line arguments using the argparse module.

        Returns:
            dict: Configuration settings based on command-line arguments and config file.
        """
        parser = argparse.ArgumentParser(
            description="Fashion Crawler: A web scraper for various fashion marketplace sites."
        )

        # Site selection group to override config settings
        site_group = parser.add_argument_group(
            "Site selection",
            "By default all are enabled or it uses the sites in config.yaml",
        )

        site_group.add_argument(
            "--enable-site",
            help="Enable a specific site(s) (comma-seperated list)",
            type=str,
            default="",
        )

        site_group.add_argument(
            "--disable-site",
            help="Disable a specific site(s) (comma-seperated list)",
            type=str,
            default="",
        )

        # Search options group
        search_group = parser.add_argument_group("Search options")
        search_group.add_argument(
            "-s", "--search", help="Search query to scrape for", type=str
        )

        # TODO: multiple output options

        # Output options group
        output_group = parser.add_argument_group(
            "Output options",
            "If no option is specified it prints table on command line",
        )
        output_group.add_argument(
            "-j", "--json", help="Output as JSON", action="store_true"
        )
        output_group.add_argument(
            "-c", "--csv", help="Output as CSV", action="store_true"
        )
        output_group.add_argument(
            "-y", "--yaml", help="Output as YAML", action="store_true"
        )
        output_group.add_argument(
            "--html", help="Output HTMl using jinja2", action="store_true"
        )
        output_group.add_argument("--pdf", help="Output a PDF", action="store_true")
        output_group.add_argument(
            "-o", "--output", help="Ouput file name (without extension)", type=str
        )
        output_group.add_argument("--output-dir", help="Output directory", type=str)

        output_group.add_argument(
            "--output-formats",
            nargs="+",
            choices=["json", "csv", "yaml", "html", "pdf", "print"],
            help="List of desired output formats (--output-format jsv csv)",
        )

        # Driver options
        driver_group = parser.add_argument_group("Driver options")
        driver_group.add_argument(
            "--headless",
            help="Run WebDriver in headless mode (WIP)",
            action="store_true",
        )

        scraping_group = parser.add_argument_group("Scraping options")
        scraping_group.add_argument(
            "--count", help="Specify the amount of items to scrape", type=int
        )

        args = parser.parse_args()

        # Load configuration from YAML file
        config = IOUtils._load_config("fashioncrawler/resources/config/config.yaml")

        # update config based on command line args
        if args.enable_site:
            IOUtils._enable_sites(config, args.enable_site.split(","))

        if args.disable_site:
            IOUtils._disable_sites(config, args.disable_site.split(","))

        IOUtils._update_config_with_options(config, args)

        return config

    @staticmethod
    def _load_config(config_file):
        """
        Load configuration settings from a YAML file.
        If no config file is present, enable all sites by default.

        Args:
            config_file (str): Path to the configuration file.

        Returns:
            dict: Configuration settings loaded from the file.
        """
        config_file = os.path.abspath(config_file)
        try:
            with open(config_file, "r", encoding="UTF-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            # If config file not found enable all sites by default (set all but grailed to false until they're completed)
            config = {
                "sites": [
                    {"name": "grailed", "enabled": True},
                    {"name": "depop", "enabled": True},
                    {"name": "goat", "enabled": False},
                    {"name": "stockx", "enabled": False},
                ]
            }

        return config

    @staticmethod
    def _enable_sites(config, site_names):
        """
        Enable specific sites in the configuration.

        Args:
            config (dict): Configuration settings.
            site_names (list): List of site names to enable.
        """
        list(
            map(
                lambda site: (
                    site.update({"enabled": True})
                    if site["name"] in site_names
                    else None
                ),
                config["sites"],
            )
        )

    @staticmethod
    def _disable_sites(config, site_names):
        """
        Disable specific sites in the configuration.

        Args:
            config (dict): Configuration settings.
            site_names (list): List of site names to disable.
        """
        list(
            map(
                lambda site: (
                    site.update({"enabled": False})
                    if site["name"] in site_names
                    else None
                ),
                config["sites"],
            )
        )

    # TODO: ability to output multiple formats
    @staticmethod
    def _get_output_format(args) -> List[str]:
        """
        Determine the output format based on command-line arguments.

        Args:
            args (Namespace): Parsed command-line arguments.

        Returns:
            formats (list) or None: Output formats (json, csv, yaml, html, pdf or print)
        """
        formats = []
        if args.output_formats:
            formats.extend(args.output_formats)
        else:
            if args.json:
                formats.append("json")
            if args.csv:
                formats.append("csv")
            if args.yaml:
                formats.append("yaml")
            if args.html:
                formats.append("html")
            if args.pdf:
                formats.append("pdf")
        return formats if formats else ["print"]

    # TODO: support for multiple output formats use append in argparse and add to list with dictionary
    @staticmethod
    def _update_config_with_options(config, args):
        """
        Update the configuration with search, output, and driver options from command-line arguments.

        Args:
            config (dict): Configuration settings.
            args (Namespace): Parsed command-line arguments.
        """
        config["search_query"] = args.search
        config["output_formats"] = list(set(IOUtils._get_output_format(args)))
        config["headless"] = args.headless

        if args.output_dir:
            config["output_directory"] = args.output_dir

        if args.count:
            config["count"] = args.count

    @classmethod
    def handle_dataframe_output(
        cls, dataframes: dict, config, enabled_sites, search_query, output_filename
    ):
        """
        Save DataFrames to a file based on the specified output format.

        Args:
            dataframes: A dictionary containing DataFrames to be saved.
            output_filename: The name of the output file.
            config: The configuration settings containing information about the output format.

        Returns:
            None
        """

        output_directory = config.get("output_directory", "")

        output_filename = output_filename.replace(" ", "_")
        if output_directory:
            os.makedirs(output_directory, exist_ok=True)
            output_filename = os.path.join(output_directory, output_filename)

        format_handlers = {
            "json": IOUtils._save_as_json,
            "csv": IOUtils._save_as_csv,
            "yaml": IOUtils._save_as_yaml,
            "print": IOUtils._print_out_dataframes,
            "pdf": IOUtils._save_as_pdf,
            "html": IOUtils.render_and_serve_html,
        }

        for output_format in config["output_formats"]:
            if output_format in ("html", "pdf"):
                # TODO: MAYBE: seperate this into another function
                from .html_renderer import render_and_serve
                from .utils import Utils

                context = Utils.create_context_dict(
                    dataframes=dataframes,
                    search_query=search_query,
                    sites=enabled_sites,
                    subtemplates=config["subtemplates"],
                    output_format=output_format,
                )
                if output_format == "pdf":
                    format_handlers[output_format](context, output_filename)
                else:
                    format_handlers[output_format](context, render_and_serve)
            elif output_format == "print":
                format_handlers[output_format](dataframes)
            else:
                format_handlers[output_format](dataframes, output_filename)

    @staticmethod
    def _save_as_json(dataframes: dict, filename: str):
        """
        Save DataFrames to a single JSON file.

        Args:
            dataframes: A dictionary containing the Pandas DataFrames to be saved.
            filename: The name of the output file.

        Returns:
            None
        """
        with open(f"{filename}.json", "w", encoding="utf-8") as json_file:
            json.dump(
                {
                    name: df.to_dict("records")
                    for name, df in dataframes.items()
                    if df is not None
                },
                json_file,
                indent=4,
            )

    # TODO: fix this
    @staticmethod
    def _save_as_csv(dataframes: dict, filename: str):
        """
        Save DataFrames to a CSV file.

        Args:
            dataframes: A dictionary containing the Pandas DataFrames to be saved.
            filename: The name of the output file.

        Returns:
            None
        """
        with open(f"{filename}.csv", "w", encoding="UTF-8") as csv_file:
            for df in dataframes.values():
                if df is not None:
                    df.to_csv(csv_file, index=False)

    @staticmethod
    def _save_as_yaml(dataframes: dict, filename: str):
        """
        Save DataFrames to a YAML file.

        Args:
            dataframes: A dictionary containing the Pandas DataFrames to be saved.
            filename: The name of the output file.

        Returns:
            None
        """
        combined_data = {name: df.to_dict("records") for name, df in dataframes.items()}

        with open(f"{filename}.yaml", "w", encoding="utf-8") as yaml_file:
            yaml.safe_dump(combined_data, yaml_file)

    @staticmethod
    def _print_out_dataframes(dataframes: dict):
        """
        Print out the DataFrames.

        Args:
            dataframes: A dictionary containing the Pandas DataFrames.

        Returns:
            None
        """
        for name, df in dataframes.items():
            print(f"{name}\n", df)

    @classmethod
    def _save_as_pdf(cls, context, filename):
        from .html_renderer import render_and_serve

        server = render_and_serve(context)
        server_thread = Thread(target=server.serve_forever)
        server_thread.daemon = (
            True  # Allow the program to exit when main thread finishes
        )
        server_thread.start()

        time.sleep(5)
        css_file_path = "fashioncrawler/resources/templates/style.css"
        with open(css_file_path) as f:
            css_content = f.read()

        try:
            url = f"http://{server.server_address[0]}:{server.server_address[1]}"
            HTML(url=url).write_pdf(
                f"{filename}.pdf", stylesheets=[CSS(string=css_content)]
            )
        finally:
            server.shutdown()

    @staticmethod
    def render_and_serve_html(context, renderer):
        try:
            server = renderer(context)
            print(
                f"Server running at http://{server.server_address[0]}:{server.server_address[1]}/"
            )
            server.serve_forever()
        except KeyboardInterrupt:
            print("^C Received, shutting down server")
            server.server_close()
