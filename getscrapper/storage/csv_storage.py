"""CSV storage implementation."""

import csv
import os
from typing import Any, Dict, List, Optional

import pandas as pd

from .base_storage import BaseStorage
from ..utils.exceptions import StorageError


class CSVStorage(BaseStorage):
    """CSV storage implementation using pandas."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize CSV storage.
        
        Args:
            config: Storage configuration with keys:
                - encoding: File encoding (default: 'utf-8')
                - delimiter: CSV delimiter (default: ',')
                - quotechar: CSV quote character (default: '"')
                - quoting: CSV quoting mode (default: csv.QUOTE_MINIMAL)
                - index: Whether to include index column (default: False)
                - na_rep: Representation for NaN values (default: '')
        """
        self.config = config or {}
        self.encoding = self.config.get("encoding", "utf-8")
        self.delimiter = self.config.get("delimiter", ",")
        self.quotechar = self.config.get("quotechar", '"')
        self.quoting = self.config.get("quoting", csv.QUOTE_MINIMAL)
        self.index = self.config.get("index", False)
        self.na_rep = self.config.get("na_rep", "")
        super().__init__(config)

    def save(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save data to CSV file.
        
        Args:
            data: List of data dictionaries to save
            output_path: Path where to save the CSV file
            
        Raises:
            StorageError: If saving fails
        """
        try:
            if not data:
                raise StorageError("No data to save", "CSV")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Save to CSV
            df.to_csv(
                output_path,
                encoding=self.encoding,
                sep=self.delimiter,
                quotechar=self.quotechar,
                quoting=self.quoting,
                index=self.index,
                na_rep=self.na_rep
            )
            
        except Exception as e:
            raise StorageError(f"Failed to save CSV file: {str(e)}", "CSV")

    def load(self, input_path: str) -> List[Dict[str, Any]]:
        """
        Load data from CSV file.
        
        Args:
            input_path: Path to load CSV file from
            
        Returns:
            List of loaded data dictionaries
            
        Raises:
            StorageError: If loading fails
        """
        try:
            if not os.path.exists(input_path):
                raise StorageError(f"File not found: {input_path}", "CSV")
            
            # Load CSV file
            df = pd.read_csv(
                input_path,
                encoding=self.encoding,
                sep=self.delimiter,
                quotechar=self.quotechar,
                quoting=self.quoting
            )
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            
            return data
            
        except Exception as e:
            raise StorageError(f"Failed to load CSV file: {str(e)}", "CSV")

    def _validate_config(self) -> None:
        """Validate storage configuration."""
        valid_encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        if self.encoding not in valid_encodings:
            raise StorageError(f"Invalid encoding: {self.encoding}. Must be one of {valid_encodings}")
        
        if not isinstance(self.index, bool):
            raise StorageError("'index' must be a boolean value")

    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return [".csv", ".tsv"]