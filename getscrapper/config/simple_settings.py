"""Simplified configuration management for GetScrapper without pydantic dependency."""

import os
from typing import Any, Dict, Optional


class SimpleSettings:
    """Simple settings class without pydantic dependency."""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize settings with default values."""
        config = config_dict or {}
        
        # Session settings
        self.session = config.get("session", {})
        self.session.setdefault("timeout", 30)
        self.session.setdefault("retries", 3)
        self.session.setdefault("backoff_factor", 0.3)
        self.session.setdefault("user_agent", "GetScrapper/1.0.0")
        self.session.setdefault("delay", 1.0)
        self.session.setdefault("verify_ssl", True)
        
        # Parser settings
        self.parser = config.get("parser", {})
        self.parser.setdefault("html_parser", "lxml")
        self.parser.setdefault("encoding", "utf-8")
        self.parser.setdefault("extract_text", True)
        self.parser.setdefault("clean_text", True)
        
        # Processor settings
        self.processor = config.get("processor", {})
        self.processor.setdefault("auto_clean", True)
        self.processor.setdefault("validate_data", True)
        self.processor.setdefault("transform_dates", True)
        self.processor.setdefault("extract_numbers", False)
        
        # Storage settings
        self.storage = config.get("storage", {})
        self.storage.setdefault("csv_encoding", "utf-8")
        self.storage.setdefault("csv_delimiter", ",")
        self.storage.setdefault("json_indent", 2)
        self.storage.setdefault("json_ensure_ascii", False)
        
        # Logging settings
        self.logging = config.get("logging", {})
        self.logging.setdefault("level", "INFO")
        self.logging.setdefault("log_file", None)
        self.logging.setdefault("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Global settings
        self.output_dir = config.get("output_dir", "./output")
        self.max_concurrent_requests = config.get("max_concurrent_requests", 5)
        self.continue_on_error = config.get("continue_on_error", True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "session": self.session,
            "parser": self.parser,
            "processor": self.processor,
            "storage": self.storage,
            "logging": self.logging,
            "output_dir": self.output_dir,
            "max_concurrent_requests": self.max_concurrent_requests,
            "continue_on_error": self.continue_on_error,
        }
    
    def get_scraper_config(self) -> Dict[str, Any]:
        """Get configuration for scraper initialization."""
        return {
            "session": self.session,
            "parser": self.parser,
            "processor": self.processor,
            "storage": self.storage,
            "output_dir": self.output_dir,
        }
    
    def validate(self) -> None:
        """Validate settings configuration."""
        # Check if output directory is writable
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            test_file = os.path.join(self.output_dir, ".test_write")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            raise ValueError(f"Output directory is not writable: {str(e)}")
    
    def __str__(self) -> str:
        """String representation of settings."""
        return f"SimpleSettings(output_dir={self.output_dir}, max_concurrent={self.max_concurrent_requests})"


# Default settings instance
default_settings = SimpleSettings()