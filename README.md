# GetScrapper

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

A powerful and flexible web scraping tool for extracting structured data from websites and APIs. GetScrapper provides a comprehensive solution for web scraping with support for various data extraction methods, processing pipelines, and output formats.

## Features

- **Multiple Parser Support**: HTML parsing with BeautifulSoup and JSON parsing
- **Flexible Data Extraction**: CSS selectors, XPath, and custom extraction methods
- **Data Processing**: Automatic cleaning, validation, and transformation
- **Multiple Output Formats**: CSV, JSON, and custom formats
- **Session Management**: Advanced HTTP session handling with retries and rate limiting
- **Configuration System**: Flexible configuration with environment variables and config files
- **Command Line Interface**: Easy-to-use CLI for quick scraping tasks
- **Comprehensive Testing**: Full test coverage with unit and integration tests
- **Error Handling**: Robust error handling and logging

## Installation

### From Source

```bash
git clone https://github.com/yourusername/getscrapper.git
cd getscrapper
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/getscrapper.git
cd getscrapper
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Scrape a single URL
getscrapper scrape https://example.com

# Scrape with CSS selectors
getscrapper scrape https://example.com --selectors '{"title": "h1", "content": ".content p"}'

# Scrape multiple URLs
getscrapper scrape-multiple https://example.com https://example.com/page2

# Scrape from file
echo "https://example.com" > urls.txt
getscrapper scrape-multiple --file urls.txt

# Save results to file
getscrapper scrape https://example.com --save --output-format csv

# Extract specific elements
getscrapper scrape https://example.com --extract-links --extract-images --extract-meta
```

### Python API Usage

```python
from getscrapper import Scraper

# Initialize scraper
scraper = Scraper()

# Scrape a single URL
results = scraper.scrape_url("https://example.com")
print(f"Scraped {len(results)} items")

# Scrape with CSS selectors
selectors = {
    "title": "h1",
    "content": ".content p",
    "prices": ".product .price"
}
results = scraper.scrape_url("https://example.com", selectors=selectors)

# Scrape multiple URLs
urls = ["https://example.com", "https://example.com/page2"]
results = scraper.scrape_urls(urls)

# Scrape with data processing and saving
results = scraper.scrape_url(
    "https://example.com",
    selectors=selectors,
    process_data=True,
    save_data=True,
    output_format="json"
)
```

## Configuration

### Environment Variables

```bash
export GETSCRAPPER_SESSION_TIMEOUT=30
export GETSCRAPPER_SESSION_RETRIES=3
export GETSCRAPPER_SESSION_DELAY=1.0
export GETSCRAPPER_PARSER_ENCODING=utf-8
export GETSCRAPPER_PROCESSOR_AUTO_CLEAN=true
export GETSCRAPPER_STORAGE_CSV_ENCODING=utf-8
export GETSCRAPPER_LOG_LEVEL=INFO
```

### Configuration File

```json
{
  "session": {
    "timeout": 30,
    "retries": 3,
    "delay": 1.0,
    "user_agent": "GetScrapper/1.0.0"
  },
  "parser": {
    "html_parser": "lxml",
    "encoding": "utf-8",
    "extract_text": true,
    "clean_text": true
  },
  "processor": {
    "auto_clean": true,
    "validate_data": true,
    "transform_dates": true,
    "extract_numbers": false
  },
  "storage": {
    "csv_encoding": "utf-8",
    "csv_delimiter": ",",
    "json_indent": 2
  },
  "logging": {
    "level": "INFO",
    "log_file": null
  },
  "output_dir": "./output",
  "max_concurrent_requests": 5,
  "continue_on_error": true
}
```

## Advanced Usage

### Custom Parsers

```python
from getscrapper.parsers import BaseParser

class CustomParser(BaseParser):
    def parse(self, content, **kwargs):
        # Custom parsing logic
        return [{"data": "parsed"}]
    
    def _validate_config(self):
        # Validate configuration
        pass

# Use custom parser
scraper = Scraper()
scraper.custom_parser = CustomParser()
```

