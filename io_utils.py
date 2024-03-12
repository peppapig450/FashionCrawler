#!/usr/bin/env python3

import argparse
import json
import os
import re

import pandas as pd
import yaml


class IOUtils:

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
            "-o", "--output", help="Ouput file name (without extension)", type=str
        )

        # Driver options group
        driver_group = parser.add_argument_group("Driver options")
        driver_group.add_argument(
            "--headless", help="Run WebDriver in headless mode", action="store_true"
        )

        args = parser.parse_args()

        # Load configuration from YAML file
        config = IOUtils._load_config("config.yaml")

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
        try:
            with open(config_file, "r", encoding="UTF-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            # If config file not found enable all sites by default (set all but grailed to false until they're completed)
            config = {
                "sites": [
                    {"name": "grailed", "enabled": True},
                    {"name": "depop", "enabled": False},
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

    @staticmethod
    def _get_output_format(args):
        """
        Determine the output format based on command-line arguments.

        Args:
            args (Namespace): Parsed command-line arguments.

        Returns:
            str or None: Output format (json, csv, yaml) or None if no format specified.
        """
        if args.json:
            return "json"
        elif args.csv:
            return "csv"
        elif args.yaml:
            return "yaml"
        else:
            return None

    @staticmethod
    def _update_config_with_options(config, args):
        """
        Update the configuration with search, output, and driver options from command-line arguments.

        Args:
            config (dict): Configuration settings.
            args (Namespace): Parsed command-line arguments.
        """
        config["search_query"] = args.search
        config["output_format"] = IOUtils._get_output_format(args)
        config["headless"] = args.headless

    @staticmethod
    def save_output_to_file(df, output_filename, config):
        """
        Save the DataFrame to a file based on the specified output format.

        Args:
            df: The Pandas DataFrame to be saved.
            output_filename: The name of the output file.
            config: The configuration settings containing information about the output format.

        Returns:
            None
        """
        output_filename = IOUtils._generate_unique_filename(
            config.get("search_query", "output")
            if not output_filename
            else output_filename
        )

        output_format = config["output_format"]
        if output_format == "json":
            IOUtils._save_as_json(df, output_filename)
        elif output_format == "csv":
            IOUtils._save_as_csv(df, output_filename)
        elif output_format == "yaml":
            IOUtils._save_as_yaml(df, output_filename)
        else:
            print(df)

    @staticmethod
    def _save_as_json(df, filename):
        """
        Save a DataFrame to a JSON file.

        Args:
            df: The Pandas DataFrame to be saved.
            filename: The name of the output file.

        Returns:
            None
        """
        with open(f"{filename}.json", "w", encoding="utf-8") as json_file:
            json.dump(df.to_dict(orient="records"), json_file, indent=4)

    @staticmethod
    def _save_as_csv(df, filename):
        """
        Save a DataFrame to a CSV file.

        Args:
            df: The Pandas DataFrame to be saved.
            filename: The name of the output file.

        Returns:
            None
        """
        df.to_csv(f"{filename}.csv", index=False)

    @staticmethod
    def _save_as_yaml(df, filename):
        """
        Save a DataFrame to a YAML file.

        Args:
            df: The Pandas DataFrame to be saved.
            filename: The name of the output file.

        Returns:
            None
        """
        with open(f"{filename}.yaml", "w", encoding="utf-8") as yaml_file:
            yaml.safe_dump(df.to_dict(orient="records"), yaml_file)

    @staticmethod
    def _generate_unique_filename(filename):
        """
        Generate a unique filename by appending a number to the base filename if it already exists.

        Args:
        - filename: The original filename to be checked and modified if necessary.

        Returns:
        - The unique filename.
        """
        base_filename, extension = os.path.splitext(filename)
        match = re.match(r"^(.*)_?(\d+)$", base_filename)
        if match:
            base_filename = match.group(1)
            count = int(match.group(2)) + 1
            new_filename = f"{base_filename}_{count}{extension}"
        else:
            new_filename = f"{base_filename}_1{extension}"

        if os.path.exists(new_filename):
            return IOUtils._generate_unique_filename(new_filename)
        else:
            return new_filename
