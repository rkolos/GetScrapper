"""Configuration management for GetScrapper."""

import os
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

from ..utils.exceptions import ConfigurationError

# Load environment variables
load_dotenv()


class SessionConfig(BaseModel):
    """Session configuration model."""
    
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    retries: int = Field(default=3, ge=0, le=10, description="Number of retries")
    backoff_factor: float = Field(default=0.3, ge=0.0, le=2.0, description="Backoff factor for retries")
    user_agent: str = Field(default="GetScrapper/1.0.0", description="User agent string")
    delay: float = Field(default=1.0, ge=0.0, le=60.0, description="Delay between requests in seconds")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    
    class Config:
        env_prefix = "GETSCRAPPER_SESSION_"


class ParserConfig(BaseModel):
    """Parser configuration model."""
    
    html_parser: str = Field(default="lxml", description="HTML parser to use")
    encoding: str = Field(default="utf-8", description="Text encoding")
    extract_text: bool = Field(default=True, description="Whether to extract text content")
    clean_text: bool = Field(default=True, description="Whether to clean extracted text")
    
    class Config:
        env_prefix = "GETSCRAPPER_PARSER_"


class ProcessorConfig(BaseModel):
    """Data processor configuration model."""
    
    auto_clean: bool = Field(default=True, description="Whether to automatically clean data")
    validate_data: bool = Field(default=True, description="Whether to validate data")
    transform_dates: bool = Field(default=True, description="Whether to transform date strings")
    extract_numbers: bool = Field(default=False, description="Whether to extract numbers from text")
    
    class Config:
        env_prefix = "GETSCRAPPER_PROCESSOR_"


class StorageConfig(BaseModel):
    """Storage configuration model."""
    
    csv_encoding: str = Field(default="utf-8", description="CSV file encoding")
    csv_delimiter: str = Field(default=",", description="CSV delimiter")
    json_indent: int = Field(default=2, ge=0, le=8, description="JSON indentation")
    json_ensure_ascii: bool = Field(default=False, description="Whether to ensure ASCII encoding in JSON")
    
    class Config:
        env_prefix = "GETSCRAPPER_STORAGE_"


class LoggingConfig(BaseModel):
    """Logging configuration model."""
    
    level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid logging level: {v}. Must be one of {valid_levels}')
        return v.upper()
    
    class Config:
        env_prefix = "GETSCRAPPER_LOG_"


class Settings(BaseModel):
    """Main settings model for GetScrapper."""
    
    session: SessionConfig = Field(default_factory=SessionConfig)
    parser: ParserConfig = Field(default_factory=ParserConfig)
    processor: ProcessorConfig = Field(default_factory=ProcessorConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Global settings
    output_dir: str = Field(default="./output", description="Output directory for saved files")
    max_concurrent_requests: int = Field(default=5, ge=1, le=50, description="Maximum concurrent requests")
    continue_on_error: bool = Field(default=True, description="Whether to continue on errors")
    
    class Config:
        env_prefix = "GETSCRAPPER_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_file(cls, config_file: str) -> "Settings":
        """
        Load settings from a configuration file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Settings instance
            
        Raises:
            ConfigurationError: If configuration file is invalid
        """
        try:
            import json
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return cls(**config_data)
            
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_file}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Settings":
        """
        Create settings from a dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Settings instance
        """
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary.
        
        Returns:
            Settings as dictionary
        """
        return self.dict()

    def to_file(self, config_file: str) -> None:
        """
        Save settings to a configuration file.
        
        Args:
            config_file: Path to save configuration file
            
        Raises:
            ConfigurationError: If saving fails
        """
        try:
            import json
            
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")

    def get_scraper_config(self) -> Dict[str, Any]:
        """
        Get configuration for scraper initialization.
        
        Returns:
            Configuration dictionary for scraper
        """
        return {
            "session": self.session.dict(),
            "parser": self.parser.dict(),
            "processor": self.processor.dict(),
            "storage": self.storage.dict(),
            "output_dir": self.output_dir,
        }

    def validate(self) -> None:
        """
        Validate settings configuration.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Check if output directory is writable
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            test_file = os.path.join(self.output_dir, ".test_write")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            raise ConfigurationError(f"Output directory is not writable: {str(e)}")

    def __str__(self) -> str:
        """String representation of settings."""
        return f"Settings(output_dir={self.output_dir}, max_concurrent={self.max_concurrent_requests})"


# Default settings instance
default_settings = Settings()