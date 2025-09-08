"""Tests for configuration management."""

import json
import os
import pytest
from pathlib import Path

from getscrapper.config.settings import (
    Settings,
    SessionConfig,
    ParserConfig,
    ProcessorConfig,
    StorageConfig,
    LoggingConfig
)
from getscrapper.utils.exceptions import ConfigurationError


class TestSessionConfig:
    """Test SessionConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = SessionConfig()
        
        assert config.timeout == 30
        assert config.retries == 3
        assert config.backoff_factor == 0.3
        assert config.user_agent == "GetScrapper/1.0.0"
        assert config.delay == 1.0
        assert config.verify_ssl is True

    def test_custom_values(self):
        """Test custom configuration values."""
        config = SessionConfig(
            timeout=60,
            retries=5,
            backoff_factor=0.5,
            user_agent="Custom Agent",
            delay=2.0,
            verify_ssl=False
        )
        
        assert config.timeout == 60
        assert config.retries == 5
        assert config.backoff_factor == 0.5
        assert config.user_agent == "Custom Agent"
        assert config.delay == 2.0
        assert config.verify_ssl is False

    def test_validation_constraints(self):
        """Test validation constraints."""
        # Test timeout constraints
        with pytest.raises(ValueError):
            SessionConfig(timeout=0)  # Below minimum
        
        with pytest.raises(ValueError):
            SessionConfig(timeout=400)  # Above maximum
        
        # Test retries constraints
        with pytest.raises(ValueError):
            SessionConfig(retries=-1)  # Below minimum
        
        with pytest.raises(ValueError):
            SessionConfig(retries=15)  # Above maximum
        
        # Test backoff_factor constraints
        with pytest.raises(ValueError):
            SessionConfig(backoff_factor=-0.1)  # Below minimum
        
        with pytest.raises(ValueError):
            SessionConfig(backoff_factor=3.0)  # Above maximum
        
        # Test delay constraints
        with pytest.raises(ValueError):
            SessionConfig(delay=-1.0)  # Below minimum
        
        with pytest.raises(ValueError):
            SessionConfig(delay=70.0)  # Above maximum


class TestParserConfig:
    """Test ParserConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ParserConfig()
        
        assert config.html_parser == "lxml"
        assert config.encoding == "utf-8"
        assert config.extract_text is True
        assert config.clean_text is True

    def test_custom_values(self):
        """Test custom configuration values."""
        config = ParserConfig(
            html_parser="html.parser",
            encoding="latin-1",
            extract_text=False,
            clean_text=False
        )
        
        assert config.html_parser == "html.parser"
        assert config.encoding == "latin-1"
        assert config.extract_text is False
        assert config.clean_text is False


class TestProcessorConfig:
    """Test ProcessorConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ProcessorConfig()
        
        assert config.auto_clean is True
        assert config.validate_data is True
        assert config.transform_dates is True
        assert config.extract_numbers is False

    def test_custom_values(self):
        """Test custom configuration values."""
        config = ProcessorConfig(
            auto_clean=False,
            validate_data=False,
            transform_dates=False,
            extract_numbers=True
        )
        
        assert config.auto_clean is False
        assert config.validate_data is False
        assert config.transform_dates is False
        assert config.extract_numbers is True


class TestStorageConfig:
    """Test StorageConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = StorageConfig()
        
        assert config.csv_encoding == "utf-8"
        assert config.csv_delimiter == ","
        assert config.json_indent == 2
        assert config.json_ensure_ascii is False

    def test_custom_values(self):
        """Test custom configuration values."""
        config = StorageConfig(
            csv_encoding="latin-1",
            csv_delimiter=";",
            json_indent=4,
            json_ensure_ascii=True
        )
        
        assert config.csv_encoding == "latin-1"
        assert config.csv_delimiter == ";"
        assert config.json_indent == 4
        assert config.json_ensure_ascii is True

    def test_validation_constraints(self):
        """Test validation constraints."""
        # Test json_indent constraints
        with pytest.raises(ValueError):
            StorageConfig(json_indent=-1)  # Below minimum
        
        with pytest.raises(ValueError):
            StorageConfig(json_indent=10)  # Above maximum


class TestLoggingConfig:
    """Test LoggingConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert config.log_file is None
        assert "%(asctime)s" in config.format

    def test_custom_values(self):
        """Test custom configuration values."""
        config = LoggingConfig(
            level="DEBUG",
            log_file="/tmp/test.log",
            format="%(levelname)s: %(message)s"
        )
        
        assert config.level == "DEBUG"
        assert config.log_file == "/tmp/test.log"
        assert config.format == "%(levelname)s: %(message)s"

    def test_level_validation(self):
        """Test logging level validation."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            config = LoggingConfig(level=level)
            assert config.level == level
        
        # Test case insensitive
        config = LoggingConfig(level="debug")
        assert config.level == "DEBUG"
        
        # Test invalid level
        with pytest.raises(ValueError, match="Invalid logging level"):
            LoggingConfig(level="INVALID")


