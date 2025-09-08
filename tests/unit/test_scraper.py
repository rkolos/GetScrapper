"""Tests for main scraper class."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from getscrapper.core.scraper import Scraper
from getscrapper.utils.exceptions import GetScrapperError, ParsingError


class TestScraper:
    """Test Scraper class."""

    def test_init_default_config(self, temp_dir):
        """Test scraper initialization with default config."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        assert scraper.output_dir == temp_dir
        assert scraper.detection_controller is not None
        assert scraper.html_parser is not None
        assert scraper.json_parser is not None
        assert scraper.data_processor is not None
        assert scraper.csv_storage is not None
        assert scraper.json_storage is not None

    def test_init_custom_config(self, temp_dir):
        """Test scraper initialization with custom config."""
        config = {
            "output_dir": temp_dir,
            "detection_controller": {"default_timeout": 60, "max_retries": 5},
            "parser": {"encoding": "latin-1"},
            "processor": {"auto_clean": False},
            "storage": {"csv_encoding": "utf-16"}
        }
        scraper = Scraper(config)
        
        assert scraper.output_dir == temp_dir
        assert scraper.detection_controller is not None

    @pytest.mark.asyncio
    async def test_scrape_url_html(self, sample_html, temp_dir):
        """Test scraping HTML URL."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller
        mock_fetch_result = {
            'html_content': sample_html,
            'content_type': 'text/html',
            'status_code': 200,
            'escalation_level': 'static'
        }
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(return_value=mock_fetch_result)
        
        results = await scraper.scrape_url("https://example.com")
        
        assert len(results) == 1
        assert results[0]["url"] == "https://example.com"
        assert results[0]["content_type"] == "text/html"
        assert results[0]["status_code"] == 200
        assert results[0]["type"] == "page_info"

    @pytest.mark.asyncio
    async def test_scrape_url_json(self, sample_json, temp_dir):
        """Test scraping JSON URL."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller
        mock_fetch_result = {
            'html_content': sample_json,
            'content_type': 'application/json',
            'status_code': 200,
            'escalation_level': 'static'
        }
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(return_value=mock_fetch_result)
        
        results = await scraper.scrape_url("https://api.example.com/data", parser_type="json")
        
        assert len(results) == 1
        assert results[0]["url"] == "https://api.example.com/data"
        assert results[0]["content_type"] == "text/html"
        assert results[0]["status_code"] == 200

    @pytest.mark.asyncio
    async def test_scrape_url_with_selectors(self, sample_html, temp_dir):
        """Test scraping with CSS selectors."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller
        mock_fetch_result = {
            'html_content': sample_html,
            'content_type': 'text/html',
            'status_code': 200,
            'escalation_level': 'static'
        }
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(return_value=mock_fetch_result)
        
        selectors = {"title": "h1", "content": ".content p"}
        results = await scraper.scrape_url("https://example.com", selectors=selectors)
        
        assert len(results) >= 2  # Should have results for each selector
        assert any(r["field"] == "title" for r in results)
        assert any(r["field"] == "content" for r in results)

    @pytest.mark.asyncio
    async def test_scrape_url_with_extraction_options(self, sample_html, temp_dir):
        """Test scraping with extraction options."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller
        mock_fetch_result = {
            'html_content': sample_html,
            'content_type': 'text/html',
            'status_code': 200,
            'escalation_level': 'static'
        }
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(return_value=mock_fetch_result)
        
        results = await scraper.scrape_url(
            "https://example.com",
            extract_links=True,
            extract_images=True,
            extract_meta=True
        )
        
        # Should have extracted elements (page_info is not included when specific extractions are requested)
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_scrape_url_with_processing(self, sample_html, temp_dir):
        """Test scraping with data processing."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller
        mock_fetch_result = {
            'html_content': sample_html,
            'content_type': 'text/html',
            'status_code': 200,
            'escalation_level': 'static'
        }
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(return_value=mock_fetch_result)
        
        results = await scraper.scrape_url("https://example.com", process_data=True)
        
        assert len(results) == 1
        # Should have processing metadata
        assert "_processed_at" in results[0]
        assert "_processor_version" in results[0]

    @pytest.mark.asyncio
    async def test_scrape_url_without_processing(self, sample_html, temp_dir):
        """Test scraping without data processing."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller
        mock_fetch_result = {
            'html_content': sample_html,
            'content_type': 'text/html',
            'status_code': 200,
            'escalation_level': 'static'
        }
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(return_value=mock_fetch_result)
        
        results = await scraper.scrape_url("https://example.com", process_data=False)
        
        assert len(results) == 1
        # Should not have processing metadata
        assert "_processed_at" not in results[0]
        assert "_processor_version" not in results[0]

    @pytest.mark.asyncio
    async def test_scrape_url_with_save(self, sample_html, temp_dir):
        """Test scraping with data saving."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller
        mock_fetch_result = {
            'html_content': sample_html,
            'content_type': 'text/html',
            'status_code': 200,
            'escalation_level': 'static'
        }
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(return_value=mock_fetch_result)
        
        results = await scraper.scrape_url(
            "https://example.com",
            save_data=True,
            output_format="json"
        )
        
        assert len(results) == 1
        # Check if file was created
        files = os.listdir(temp_dir)
        assert len(files) == 1
        assert files[0].endswith('.json')

    @pytest.mark.asyncio
    async def test_scrape_urls(self, sample_html, temp_dir):
        """Test scraping multiple URLs."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller
        mock_fetch_result = {
            'html_content': sample_html,
            'content_type': 'text/html',
            'status_code': 200,
            'escalation_level': 'static'
        }
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(return_value=mock_fetch_result)
        
        urls = ["https://example.com", "https://example.com/page2"]
        results = await scraper.scrape_urls(urls)
        
        assert len(results) == 2
        assert results[0]["url"] == "https://example.com"
        assert results[1]["url"] == "https://example.com/page2"

    @pytest.mark.asyncio
    async def test_scrape_urls_with_continue_on_error(self, sample_html, temp_dir):
        """Test scraping multiple URLs with continue on error."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Mock detection controller with side effect
        def side_effect(url, **kwargs):
            if "page2" in url:
                return {'error': 'Failed to scrape page2', 'html_content': ''}
            return {
                'html_content': sample_html,
                'content_type': 'text/html',
                'status_code': 200,
                'escalation_level': 'static'
            }
        
        scraper.detection_controller.fetch_html_with_escalation = AsyncMock(side_effect=side_effect)
        
        urls = ["https://example.com", "https://example.com/page2"]
        results = await scraper.scrape_urls(urls, continue_on_error=True)
        
        # Should have results from first URL only
        assert len(results) == 1
        assert results[0]["url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_scrape_from_file(self, temp_dir):
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
            await scraper.scrape_from_file(urls_file)
            mock_scrape_urls.assert_called_once_with(
                ["https://example.com", "https://example.com/page2"]
            )

    @pytest.mark.asyncio
    async def test_scrape_from_nonexistent_file(self, temp_dir):
        """Test scraping from nonexistent file."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        nonexistent_file = os.path.join(temp_dir, "nonexistent.txt")
        
        with pytest.raises(GetScrapperError, match="Failed to read URLs from file"):
            await scraper.scrape_from_file(nonexistent_file)

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
        
        assert "detection_controller_info" in stats
        assert "available_strategies" in stats
        assert "output_directory" in stats
        assert "supported_parsers" in stats
        assert "supported_formats" in stats
        assert stats["output_directory"] == temp_dir

    def test_context_manager(self, temp_dir):
        """Test scraper as context manager."""
        config = {"output_dir": temp_dir}
        
        with Scraper(config) as scraper:
            assert scraper.detection_controller is not None
        
        # Detection controller should be closed after context exit

    def test_close(self, temp_dir):
        """Test scraper closing."""
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        scraper.close()
        # Scraper should be closed (structure is correct)