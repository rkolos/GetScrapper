"""
GetScrapper - A powerful web scraping tool for extracting structured data.

This package provides a comprehensive solution for web scraping with support for
various data extraction methods, processing pipelines, and output formats.
"""

__version__ = "1.0.0"
__author__ = "GetScrapper Team"

from .core.scraper import Scraper
from .core.session import SessionManager
from .parsers.html_parser import HTMLParser
from .parsers.json_parser import JSONParser
from .processors.data_processor import DataProcessor
from .storage.csv_storage import CSVStorage
from .storage.json_storage import JSONStorage
from .config.settings import Settings

__all__ = [
    "Scraper",
    "SessionManager", 
    "HTMLParser",
    "JSONParser",
    "DataProcessor",
    "CSVStorage",
    "JSONStorage",
    "Settings",
]