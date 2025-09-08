"""Simplified CSV storage implementation without pandas dependency."""

import csv
import os
from typing import Any, Dict, List, Optional

from .base_storage import BaseStorage
from ..utils.exceptions import StorageError


class SimpleCSVStorage(BaseStorage):
    """Simplified CSV storage implementation without pandas."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize CSV storage.
        
        Args:
            config: Storage configuration with keys:
                - encoding: File encoding (default: 'utf-8')
                - delimiter: CSV delimiter (default: ',')
                - quotechar: CSV quote character (default: '"')
                - quoting: CSV quoting mode (default: csv.QUOTE_MINIMAL)
        """
        self.config = config or {}
        self.encoding = self.config.get("encoding", "utf-8")
        self.delimiter = self.config.get("delimiter", ",")
        self.quotechar = self.config.get("quotechar", '"')
        self.quoting = self.config.get("quoting", csv.QUOTE_MINIMAL)
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
            
            # Get all unique field names
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))
            
            # Write CSV file
            with open(output_path, 'w', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fieldnames,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                    quoting=self.quoting
                )
                
                # Write header
                writer.writeheader()
                
                # Write data rows
                for item in data:
                    # Convert all values to strings and handle None values
                    row = {}
                    for field in fieldnames:
                        value = item.get(field, '')
                        if value is None:
                            row[field] = ''
                        else:
                            row[field] = str(value)
                    writer.writerow(row)
            
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
            
            data = []
            
            with open(input_path, 'r', newline='', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(
                    csvfile,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                    quoting=self.quoting
                )
                
                for row in reader:
                    # Convert empty strings back to None for consistency
                    processed_row = {}
                    for key, value in row.items():
                        if value == '':
                            processed_row[key] = None
                        else:
                            processed_row[key] = value
                    data.append(processed_row)
            
            return data
            
        except Exception as e:
            raise StorageError(f"Failed to load CSV file: {str(e)}", "CSV")

    def _validate_config(self) -> None:
        """Validate storage configuration."""
        valid_encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        if self.encoding not in valid_encodings:
            raise StorageError(f"Invalid encoding: {self.encoding}. Must be one of {valid_encodings}")

    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return [".csv", ".tsv"]