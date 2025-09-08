"""Data processing and transformation utilities."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .validators import DataValidator, ScrapedDataModel, ValidationResult


class DataProcessor:
    """Data processing and transformation utilities."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize data processor.
        
        Args:
            config: Processor configuration with keys:
                - auto_clean: Whether to automatically clean data (default: True)
                - validate_data: Whether to validate data (default: True)
                - transform_dates: Whether to transform date strings (default: True)
                - extract_numbers: Whether to extract numbers from text (default: False)
        """
        self.config = config or {}
        self.auto_clean = self.config.get("auto_clean", True)
        self.validate_data = self.config.get("validate_data", True)
        self.transform_dates = self.config.get("transform_dates", True)
        self.extract_numbers = self.config.get("extract_numbers", False)

    def process(self, data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """
        Process a list of data items.
        
        Args:
            data: List of data dictionaries to process
            **kwargs: Additional processing options
            
        Returns:
            List of processed data dictionaries
        """
        processed_data = []
        
        for item in data:
            try:
                processed_item = self._process_item(item, **kwargs)
                processed_data.append(processed_item)
            except Exception as e:
                # Log error but continue processing other items
                processed_item = item.copy()
                processed_item["_processing_error"] = str(e)
                processed_data.append(processed_item)
        
        return processed_data

    def _process_item(self, item: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process a single data item."""
        processed_item = item.copy()
        
        # Add processing metadata
        processed_item["_processed_at"] = datetime.now().isoformat()
        processed_item["_processor_version"] = "1.0.0"
        
        # Auto-clean text fields
        if self.auto_clean:
            processed_item = self._clean_item(processed_item)
        
        # Transform dates
        if self.transform_dates:
            processed_item = self._transform_dates(processed_item)
        
        # Extract numbers
        if self.extract_numbers:
            processed_item = self._extract_numbers(processed_item)
        
        # Validate data
        if self.validate_data:
            validation_result = self._validate_item(processed_item)
            processed_item["_validation"] = validation_result.to_dict()
        
        return processed_item

    def _clean_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Clean text fields in the item."""
        cleaned_item = item.copy()
        
        for key, value in item.items():
            if isinstance(value, str):
                cleaned_item[key] = DataValidator.clean_text(value)
            elif isinstance(value, dict):
                cleaned_item[key] = self._clean_item(value)
            elif isinstance(value, list):
                cleaned_item[key] = [
                    DataValidator.clean_text(v) if isinstance(v, str) else v
                    for v in value
                ]
        
        return cleaned_item

    def _transform_dates(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform date strings to standardized format."""
        transformed_item = item.copy()
        
        # Common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        ]
        
        for key, value in item.items():
            if isinstance(value, str):
                for pattern in date_patterns:
                    if re.match(pattern, value):
                        try:
                            # Try to parse and reformat the date
                            parsed_date = datetime.strptime(value, self._get_date_format(pattern))
                            transformed_item[key] = parsed_date.isoformat()
                            transformed_item[f"{key}_original"] = value
                        except ValueError:
                            continue
                        break
        
        return transformed_item

    def _get_date_format(self, pattern: str) -> str:
        """Get datetime format string for a pattern."""
        format_mapping = {
            r'\d{4}-\d{2}-\d{2}': '%Y-%m-%d',
            r'\d{2}/\d{2}/\d{4}': '%m/%d/%Y',
            r'\d{2}-\d{2}-\d{4}': '%m-%d-%Y',
            r'\d{4}/\d{2}/\d{2}': '%Y/%m/%d',
        }
        return format_mapping.get(pattern, '%Y-%m-%d')

    def _extract_numbers(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract numbers from text fields."""
        extracted_item = item.copy()
        
        for key, value in item.items():
            if isinstance(value, str):
                numbers = DataValidator.extract_numbers(value)
                if numbers:
                    extracted_item[f"{key}_numbers"] = numbers
        
        return extracted_item

    def _validate_item(self, item: Dict[str, Any]) -> ValidationResult:
        """Validate a data item."""
        result = ValidationResult(is_valid=True)
        
        # Check for required fields
        required_fields = ["url", "content"]
        missing_fields = DataValidator.validate_required_fields(item, required_fields)
        if missing_fields:
            result.add_error(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate URL if present
        if "url" in item and item["url"]:
            if not DataValidator.validate_url(item["url"]):
                result.add_error("Invalid URL format")
        
        # Validate email if present
        if "email" in item and item["email"]:
            if not DataValidator.validate_email(item["email"]):
                result.add_warning("Invalid email format")
        
        # Validate phone if present
        if "phone" in item and item["phone"]:
            if not DataValidator.validate_phone(item["phone"]):
                result.add_warning("Invalid phone format")
        
        return result

    def filter_data(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter data based on criteria.
        
        Args:
            data: List of data dictionaries to filter
            filters: Filter criteria dictionary
            
        Returns:
            Filtered list of data dictionaries
        """
        filtered_data = []
        
        for item in data:
            if self._matches_filters(item, filters):
                filtered_data.append(item)
        
        return filtered_data

    def _matches_filters(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if item matches filter criteria."""
        for field, criteria in filters.items():
            if field not in item:
                return False
            
            value = item[field]
            
            if isinstance(criteria, dict):
                # Complex filter criteria
                if "min" in criteria and value < criteria["min"]:
                    return False
                if "max" in criteria and value > criteria["max"]:
                    return False
                if "contains" in criteria and criteria["contains"] not in str(value):
                    return False
                if "regex" in criteria and not re.search(criteria["regex"], str(value)):
                    return False
            else:
                # Simple equality check
                if value != criteria:
                    return False
        
        return True

    def group_data(self, data: List[Dict[str, Any]], group_by: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group data by a field.
        
        Args:
            data: List of data dictionaries to group
            group_by: Field name to group by
            
        Returns:
            Dictionary with grouped data
        """
        grouped_data = {}
        
        for item in data:
            if group_by in item:
                key = str(item[group_by])
                if key not in grouped_data:
                    grouped_data[key] = []
                grouped_data[key].append(item)
        
        return grouped_data

    def aggregate_data(self, data: List[Dict[str, Any]], aggregations: Dict[str, str]) -> Dict[str, Any]:
        """
        Aggregate data using specified functions.
        
        Args:
            data: List of data dictionaries to aggregate
            aggregations: Dictionary mapping field names to aggregation functions
            
        Returns:
            Dictionary with aggregated results
        """
        results = {}
        
        for field, func in aggregations.items():
            values = [item.get(field) for item in data if field in item and item[field] is not None]
            
            if not values:
                results[field] = None
                continue
            
            if func == "count":
                results[field] = len(values)
            elif func == "sum":
                results[field] = sum(v for v in values if isinstance(v, (int, float)))
            elif func == "avg":
                numeric_values = [v for v in values if isinstance(v, (int, float))]
                results[field] = sum(numeric_values) / len(numeric_values) if numeric_values else None
            elif func == "min":
                results[field] = min(values)
            elif func == "max":
                results[field] = max(values)
            elif func == "unique":
                results[field] = list(set(values))
        
        return results