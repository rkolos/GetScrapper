"""Tests for custom exceptions."""

import pytest

from getscrapper.utils.exceptions import (
    GetScrapperError,
    ParsingError,
    StorageError,
    ConfigurationError,
    NetworkError
)


class TestGetScrapperError:
    """Test GetScrapperError base exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = GetScrapperError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None

    def test_error_with_code(self):
        """Test error with error code."""
        error = GetScrapperError("Test error", "TEST_ERROR")
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"


class TestParsingError:
    """Test ParsingError exception."""

    def test_parsing_error(self):
        """Test parsing error creation."""
        error = ParsingError("Failed to parse HTML", "HTML")
        assert error.message == "Failed to parse HTML"
        assert error.error_code == "PARSING_ERROR"
        assert error.parser_type == "HTML"

    def test_parsing_error_without_type(self):
        """Test parsing error without parser type."""
        error = ParsingError("Failed to parse")
        assert error.message == "Failed to parse"
        assert error.parser_type is None


class TestStorageError:
    """Test StorageError exception."""

    def test_storage_error(self):
        """Test storage error creation."""
        error = StorageError("Failed to save file", "CSV")
        assert error.message == "Failed to save file"
        assert error.error_code == "STORAGE_ERROR"
        assert error.storage_type == "CSV"

    def test_storage_error_without_type(self):
        """Test storage error without storage type."""
        error = StorageError("Failed to save")
        assert error.message == "Failed to save"
        assert error.storage_type is None


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error(self):
        """Test configuration error creation."""
        error = ConfigurationError("Invalid configuration")
        assert error.message == "Invalid configuration"
        assert error.error_code == "CONFIG_ERROR"


class TestNetworkError:
    """Test NetworkError exception."""

    def test_network_error(self):
        """Test network error creation."""
        error = NetworkError("Connection failed", 500)
        assert error.message == "Connection failed"
        assert error.error_code == "NETWORK_ERROR"
        assert error.status_code == 500

    def test_network_error_without_status(self):
        """Test network error without status code."""
        error = NetworkError("Connection failed")
        assert error.message == "Connection failed"
        assert error.status_code is None