"""Tests for main scraper class."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from getscrapper.core.scraper import Scraper
from getscrapper.utils.exceptions import GetScrapperError, ParsingError


class TestScraper:
    """Test Scraper class."""

    def test_init_default_config(self, temp_dir):
        """Test scraper initialization with default config."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        assert scraper.output_dir == temp_dir
        assert scraper.session_manager is not None
        assert scraper.html_parser is not None
        assert scraper.json_parser is not None
        assert scraper.data_processor is not None
        assert scraper.csv_storage is not None
        assert scraper.json_storage is not None

    def test_init_custom_config(self, temp_dir):
        """Test scraper initialization with custom config."""
        config = {
            "output_dir": temp_dir,
            "session": {"timeout": 60, "retries": 5},
            "parser": {"encoding": "latin-1"},
            "processor": {"auto_clean": False},
            "storage": {"csv_encoding": "utf-16"}
        }
        scraper = Scraper(config)
        
        assert scraper.output_dir == temp_dir
        assert scraper.session_manager.timeout == 60
        assert scraper.session_manager.retries == 5

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_url_html(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping HTML URL."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        results = scraper.scrape_url("https://example.com")
        
        assert len(results) == 1
        assert results[0]["url"] == "https://example.com"
        assert results[0]["content_type"] == "text/html"
        assert results[0]["status_code"] == 200
        assert results[0]["type"] == "page_info"

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_url_json(self, mock_session_manager, sample_json, temp_dir):
        """Test scraping JSON URL."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_json
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        results = scraper.scrape_url("https://api.example.com/data", parser_type="json")
        
        assert len(results) == 1
        assert results[0]["url"] == "https://api.example.com/data"
        assert results[0]["content_type"] == "application/json"
        assert results[0]["status_code"] == 200

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_url_with_selectors(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping with CSS selectors."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        selectors = {"title": "h1", "content": ".content p"}
        results = scraper.scrape_url("https://example.com", selectors=selectors)
        
        assert len(results) >= 2  # Should have results for each selector
        assert any(r["field"] == "title" for r in results)
        assert any(r["field"] == "content" for r in results)

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_url_with_extraction_options(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping with extraction options."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        results = scraper.scrape_url(
            "https://example.com",
            extract_links=True,
            extract_images=True,
            extract_meta=True
        )
        
        # Should have extracted elements (page_info is not included when specific extractions are requested)
        assert len(results) >= 1

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_url_with_processing(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping with data processing."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        results = scraper.scrape_url("https://example.com", process_data=True)
        
        assert len(results) == 1
        # Should have processing metadata
        assert "_processed_at" in results[0]
        assert "_processor_version" in results[0]

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_url_without_processing(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping without data processing."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        results = scraper.scrape_url("https://example.com", process_data=False)
        
        assert len(results) == 1
        # Should not have processing metadata
        assert "_processed_at" not in results[0]
        assert "_processor_version" not in results[0]

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_url_with_save(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping with data saving."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        results = scraper.scrape_url(
            "https://example.com",
            save_data=True,
            output_format="json"
        )
        
        assert len(results) == 1
        # Check if file was created
        files = os.listdir(temp_dir)
        assert len(files) == 1
        assert files[0].endswith('.json')

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_urls(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping multiple URLs."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        urls = ["https://example.com", "https://example.com/page2"]
        results = scraper.scrape_urls(urls)
        
        assert len(results) == 2
        assert results[0]["url"] == "https://example.com"
        assert results[1]["url"] == "https://example.com/page2"

    @patch('getscrapper.core.scraper.SessionManager')
    def test_scrape_urls_with_continue_on_error(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping multiple URLs with continue on error."""
        # Mock session manager
        mock_session = Mock()
        mock_session_manager.return_value = mock_session
        
        # First call succeeds, second fails
        def side_effect(url, **kwargs):
            if "page2" in url:
                raise GetScrapperError("Failed to scrape page2")
            mock_response = Mock()
            mock_response.text = sample_html
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.status_code = 200
            return mock_response
        
        mock_session.get.side_effect = side_effect
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        urls = ["https://example.com", "https://example.com/page2"]
        results = scraper.scrape_urls(urls, continue_on_error=True)
        
        # Should have results from first URL only
        assert len(results) == 1
        assert results[0]["url"] == "https://example.com"

    def test_scrape_from_file(self, temp_dir):
        """Test scraping URLs from file."""
        # Create test file with URLs
        urls_file = os.path.join(temp_dir, "urls.txt")
        with open(urls_file, 'w') as f:
            f.write("https://example.com\n")
            f.write("https://example.com/page2\n")
        
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        with patch.object(scraper, 'scrape_urls') as mock_scrape_urls:
            mock_scrape_urls.return_value = []
            scraper.scrape_from_file(urls_file)
            mock_scrape_urls.assert_called_once_with(
                ["https://example.com", "https://example.com/page2"]
            )

    def test_scrape_from_nonexistent_file(self, temp_dir):
        """Test scraping from nonexistent file."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        nonexistent_file = os.path.join(temp_dir, "nonexistent.txt")
        
        with pytest.raises(GetScrapperError, match="Failed to read URLs from file"):
            scraper.scrape_from_file(nonexistent_file)

    def test_generate_filename(self, temp_dir):
        """Test filename generation."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Test basic URL
        filename = scraper._generate_filename("https://example.com", "json")
        assert filename == "example.com.json"
        
        # Test URL with path
        filename = scraper._generate_filename("https://example.com/path/page", "csv")
        assert filename == "example.com_path/page.csv"
        
        # Test URL with query parameters
        filename = scraper._generate_filename("https://example.com?param=value", "json")
        assert "example.com" in filename
        assert filename.endswith(".json")

    def test_get_scraping_stats(self, temp_dir):
        """Test getting scraping statistics."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        stats = scraper.get_scraping_stats()
        
        assert "session_info" in stats
        assert "output_directory" in stats
        assert "supported_parsers" in stats
        assert "supported_formats" in stats
        assert stats["output_directory"] == temp_dir

    def test_context_manager(self, temp_dir):
        """Test scraper as context manager."""
        config = {"output_dir": temp_dir}
        
        with Scraper(config) as scraper:
            assert scraper.session_manager is not None
        
        # Session should be closed after context exit

    def test_close(self, temp_dir):
        """Test scraper closing."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        scraper.close()
        # Scraper should be closed (structure is correct)