"""Base fetcher strategy for HTML retrieval."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FetcherStrategy(ABC):
    """Abstract base class for HTML fetching strategies."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize fetcher strategy.
        
        Args:
            config: Configuration dictionary for the fetcher
        """
        self.config = config or {}
        self.logger = logger
    
    @abstractmethod
    async def fetch_html(self, url: str) -> Dict[str, Any]:
        """
        Fetch HTML content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary containing:
            - html_content: HTML content
            - page_title: Page title
            - final_url: Final URL after redirects
            - status_code: HTTP status code
            - content_length: Content length
            - render_time: Time taken to render
            - error: Error message if any
            - source: Source of the content (strategy name)
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get the name of this strategy.
        
        Returns:
            Strategy name
        """
        pass
    
    def is_available(self) -> bool:
        """
        Check if this strategy is available.
        
        Returns:
            True if strategy is available, False otherwise
        """
        return True
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get configuration for this strategy.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def close(self) -> None:
        """
        Clean up resources.
        Override in subclasses if needed.
        """
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()