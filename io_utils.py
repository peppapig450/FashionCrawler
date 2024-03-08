#!/usr/bin/env python3

import argparse
import json
import os
import re

import yaml


def parse_args():
    """
    Parse command-line arguments using the argparse module.
    """
    parser = argparse.ArgumentParser(
        description="Grailed scraper for Final Create Task"
    )

    search_group = parser.add_argument_group("Search options")
    output_group = parser.add_argument_group("Output options")
    driver_group = parser.add_argument_group("Driver options")

    search_group.add_argument(
        "-s", "--search", help="Search query to scrape for", type=str
    )
    output_group.add_argument(
        "-j", "--json", help="Output as JSON", action="store_true"
    )
    output_group.add_argument("-c", "--csv", help="Output as CSV", action="store_true")
    output_group.add_argument(
        "-y", "--yaml", help="Output as YAML", action="store_true"
    )
    output_group.add_argument("-o", "--output", help="Output file name", type=str)
    driver_group.add_argument(
        "--headless", help="Run ChromeDriver in headless mode", action="store_true"
    )

    return parser.parse_args()


def save_as_json(df, filename):
    """
    Save a DataFrame to a JSON file.
    """
    with open(f"{filename}.json", "w", encoding="utf-8") as json_file:
        json.dump(df.to_dict(orient="records"), json_file, indent=4)


def save_as_csv(df, filename):
    """
    Save a DataFrame to a CSV file.
    """
    df.to_csv(f"{filename}.csv", index=False)


def save_as_yaml(df, filename):
    """
    Save a DataFrame to a YAML file.
    """
    with open(f"{filename}.yaml", "w", encoding="utf-8") as yaml_file:
        yaml.safe_dump(df.to_dict(orient="records"), yaml_file)


def generate_unique_filename(filename):
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
        return generate_unique_filename(new_filename)
    else:
        return new_filename


def save_output_to_file(df, output_filename, args):
    """
    Save the DataFrame to a file based on the specified output format.

    Args:
    - df: The Pandas DataFrame to be saved.
    - output_filename: The name of the output file.
    - args: The command-line arguments containing information about the output format.

    Returns:
    - None
    """
    if args.json:
        save_as_json(df, output_filename)
    elif args.csv:
        save_as_csv(df, output_filename)
    elif args.yaml:
        save_as_yaml(df, output_filename)
    else:
        print(df)
