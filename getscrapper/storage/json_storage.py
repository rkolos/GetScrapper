"""JSON storage implementation."""

import json
import os
from typing import Any, Dict, List, Optional

from .base_storage import BaseStorage
from ..utils.exceptions import StorageError


class JSONStorage(BaseStorage):
    """JSON storage implementation."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize JSON storage.
        
        Args:
            config: Storage configuration with keys:
                - encoding: File encoding (default: 'utf-8')
                - indent: JSON indentation (default: 2)
                - ensure_ascii: Whether to ensure ASCII encoding (default: False)
                - sort_keys: Whether to sort keys (default: False)
                - separators: JSON separators (default: (',', ': '))
        """
        self.config = config or {}
        self.encoding = self.config.get("encoding", "utf-8")
        self.indent = self.config.get("indent", 2)
        self.ensure_ascii = self.config.get("ensure_ascii", False)
        self.sort_keys = self.config.get("sort_keys", False)
        self.separators = self.config.get("separators", (",", ": "))
        super().__init__(config)

    def save(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save data to JSON file.
        
        Args:
            data: List of data dictionaries to save
            output_path: Path where to save the JSON file
            
        Raises:
            StorageError: If saving fails
        """
        try:
            if not data:
                raise StorageError("No data to save", "JSON")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to JSON file
            with open(output_path, 'w', encoding=self.encoding) as f:
                json.dump(
                    data,
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii,
                    sort_keys=self.sort_keys,
                    separators=self.separators
                )
            
        except Exception as e:
            raise StorageError(f"Failed to save JSON file: {str(e)}", "JSON")

    def load(self, input_path: str) -> List[Dict[str, Any]]:
        """
        Load data from JSON file.
        
        Args:
            input_path: Path to load JSON file from
            
        Returns:
            List of loaded data dictionaries
            
        Raises:
            StorageError: If loading fails
        """
        try:
            if not os.path.exists(input_path):
                raise StorageError(f"File not found: {input_path}", "JSON")
            
            # Load JSON file
            with open(input_path, 'r', encoding=self.encoding) as f:
                data = json.load(f)
            
            # Ensure data is a list
            if not isinstance(data, list):
                if isinstance(data, dict):
                    data = [data]
                else:
                    raise StorageError("JSON file must contain a list or object", "JSON")
            
            return data
            
        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid JSON format: {str(e)}", "JSON")
        except Exception as e:
            raise StorageError(f"Failed to load JSON file: {str(e)}", "JSON")

    def _validate_config(self) -> None:
        """Validate storage configuration."""
        valid_encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        if self.encoding not in valid_encodings:
            raise StorageError(f"Invalid encoding: {self.encoding}. Must be one of {valid_encodings}")
        
        if not isinstance(self.indent, (int, type(None))):
            raise StorageError("'indent' must be an integer or None")
        
        if not isinstance(self.ensure_ascii, bool):
            raise StorageError("'ensure_ascii' must be a boolean value")
        
        if not isinstance(self.sort_keys, bool):
            raise StorageError("'sort_keys' must be a boolean value")

    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return [".json", ".jsonl"]