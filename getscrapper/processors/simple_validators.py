"""Simplified data validation utilities without pydantic dependency."""

import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse


class DataValidator:
    """Data validation utilities."""

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits) <= 15

    @staticmethod
    def validate_date(date_str: str, format_pattern: str = r'\d{4}-\d{2}-\d{2}') -> bool:
        """
        Validate date format.
        
        Args:
            date_str: Date string to validate
            format_pattern: Regex pattern for date format
            
        Returns:
            True if valid, False otherwise
        """
        if not date_str:
            return False
        return bool(re.match(format_pattern, date_str))

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove control characters first
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text

    @staticmethod
    def extract_numbers(text: str) -> List[Union[int, float]]:
        """
        Extract numbers from text.
        
        Args:
            text: Text to extract numbers from
            
        Returns:
            List of extracted numbers
        """
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            try:
                if '.' in match:
                    numbers.append(float(match))
                else:
                    numbers.append(int(match))
            except ValueError:
                continue
        
        return numbers

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Validate that required fields are present in data.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            List of missing field names
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        
        return missing_fields


class SimpleScrapedDataModel:
    """Simple model for scraped data validation without pydantic."""
    
    def __init__(self, url: str, title: Optional[str] = None, content: Optional[str] = None, 
                 metadata: Optional[Dict[str, Any]] = None, timestamp: Optional[str] = None):
        """
        Initialize scraped data model.
        
        Args:
            url: Source URL
            title: Page title
            content: Extracted content
            metadata: Additional metadata
            timestamp: Extraction timestamp
        """
        if not DataValidator.validate_url(url):
            raise ValueError('Invalid URL format')
        
        self.url = url
        self.title = title
        self.content = DataValidator.clean_text(content) if content else None
        self.metadata = metadata or {}
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class ValidationResult:
    """Result of data validation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add validation warning."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }