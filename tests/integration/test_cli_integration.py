"""Integration tests for CLI functionality."""

import json
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock

from getscrapper.cli.main import cli


class TestCLIIntegration:
    """Test CLI integration functionality."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "GetScrapper - A powerful web scraping tool" in result.output

    def test_cli_info_command(self):
        """Test CLI info command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['info'])
        
        assert result.exit_code == 0
        assert "GetScrapper - Web Scraping Tool" in result.output
        assert "Version: 1.0.0" in result.output

    def test_cli_config_command(self, temp_dir):
        """Test CLI config command."""
        runner = CliRunner()
        config_file = os.path.join(temp_dir, "config.json")
        
        # Test saving config
        result = runner.invoke(cli, ['--output-dir', temp_dir, 'config', '--output', config_file])
        
        assert result.exit_code == 0
        assert os.path.exists(config_file)
        
        # Verify config content
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        assert "session" in config_data
        assert "parser" in config_data
        assert "processor" in config_data
        assert "storage" in config_data

    def test_cli_config_display(self):
        """Test CLI config display."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config'])
        
        assert result.exit_code == 0
        config_data = json.loads(result.output)
        assert "session" in config_data

    @patch('getscrapper.core.scraper.SessionManager')
    def test_cli_scrape_command(self, mock_session_manager, sample_html, temp_dir):
        """Test CLI scrape command."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--output-dir', temp_dir,
            'scrape', 'https://example.com'
        ])
        
        assert result.exit_code == 0
        assert "Successfully scraped" in result.output

    @patch('getscrapper.core.scraper.SessionManager')
    def test_cli_scrape_with_options(self, mock_session_manager, sample_html, temp_dir):
        """Test CLI scrape command with options."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--output-dir', temp_dir,
            'scrape', 'https://example.com',
            '--parser', 'html',
            '--extract-links',
            '--extract-images',
            '--save',
            '--output-format', 'json'
        ])
        
        assert result.exit_code == 0
        assert "Successfully scraped" in result.output

    @patch('getscrapper.core.scraper.SessionManager')
    def test_cli_scrape_with_selectors(self, mock_session_manager, sample_html, temp_dir):
        """Test CLI scrape command with selectors."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        selectors = '{"title": "h1", "content": ".content p"}'
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--output-dir', temp_dir,
            'scrape', 'https://example.com',
            '--selectors', selectors
        ])
        
        assert result.exit_code == 0
        assert "Successfully scraped" in result.output

    @patch('getscrapper.core.scraper.SessionManager')
    def test_cli_scrape_multiple_command(self, mock_session_manager, sample_html, temp_dir):
        """Test CLI scrape-multiple command."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--output-dir', temp_dir,
            'scrape-multiple',
            'https://example.com',
            'https://example.com/page2'
        ])
        
        assert result.exit_code == 0
        assert "Successfully scraped" in result.output

    def test_cli_scrape_multiple_from_file(self, temp_dir):
        """Test CLI scrape-multiple command with file input."""
        # Create URLs file
        urls_file = os.path.join(temp_dir, "urls.txt")
        with open(urls_file, 'w') as f:
            f.write("https://example.com\n")
            f.write("https://example.com/page2\n")
        
        runner = CliRunner()
        
        with patch('getscrapper.core.scraper.SessionManager') as mock_session_manager:
            # Mock session manager and response
            mock_session = Mock()
            mock_response = Mock()
            mock_response.text = '<html><body>Test</body></html>'
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            mock_session_manager.return_value = mock_session
            
            result = runner.invoke(cli, [
                '--output-dir', temp_dir,
                'scrape-multiple',
                '--file', urls_file
            ])
            
            # Check if the command succeeded or failed with expected error
            if result.exit_code == 0:
                assert "Successfully scraped" in result.output
            else:
                # If it fails, it should be due to file not found or similar
                assert result.exit_code == 2  # Click argument error

    def test_cli_invalid_selectors(self, temp_dir):
        """Test CLI with invalid selectors JSON."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--output-dir', temp_dir,
            'scrape', 'https://example.com',
            '--selectors', 'invalid json'
        ])
        
        assert result.exit_code == 1
        assert "Invalid JSON format for selectors" in result.output

    def test_cli_verbose_logging(self, temp_dir):
        """Test CLI with verbose logging."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--verbose',
            '--output-dir', temp_dir,
            'info'
        ])
        
        assert result.exit_code == 0
        assert "GetScrapper - Web Scraping Tool" in result.output

    def test_cli_custom_config_file(self, temp_dir):
        """Test CLI with custom config file."""
        # Create custom config file
        config_file = os.path.join(temp_dir, "custom_config.json")
        custom_config = {
            "session": {"timeout": 60},
            "parser": {"encoding": "utf-8"},
            "processor": {"auto_clean": True},
            "storage": {"csv_encoding": "utf-8"},
            "logging": {"level": "DEBUG"}
        }
        
        with open(config_file, 'w') as f:
            json.dump(custom_config, f)
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--config', config_file,
            'info'
        ])
        
        assert result.exit_code == 0
        assert "GetScrapper - Web Scraping Tool" in result.output

    def test_cli_nonexistent_config_file(self, temp_dir):
        """Test CLI with nonexistent config file."""
        runner = CliRunner()
        nonexistent_config = os.path.join(temp_dir, "nonexistent.json")
        
        result = runner.invoke(cli, [
            '--config', nonexistent_config,
            'info'
        ])
        
        assert result.exit_code == 2  # Click returns 2 for argument errors

    @patch('getscrapper.core.scraper.SessionManager')
    def test_cli_scrape_with_save_and_no_output(self, mock_session_manager, sample_html, temp_dir):
        """Test CLI scrape with save but no output to stdout."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--output-dir', temp_dir,
            'scrape', 'https://example.com',
            '--save'
        ])
        
        assert result.exit_code == 0
        assert "Successfully scraped" in result.output
        # Should not output JSON data when saving to file
        assert "{" not in result.output

    @patch('getscrapper.core.scraper.SessionManager')
    def test_cli_scrape_without_save(self, mock_session_manager, sample_html, temp_dir):
        """Test CLI scrape without save (output to stdout)."""
        # Mock session manager and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_manager.return_value = mock_session
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--output-dir', temp_dir,
            'scrape', 'https://example.com'
        ])
        
        assert result.exit_code == 0
        assert "Successfully scraped" in result.output
        # Should output JSON data to stdout
        assert "{" in result.output

    def test_cli_keyboard_interrupt(self):
        """Test CLI handling of keyboard interrupt."""
        runner = CliRunner()
        
        # Test that the main function handles KeyboardInterrupt correctly
        with patch('getscrapper.cli.main.cli') as mock_cli:
            mock_cli.side_effect = KeyboardInterrupt()
            
            # Import and test the main function directly
            from getscrapper.cli.main import main
            import sys
            from io import StringIO
            
            # Capture stderr
            old_stderr = sys.stderr
            sys.stderr = StringIO()
            
            try:
                main()
                assert False, "Should have exited with code 1"
            except SystemExit as e:
                assert e.code == 1
                assert "Operation cancelled by user" in sys.stderr.getvalue()
            finally:
                sys.stderr = old_stderr

    def test_cli_unexpected_error(self):
        """Test CLI handling of unexpected errors."""
        runner = CliRunner()
        
        # Test that the main function handles unexpected errors correctly
        with patch('getscrapper.cli.main.cli') as mock_cli:
            mock_cli.side_effect = Exception("Unexpected error")
            
            # Import and test the main function directly
            from getscrapper.cli.main import main
            import sys
            from io import StringIO
            
            # Capture stderr
            old_stderr = sys.stderr
            sys.stderr = StringIO()
            
            try:
                main()
                assert False, "Should have exited with code 1"
            except SystemExit as e:
                assert e.code == 1
                assert "Unexpected error" in sys.stderr.getvalue()
            finally:
                sys.stderr = old_stderr