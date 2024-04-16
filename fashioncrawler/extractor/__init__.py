"""
Extractor Package
=======================

This package provides functionality for extracting data fashion-related websites.

Modules:
- base_data_extractor: Defines a base class for extracting data from web pages and storing it in a Pandas DataFrame.
- grailed_data_extractor: Implements data extraction from the Grailed website.
- depop_data_extractor: Implements data extraction from the Depop website.
"""

from .base_data_extractor import BaseDataExtractor
from .grailed_data_extractor import GrailedDataExtractor
from .depop_data_extractor import DepopDataExtractor
