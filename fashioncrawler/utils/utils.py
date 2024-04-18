"""
Utility Functions Module
=======================

This module provides utility functions for various operations.

Classes:
- Utils: A class containing utility methods.

Functions:
- convert_to_datetime(time_str_list): Convert a list of time strings to datetime objects.
"""

from datetime import datetime, timedelta


class Utils:
    """
    Utils: A class containing utility methods.

    Methods:
    - convert_to_datetime(time_str_list): Convert a list of time strings to datetime objects.
    """

    # TODO: optimize this (check testing/testing.py)
    @classmethod
    def convert_to_datetime(cls, time_str_list):
        """
        Convert a list of time strings to datetime objects.

        Args:
            time_str_list (list): A list of time strings.

        Returns:
            list: A list of formatted datetime strings.
        """
        datetime_list = []

        for time_str in time_str_list:
            parts = time_str.split(" ")
            num = int(parts[0])
            unit = parts[1]

            if unit in ("days", "day"):
                delta = timedelta(days=num)
                tformat = "%a, %B %d"
            elif unit in ("hours", "hour"):
                delta = timedelta(hours=num)
                tformat = "%a, %B %d at about %I%p"
            elif unit in ("minutes", "minute"):
                delta = timedelta(minutes=num)
                tformat = "%a, %B %d at %I:%M%p"
            else:
                raise ValueError("Invalid unit")

            datetime_string = datetime.now() - delta
            formatted_string = datetime_string.strftime(tformat)
            datetime_list.append(formatted_string)

        return datetime_list

    @staticmethod
    def create_context_dict(dataframes, **kwargs):
        """
        Create a context dictionary for Jinja2 templates by merging the given dataframes and additional key-value pairs.

        Parameters:
        - dataframes (dict): A dictionary containing dataframes as values.
        - **kwargs: Additional key-value pairs to include in the context dictionary.

        Returns:
        dict: A context dictionary containing merged dataframes and additional key-value pairs.
        """
        context = {**dataframes, **kwargs}
        return context
