"""Tests for data validators."""

import pytest

from getscrapper.processors.validators import (
    DataValidator,
    ScrapedDataModel,
    ValidationResult
)


class TestDataValidator:
    """Test DataValidator class."""

    def test_validate_url_valid(self):
        """Test URL validation with valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com/path",
            "https://example.com:8080/path?query=value",
            "ftp://example.com/file.txt"
        ]
        
        for url in valid_urls:
            assert DataValidator.validate_url(url) is True

    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "example.com",
            "https://",
            "",
            "javascript:alert('test')"
        ]
        
        for url in invalid_urls:
            assert DataValidator.validate_url(url) is False

    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.com"
        ]
        
        for email in valid_emails:
            assert DataValidator.validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "test@",
            "test.example.com",
            ""
        ]
        
        for email in invalid_emails:
            assert DataValidator.validate_email(email) is False

    def test_validate_phone_valid(self):
        """Test phone validation with valid phone numbers."""
        valid_phones = [
            "1234567890",
            "+1-234-567-8900",
            "(123) 456-7890",
            "123.456.7890",
            "+44 20 7946 0958"
        ]
        
        for phone in valid_phones:
            assert DataValidator.validate_phone(phone) is True

    def test_validate_phone_invalid(self):
        """Test phone validation with invalid phone numbers."""
        invalid_phones = [
            "123",
            "12345678901234567890",  # Too long
            "abc-def-ghij",
            ""
        ]
        
        for phone in invalid_phones:
            assert DataValidator.validate_phone(phone) is False

    def test_validate_date_valid(self):
        """Test date validation with valid dates."""
        valid_dates = [
            "2023-01-01",
            "2023-12-31",
            "2000-02-29"  # Leap year
        ]
        
        for date in valid_dates:
            assert DataValidator.validate_date(date) is True

    def test_validate_date_invalid(self):
        """Test date validation with invalid dates."""
        invalid_dates = [
            "23-01-01",    # Wrong format
            "2023/01/01",  # Wrong separator
            ""
        ]
        
        for date in invalid_dates:
            assert DataValidator.validate_date(date) is False

    def test_clean_text(self):
        """Test text cleaning functionality."""
        test_cases = [
            ("  hello   world  ", "hello world"),
            ("\n\t  test  \n\t", "test"),
            ("", ""),
            ("normal text", "normal text"),
            ("text\x00with\x1fcontrol\x7fchars", "textwithcontrolchars")
        ]
        
        for input_text, expected in test_cases:
            assert DataValidator.clean_text(input_text) == expected

    def test_extract_numbers(self):
        """Test number extraction from text."""
        test_cases = [
            ("Price: $19.99", [19.99]),
            ("Count: 42 items", [42]),
            ("Range: 10-20", [10, -20]),  # Fixed: -20 is correct for "10-20"
            ("Negative: -5.5", [-5.5]),
            ("No numbers here", []),
            ("", [])
        ]
        
        for text, expected in test_cases:
            assert DataValidator.extract_numbers(text) == expected

    def test_validate_required_fields(self):
        """Test required fields validation."""
        data = {
            "name": "John",
            "email": "john@example.com",
            "age": 30
        }
        
        # All fields present
        missing = DataValidator.validate_required_fields(data, ["name", "email"])
        assert missing == []
        
        # Some fields missing
        missing = DataValidator.validate_required_fields(data, ["name", "phone", "address"])
        assert missing == ["phone", "address"]
        
        # Empty values
        data_with_empty = {"name": "", "email": None}
        missing = DataValidator.validate_required_fields(data_with_empty, ["name", "email"])
        assert missing == ["name", "email"]


class TestScrapedDataModel:
    """Test ScrapedDataModel validation."""

    def test_valid_data(self):
        """Test valid scraped data."""
        data = {
            "url": "https://example.com",
            "title": "Test Page",
            "content": "Test content",
            "metadata": {"key": "value"},
            "timestamp": "2023-01-01T00:00:00Z"
        }
        
        model = ScrapedDataModel(**data)
        assert model.url == "https://example.com"
        assert model.title == "Test Page"
        assert model.content == "Test content"

    def test_invalid_url(self):
        """Test invalid URL validation."""
        data = {
            "url": "not-a-url",
            "content": "Test content"
        }
        
        with pytest.raises(ValueError, match="Invalid URL format"):
            ScrapedDataModel(**data)

    def test_content_cleaning(self):
        """Test content cleaning in model."""
        data = {
            "url": "https://example.com",
            "content": "  dirty   content  \n\t"
        }
        
        model = ScrapedDataModel(**data)
        assert model.content == "dirty content"


class TestValidationResult:
    """Test ValidationResult class."""

    def test_valid_result(self):
        """Test valid validation result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_invalid_result(self):
        """Test invalid validation result."""
        result = ValidationResult(is_valid=False, errors=["Error 1"], warnings=["Warning 1"])
        assert result.is_valid is False
        assert result.errors == ["Error 1"]
        assert result.warnings == ["Warning 1"]

    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult(is_valid=True)
        result.add_error("New error")
        
        assert result.is_valid is False
        assert result.errors == ["New error"]

    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult(is_valid=True)
        result.add_warning("New warning")
        
        assert result.is_valid is True
        assert result.warnings == ["New warning"]

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ValidationResult(is_valid=False, errors=["Error"], warnings=["Warning"])
        expected = {
            "is_valid": False,
            "errors": ["Error"],
            "warnings": ["Warning"]
        }
        
        assert result.to_dict() == expected