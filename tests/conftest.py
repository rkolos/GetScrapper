"""Pytest configuration and fixtures."""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from getscrapper.config.settings import Settings
from getscrapper.core.scraper import Scraper
from getscrapper.parsers.html_parser import HTMLParser
from getscrapper.parsers.json_parser import JSONParser
from getscrapper.storage.csv_storage import CSVStorage
from getscrapper.storage.json_storage import JSONStorage


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="A test page for scraping">
        <meta name="keywords" content="test, scraping, example">
    </head>
    <body>
        <h1>Welcome to Test Page</h1>
        <div class="content">
            <p>This is a test paragraph with some content.</p>
            <a href="https://example.com">Example Link</a>
            <img src="test.jpg" alt="Test Image" width="100" height="100">
        </div>
        <div class="products">
            <div class="product">
                <h3>Product 1</h3>
                <span class="price">$19.99</span>
            </div>
            <div class="product">
                <h3>Product 2</h3>
                <span class="price">$29.99</span>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_json():
    """Sample JSON content for testing."""
    return json.dumps({
        "users": [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ],
        "products": [
            {"id": 1, "name": "Product 1", "price": 19.99},
            {"id": 2, "name": "Product 2", "price": 29.99}
        ],
        "metadata": {
            "total_users": 2,
            "total_products": 2,
            "last_updated": "2023-01-01T00:00:00Z"
        }
    })


@pytest.fixture
def sample_data():
    """Sample scraped data for testing."""
    return [
        {
            "url": "https://example.com",
            "title": "Test Page",
            "content": "This is test content",
            "metadata": {"scraped_at": "2023-01-01T00:00:00Z"}
        },
        {
            "url": "https://example.com/page2",
            "title": "Test Page 2",
            "content": "This is more test content",
            "metadata": {"scraped_at": "2023-01-01T00:01:00Z"}
        }
    ]


@pytest.fixture
def settings():
    """Default settings for testing."""
    return Settings()


@pytest.fixture
def html_parser():
    """HTML parser instance for testing."""
    return HTMLParser()


@pytest.fixture
def json_parser():
    """JSON parser instance for testing."""
    return JSONParser()


@pytest.fixture
def csv_storage():
    """CSV storage instance for testing."""
    return CSVStorage()


@pytest.fixture
def json_storage():
    """JSON storage instance for testing."""
    return JSONStorage()


@pytest.fixture
def scraper_config(temp_dir):
    """Scraper configuration for testing."""
    return {
        "output_dir": temp_dir,
        "session": {
            "timeout": 10,
            "retries": 1,
            "delay": 0.1
        }
    }


@pytest.fixture
def scraper(scraper_config):
    """Scraper instance for testing."""
    return Scraper(scraper_config)