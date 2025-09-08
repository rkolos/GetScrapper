"""Base parser class for all parsers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..utils.exceptions import ParsingError


class BaseParser(ABC):
    """Base class for all parsers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize parser with optional configuration.
        
        Args:
            config: Parser configuration dictionary
        """
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def parse(self, content: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Parse content and extract data.
        
        Args:
            content: Raw content to parse
            **kwargs: Additional parsing parameters
            
        Returns:
            List of extracted data dictionaries
            
        Raises:
            ParsingError: If parsing fails
        """
        pass

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate parser configuration."""
        pass

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported content formats.
        
        Returns:
            List of supported format strings
        """
        return []

    def is_supported(self, content_type: str) -> bool:
        """
        Check if content type is supported.
        
        Args:
            content_type: MIME type or format string
            
        Returns:
            True if supported, False otherwise
        """
        return content_type.lower() in [
            fmt.lower() for fmt in self.get_supported_formats()
        ]