### Data Processing

```python
from getscrapper.processors import DataProcessor

processor = DataProcessor({
    "auto_clean": True,
    "validate_data": True,
    "transform_dates": True,
    "extract_numbers": True
})

# Process data
processed_data = processor.process(raw_data)

# Filter data
filtered_data = processor.filter_data(data, {"price": {"min": 10, "max": 100}})

# Group data
grouped_data = processor.group_data(data, "category")

# Aggregate data
aggregated = processor.aggregate_data(data, {
    "price": "avg",
    "count": "count"
})
```

### Custom Storage

```python
from getscrapper.storage import BaseStorage

class CustomStorage(BaseStorage):
    def save(self, data, output_path):
        # Custom saving logic
        pass
    
    def load(self, input_path):
        # Custom loading logic
        return []

# Use custom storage
scraper = Scraper()
scraper.custom_storage = CustomStorage()
```

## Examples

### E-commerce Product Scraping

```python
from getscrapper import Scraper

scraper = Scraper()

# Scrape product information
selectors = {
    "name": ".product-title",
    "price": ".price",
    "description": ".product-description",
    "rating": ".rating",
    "availability": ".availability"
}

results = scraper.scrape_url(
    "https://shop.example.com/product/123",
    selectors=selectors,
    process_data=True,
    save_data=True,
    output_format="csv"
)
```

### API Data Extraction

```python
from getscrapper import Scraper

scraper = Scraper()

# Scrape JSON API
results = scraper.scrape_url(
    "https://api.example.com/data",
    parser_type="json",
    path="users",
    extract_arrays=True,
    process_data=True
)
```

### News Article Scraping

```python
from getscrapper import Scraper

scraper = Scraper()

# Scrape news articles
results = scraper.scrape_url(
    "https://news.example.com/article",
    selectors={
        "headline": "h1.headline",
        "author": ".author",
        "date": ".publish-date",
        "content": ".article-content p"
    },
    extract_meta=True,
    process_data=True
)
```

## Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/unit/test_scraper.py -v
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/getscrapper.git
cd getscrapper

# Install in development mode
make install-dev

# Setup pre-commit hooks
make dev-setup
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run all checks
make check
```

### Building

```bash
# Build package
make build

# Clean build artifacts
make clean
```

## API Reference

### Scraper Class

The main `Scraper` class provides the core functionality for web scraping.

#### Methods

- `scrape_url(url, **kwargs)`: Scrape a single URL
- `scrape_urls(urls, **kwargs)`: Scrape multiple URLs
- `scrape_from_file(file_path, **kwargs)`: Scrape URLs from a file
- `get_scraping_stats()`: Get scraping statistics

#### Parameters

- `url`: URL to scrape
- `parser_type`: Type of parser ('html' or 'json')
- `selectors`: CSS selectors for data extraction
- `extract_links`: Whether to extract links
- `extract_images`: Whether to extract images
- `extract_meta`: Whether to extract meta tags
- `process_data`: Whether to process the data
- `save_data`: Whether to save the data
- `output_format`: Output format ('csv' or 'json')

### Configuration Classes

- `SessionConfig`: HTTP session configuration
- `ParserConfig`: Parser configuration
- `ProcessorConfig`: Data processor configuration
- `StorageConfig`: Storage configuration
- `LoggingConfig`: Logging configuration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0

- Initial release
- HTML and JSON parsing support
- CSS selector extraction
- Data processing and validation
- CSV and JSON output formats
- Command line interface
- Comprehensive test suite
- Configuration system
- Session management with retries and rate limiting

## Support

For support, please open an issue on GitHub or contact the maintainers.

## Roadmap

- [ ] Selenium integration for JavaScript-heavy sites
- [ ] Database storage support
- [ ] Distributed scraping capabilities
- [ ] Web interface for configuration
- [ ] Plugin system for custom parsers
- [ ] Advanced data transformation pipelines
- [ ] Real-time monitoring and metrics