class TestSettings:
    """Test Settings class."""

    def test_default_settings(self):
        """Test default settings."""
        settings = Settings()
        
        assert isinstance(settings.session, SessionConfig)
        assert isinstance(settings.parser, ParserConfig)
        assert isinstance(settings.processor, ProcessorConfig)
        assert isinstance(settings.storage, StorageConfig)
        assert isinstance(settings.logging, LoggingConfig)
        
        assert settings.output_dir == "./output"
        assert settings.max_concurrent_requests == 5
        assert settings.continue_on_error is True

    def test_custom_settings(self):
        """Test custom settings."""
        settings = Settings(
            output_dir="/custom/output",
            max_concurrent_requests=10,
            continue_on_error=False,
            session=SessionConfig(timeout=60),
            parser=ParserConfig(encoding="latin-1")
        )
        
        assert settings.output_dir == "/custom/output"
        assert settings.max_concurrent_requests == 10
        assert settings.continue_on_error is False
        assert settings.session.timeout == 60
        assert settings.parser.encoding == "latin-1"

    def test_validation_constraints(self):
        """Test validation constraints."""
        # Test max_concurrent_requests constraints
        with pytest.raises(ValueError):
            Settings(max_concurrent_requests=0)  # Below minimum
        
        with pytest.raises(ValueError):
            Settings(max_concurrent_requests=60)  # Above maximum

    def test_from_file(self, temp_dir):
        """Test loading settings from file."""
        config_file = os.path.join(temp_dir, "config.json")
        config_data = {
            "output_dir": "/test/output",
            "max_concurrent_requests": 10,
            "session": {
                "timeout": 60,
                "retries": 5
            },
            "parser": {
                "encoding": "latin-1"
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        settings = Settings.from_file(config_file)
        
        assert settings.output_dir == "/test/output"
        assert settings.max_concurrent_requests == 10
        assert settings.session.timeout == 60
        assert settings.session.retries == 5
        assert settings.parser.encoding == "latin-1"

    def test_from_nonexistent_file(self, temp_dir):
        """Test loading from nonexistent file."""
        nonexistent_file = os.path.join(temp_dir, "nonexistent.json")
        
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            Settings.from_file(nonexistent_file)

    def test_from_invalid_json_file(self, temp_dir):
        """Test loading from invalid JSON file."""
        invalid_file = os.path.join(temp_dir, "invalid.json")
        
        with open(invalid_file, 'w') as f:
            f.write('{"invalid": json}')
        
        with pytest.raises(ConfigurationError, match="Invalid JSON"):
            Settings.from_file(invalid_file)

    def test_from_dict(self):
        """Test creating settings from dictionary."""
        config_dict = {
            "output_dir": "/test/output",
            "session": {"timeout": 60},
            "parser": {"encoding": "latin-1"}
        }
        
        settings = Settings.from_dict(config_dict)
        
        assert settings.output_dir == "/test/output"
        assert settings.session.timeout == 60
        assert settings.parser.encoding == "latin-1"

    def test_to_dict(self):
        """Test converting settings to dictionary."""
        settings = Settings(
            output_dir="/test/output",
            session=SessionConfig(timeout=60)
        )
        
        config_dict = settings.to_dict()
        
        assert config_dict["output_dir"] == "/test/output"
        assert config_dict["session"]["timeout"] == 60
        assert "parser" in config_dict
        assert "processor" in config_dict
        assert "storage" in config_dict
        assert "logging" in config_dict

    def test_to_file(self, temp_dir):
        """Test saving settings to file."""
        config_file = os.path.join(temp_dir, "output_config.json")
        settings = Settings(
            output_dir="/test/output",
            session=SessionConfig(timeout=60)
        )
        
        settings.to_file(config_file)
        
        assert os.path.exists(config_file)
        
        # Verify content
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        assert config_data["output_dir"] == "/test/output"
        assert config_data["session"]["timeout"] == 60

    def test_get_scraper_config(self):
        """Test getting scraper configuration."""
        settings = Settings(
            output_dir="/test/output",
            session=SessionConfig(timeout=60),
            parser=ParserConfig(encoding="latin-1")
        )
        
        scraper_config = settings.get_scraper_config()
        
        assert scraper_config["output_dir"] == "/test/output"
        assert scraper_config["session"]["timeout"] == 60
        assert scraper_config["parser"]["encoding"] == "latin-1"
        assert "processor" in scraper_config
        assert "storage" in scraper_config

    def test_validate_writable_output_dir(self, temp_dir):
        """Test validation with writable output directory."""
        settings = Settings(output_dir=temp_dir)
        settings.validate()  # Should not raise exception

    def test_validate_unwritable_output_dir(self):
        """Test validation with unwritable output directory."""
        settings = Settings(output_dir="/root/unwritable")
        
        with pytest.raises(ConfigurationError, match="Output directory is not writable"):
            settings.validate()

    def test_str_representation(self):
        """Test string representation."""
        settings = Settings(
            output_dir="/test/output",
            max_concurrent_requests=10
        )
        
        str_repr = str(settings)
        assert "output_dir=/test/output" in str_repr
        assert "max_concurrent=10" in str_repr