"""Fetcher strategies for different HTML retrieval methods."""

from .base_fetcher import FetcherStrategy
from .static_fetcher import StaticFetcher
from .local_browser_fetcher import LocalBrowserFetcher
from .browserbase_fetcher import BrowserbaseFetcher

__all__ = [
    'FetcherStrategy',
    'StaticFetcher', 
    'LocalBrowserFetcher',
    'BrowserbaseFetcher'
]