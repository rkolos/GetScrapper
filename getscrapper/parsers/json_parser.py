"""JSON parser implementation."""

import json
from typing import Any, Dict, List, Optional, Union

from .base_parser import BaseParser
from ..utils.exceptions import ParsingError


class JSONParser(BaseParser):
    """JSON parser for extracting data from JSON content."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize JSON parser.
        
        Args:
            config: Parser configuration with keys:
                - encoding: Text encoding (default: 'utf-8')
                - strict: Whether to use strict JSON parsing (default: True)
                - object_hook: Custom object hook for JSON parsing
        """
        self.config = config or {}
        self.encoding = self.config.get("encoding", "utf-8")
        self.strict = self.config.get("strict", True)
        self.object_hook = self.config.get("object_hook")
        super().__init__(config)

    def parse(self, content: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Parse JSON content and extract data.
        
        Args:
            content: JSON content to parse
            **kwargs: Additional parameters:
                - path: JSONPath expression to extract specific data
                - flatten: Whether to flatten nested objects (default: False)
                - extract_arrays: Whether to extract array elements separately (default: False)
                
        Returns:
            List of extracted data dictionaries
            
        Raises:
            ParsingError: If parsing fails
        """
        try:
            # Parse JSON content
            json_data = self._parse_json(content)
            
            # Extract data based on path if specified
            path = kwargs.get("path")
            if path:
                extracted_data = self._extract_by_path(json_data, path)
            else:
                extracted_data = json_data
            
            # Process the extracted data
            results = self._process_extracted_data(extracted_data, kwargs)
            
            return results
            
        except Exception as e:
            raise ParsingError(f"Failed to parse JSON: {str(e)}", "JSON")

    def _parse_json(self, content: str) -> Union[Dict[str, Any], List[Any]]:
        """Parse JSON content."""
        try:
            return json.loads(content, strict=self.strict, object_hook=self.object_hook)
        except json.JSONDecodeError as e:
            raise ParsingError(f"Invalid JSON format: {str(e)}", "JSON")

    def _extract_by_path(self, data: Union[Dict[str, Any], List[Any]], path: str) -> Any:
        """
        Extract data using a simple path notation.
        
        Args:
            data: JSON data to extract from
            path: Path notation (e.g., "users[0].name", "items[*].price")
            
        Returns:
            Extracted data
        """
        current = data
        
        # Simple path parsing - can be extended with full JSONPath support
        parts = path.split('.')
        
        for part in parts:
            if '[' in part and ']' in part:
                # Handle array access like "items[0]" or "items[*]"
                key = part[:part.index('[')]
                index_str = part[part.index('[') + 1:part.index(']')]
                
                if key:
                    current = current[key]
                
                if index_str == '*':
                    # Extract all elements from array
                    if isinstance(current, list):
                        return current
                    else:
                        raise ParsingError(f"Expected array at path {key}, got {type(current)}")
                else:
                    try:
                        index = int(index_str)
                        current = current[index]
                    except (ValueError, IndexError) as e:
                        raise ParsingError(f"Invalid array index {index_str}: {str(e)}")
            else:
                # Handle object key access
                if isinstance(current, dict):
                    current = current[part]
                else:
                    raise ParsingError(f"Expected object at path {part}, got {type(current)}")
        
        return current

    def _process_extracted_data(self, data: Any, kwargs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process extracted data into standardized format."""
        results = []
        
        if isinstance(data, list):
            # Handle array data
            if kwargs.get("extract_arrays", False):
                # Extract each array element as separate item
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        item["_array_index"] = i
                        results.append(item)
                    else:
                        results.append({
                            "value": item,
                            "_array_index": i,
                            "_type": type(item).__name__
                        })
            else:
                # Return array as single item
                results.append({
                    "data": data,
                    "_type": "array",
                    "_length": len(data)
                })
        
        elif isinstance(data, dict):
            # Handle object data
            if kwargs.get("flatten", False):
                flattened = self._flatten_dict(data)
                results.append(flattened)
            else:
                results.append(data)
        
        else:
            # Handle primitive data
            results.append({
                "value": data,
                "_type": type(data).__name__
            })
        
        return results

    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary."""
        items = []
        
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, value))
        
        return dict(items)

    def _validate_config(self) -> None:
        """Validate parser configuration."""
        if not isinstance(self.strict, bool):
            raise ParsingError("'strict' must be a boolean value")

    def get_supported_formats(self) -> List[str]:
        """Get supported content formats."""
        return ["application/json", "text/json", "json"]