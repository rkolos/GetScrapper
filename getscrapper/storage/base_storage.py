"""Base storage class for all storage implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..utils.exceptions import StorageError


class BaseStorage(ABC):
    """Base class for all storage implementations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize storage with optional configuration.
        
        Args:
            config: Storage configuration dictionary
        """
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def save(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save data to storage.
        
        Args:
            data: List of data dictionaries to save
            output_path: Path where to save the data
            
        Raises:
            StorageError: If saving fails
        """
        pass

    @abstractmethod
    def load(self, input_path: str) -> List[Dict[str, Any]]:
        """
        Load data from storage.
        
        Args:
            input_path: Path to load data from
            
        Returns:
            List of loaded data dictionaries
            
        Raises:
            StorageError: If loading fails
        """
        pass

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate storage configuration."""
        pass

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported format strings
        """
        return []

    def is_supported(self, file_extension: str) -> bool:
        """
        Check if file extension is supported.
        
        Args:
            file_extension: File extension (e.g., '.csv', '.json')
            
        Returns:
            True if supported, False otherwise
        """
        return file_extension.lower() in [
            fmt.lower() for fmt in self.get_supported_formats()
        ]