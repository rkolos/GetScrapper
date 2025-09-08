"""End-to-end integration tests for GetScrapper."""

import json
import os
import pytest
from unittest.mock import patch, Mock

from getscrapper.core.scraper import Scraper
from getscrapper.config.settings import Settings


class TestEndToEndScraping:
    """Test complete scraping workflows."""

    @patch('getscrapper.core.scraper.SessionManager')
    def test_html_scraping_workflow(self, mock_session_manager, sample_html, temp_dir):
        """Test complete HTML scraping workflow."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        # Initialize scraper
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Scrape with various options
        results = scraper.scrape_url(
            "https://example.com",
            selectors={"title": "h1", "prices": ".product .price"},
            extract_links=True,
            extract_images=True,
            process_data=True,
            save_data=True,
            output_format="json"
        )
        
        # Verify results
        assert len(results) >= 1
        
        # Check that file was saved
        files = os.listdir(temp_dir)
        assert len(files) == 1
        assert files[0].endswith('.json')
        
        # Verify saved content
        saved_file = os.path.join(temp_dir, files[0])
        with open(saved_file, 'r') as f:
            saved_data = json.load(f)
        
        assert len(saved_data) >= 1
        assert saved_data[0]["url"] == "https://example.com"

    @patch('getscrapper.core.scraper.SessionManager')
    def test_json_scraping_workflow(self, mock_session_manager, sample_json, temp_dir):
        """Test complete JSON scraping workflow."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_json
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        # Initialize scraper
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Scrape JSON data
        results = scraper.scrape_url(
            "https://api.example.com/data",
            parser_type="json",
            path="users",
            extract_arrays=True,
            process_data=True,
            save_data=True,
            output_format="csv"
        )
        
        # Verify results
        assert len(results) >= 1
        
        # Check that file was saved
        files = os.listdir(temp_dir)
        assert len(files) == 1
        assert files[0].endswith('.csv')

    @patch('getscrapper.core.scraper.SessionManager')
    def test_multiple_urls_workflow(self, mock_session_manager, sample_html, temp_dir):
        """Test scraping multiple URLs workflow."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        # Initialize scraper
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Scrape multiple URLs
        urls = [
            "https://example.com",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        results = scraper.scrape_urls(
            urls,
            selectors={"title": "h1"},
            process_data=True,
            save_data=True,
            output_format="json"
        )
        
        # Verify results
        assert len(results) >= 3
        
        # Check that files were saved
        files = os.listdir(temp_dir)
        assert len(files) == 3
        
        # Verify each file contains data
        for file in files:
            file_path = os.path.join(temp_dir, file)
            with open(file_path, 'r') as f:
                data = json.load(f)
            assert len(data) >= 1

    def test_file_based_url_scraping(self, temp_dir):
        """Test scraping URLs from file."""
        # Create URLs file
        urls_file = os.path.join(temp_dir, "urls.txt")
        with open(urls_file, 'w') as f:
            f.write("https://example.com\n")
            f.write("https://example.com/page2\n")
        
        # Initialize scraper
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        with patch.object(scraper, 'scrape_urls') as mock_scrape_urls:
            mock_scrape_urls.return_value = []
            scraper.scrape_from_file(urls_file)
            mock_scrape_urls.assert_called_once()

    @patch('getscrapper.core.scraper.SessionManager')
    def test_error_handling_workflow(self, mock_session_manager, temp_dir):
        """Test error handling in scraping workflow."""
        # Mock session manager to raise error
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Network error")
        mock_session_manager.return_value = mock_session
        
        # Initialize scraper
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Should raise GetScrapperError
        with pytest.raises(Exception):
            scraper.scrape_url("https://example.com")

    def test_settings_integration(self, temp_dir):
        """Test integration with settings system."""
        # Create custom settings
        settings = Settings()
        settings.output_dir = temp_dir
        settings.session.timeout = 60
        settings.parser.encoding = "utf-8"
        
        # Initialize scraper with settings
        scraper = Scraper(settings.get_scraper_config())
        
        # Verify settings were applied
        assert scraper.output_dir == temp_dir
        assert scraper.session_manager.timeout == 60

    @patch('getscrapper.core.scraper.SessionManager')
    def test_data_processing_integration(self, mock_session_manager, sample_html, temp_dir):
        """Test integration with data processing."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        # Initialize scraper with custom processor config
        config = {
            "output_dir": temp_dir,
            "processor": {
                "auto_clean": True,
                "validate_data": True,
                "transform_dates": True,
                "extract_numbers": True
            }
        }
        scraper = Scraper(config)
        
        # Scrape with processing
        results = scraper.scrape_url(
            "https://example.com",
            process_data=True
        )
        
        # Verify processing was applied
        assert len(results) == 1
        result = results[0]
        assert "_processed_at" in result
        assert "_processor_version" in result
        assert "_validation" in result

    @patch('getscrapper.core.scraper.SessionManager')
    def test_storage_integration(self, mock_session_manager, sample_data, temp_dir):
        """Test integration with storage systems."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = '<html><body>Test</body></html>'
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        # Initialize scraper
        config = {"output_dir": temp_dir}
        scraper = Scraper(config)
        
        # Test CSV storage
        scraper.scrape_url(
            "https://example.com",
            save_data=True,
            output_format="csv"
        )
        
        # Test JSON storage
        scraper.scrape_url(
            "https://example.com/page2",
            save_data=True,
            output_format="json"
        )
        
        # Verify both files were created
        files = os.listdir(temp_dir)
        csv_files = [f for f in files if f.endswith('.csv')]
        json_files = [f for f in files if f.endswith('.json')]
        
        assert len(csv_files) == 1
        assert len(json_files) == 1

    def test_scraper_context_manager(self, temp_dir):
        """Test scraper as context manager."""
        config = {"output_dir": temp_dir}
        
        with Scraper(config) as scraper:
            assert scraper.session_manager is not None
            assert scraper.output_dir == temp_dir
        
        # Scraper should be properly closed

    @patch('getscrapper.core.scraper.SessionManager')
    def test_comprehensive_scraping_scenario(self, mock_session_manager, sample_html, temp_dir):
        """Test comprehensive scraping scenario with all features."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        # Initialize scraper with comprehensive config
        config = {
            "output_dir": temp_dir,
            "session": {
                "timeout": 30,
                "retries": 3,
                "delay": 1.0
            },
            "parser": {
                "encoding": "utf-8",
                "extract_text": True,
                "clean_text": True
            },
            "processor": {
                "auto_clean": True,
                "validate_data": True,
                "transform_dates": True,
                "extract_numbers": True
            },
            "storage": {
                "csv_encoding": "utf-8",
                "json_indent": 2
            }
        }
        
        with Scraper(config) as scraper:
            # Test comprehensive scraping
            results = scraper.scrape_url(
                "https://example.com",
                selectors={
                    "title": "h1",
                    "content": ".content p",
                    "prices": ".product .price"
                },
                extract_links=True,
                extract_images=True,
                extract_meta=True,
                process_data=True,
                save_data=True,
                output_format="json"
            )
            
            # Verify comprehensive results
            assert len(results) >= 1
            
            # Check processing metadata
            result = results[0]
            assert "_processed_at" in result
            assert "_processor_version" in result
            assert "_validation" in result
            
            # Check that file was saved
            files = os.listdir(temp_dir)
            assert len(files) == 1
            assert files[0].endswith('.json')
            
            # Verify saved content
            saved_file = os.path.join(temp_dir, files[0])
            with open(saved_file, 'r') as f:
                saved_data = json.load(f)
            
            assert len(saved_data) >= 1
            assert saved_data[0]["url"] == "https://example.com"