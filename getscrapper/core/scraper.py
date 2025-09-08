"""Main scraper class for GetScrapper."""

import os
from typing import Any, Dict, List, Optional, Union

from .session import SessionManager
from ..parsers.html_parser import HTMLParser
from ..parsers.json_parser import JSONParser
from ..processors.data_processor import DataProcessor
from ..storage.csv_storage import CSVStorage
from ..storage.json_storage import JSONStorage
from ..utils.exceptions import GetScrapperError, ParsingError
from ..utils.logger import setup_logger


class Scraper:
    """Main scraper class for GetScrapper."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize scraper.
        
        Args:
            config: Scraper configuration with keys:
                - session: Session configuration
                - parser: Parser configuration
                - processor: Data processor configuration
                - storage: Storage configuration
                - output_dir: Output directory for saved files
        """
        self.config = config or {}
        self.logger = setup_logger("getscrapper.scraper")
        
        # Initialize components
        self.session_manager = SessionManager(self.config.get("session", {}))
        self.html_parser = HTMLParser(self.config.get("parser", {}))
        self.json_parser = JSONParser(self.config.get("parser", {}))
        self.data_processor = DataProcessor(self.config.get("processor", {}))
        
        # Initialize storage
        self.csv_storage = CSVStorage(self.config.get("storage", {}))
        self.json_storage = JSONStorage(self.config.get("storage", {}))
        
        # Output directory
        self.output_dir = self.config.get("output_dir", "./output")
        os.makedirs(self.output_dir, exist_ok=True)

    def scrape_url(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape a single URL.
        
        Args:
            url: URL to scrape
            **kwargs: Additional scraping parameters:
                - parser_type: Type of parser to use ('html', 'json')
                - selectors: CSS selectors for HTML parsing
                - extract_links: Whether to extract links
                - extract_images: Whether to extract images
                - extract_meta: Whether to extract meta tags
                - process_data: Whether to process the data
                - save_data: Whether to save the data
                - output_format: Output format ('csv', 'json')
                
        Returns:
            List of scraped data dictionaries
        """
        try:
            self.logger.info(f"Scraping URL: {url}")
            
            # Fetch content
            response = self.session_manager.get(url)
            content = response.text
            content_type = response.headers.get('content-type', '').lower()
            
            # Determine parser type
            parser_type = kwargs.get("parser_type")
            if not parser_type:
                if "json" in content_type:
                    parser_type = "json"
                else:
                    parser_type = "html"
            
            # Parse content
            if parser_type == "html":
                parsed_data = self.html_parser.parse(content, **kwargs)
            elif parser_type == "json":
                parsed_data = self.json_parser.parse(content, **kwargs)
            else:
                raise ParsingError(f"Unsupported parser type: {parser_type}")
            
            # Add URL to each data item
            for item in parsed_data:
                item["url"] = url
                item["content_type"] = content_type
                item["status_code"] = response.status_code
            
            # Process data if requested
            if kwargs.get("process_data", True):
                parsed_data = self.data_processor.process(parsed_data)
            
            # Save data if requested
            if kwargs.get("save_data", False):
                output_format = kwargs.get("output_format", "json")
                self._save_data(parsed_data, url, output_format)
            
            self.logger.info(f"Successfully scraped {len(parsed_data)} items from {url}")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {str(e)}")
            raise GetScrapperError(f"Failed to scrape {url}: {str(e)}")

    def scrape_urls(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            **kwargs: Additional scraping parameters (same as scrape_url)
            
        Returns:
            List of all scraped data dictionaries
        """
        all_data = []
        
        for url in urls:
            try:
                data = self.scrape_url(url, **kwargs)
                all_data.extend(data)
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {str(e)}")
                if not kwargs.get("continue_on_error", True):
                    raise
        
        return all_data

    def scrape_from_file(self, file_path: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape URLs from a file.
        
        Args:
            file_path: Path to file containing URLs (one per line)
            **kwargs: Additional scraping parameters
            
        Returns:
            List of all scraped data dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            return self.scrape_urls(urls, **kwargs)
            
        except Exception as e:
            raise GetScrapperError(f"Failed to read URLs from file {file_path}: {str(e)}")

    def _save_data(self, data: List[Dict[str, Any]], url: str, format_type: str) -> None:
        """Save scraped data to file."""
        try:
            # Generate filename from URL
            filename = self._generate_filename(url, format_type)
            output_path = os.path.join(self.output_dir, filename)
            
            if format_type.lower() == "csv":
                self.csv_storage.save(data, output_path)
            elif format_type.lower() == "json":
                self.json_storage.save(data, output_path)
            else:
                raise GetScrapperError(f"Unsupported output format: {format_type}")
            
            self.logger.info(f"Data saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {str(e)}")
            raise

    def _generate_filename(self, url: str, format_type: str) -> str:
        """Generate filename from URL."""
        import re
        from urllib.parse import urlparse
        
        # Extract domain and path
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.strip('/')
        
        # Clean up path
        path = re.sub(r'[^\w\-_/]', '_', path)
        path = re.sub(r'_+', '_', path)
        
        # Generate filename
        if path:
            filename = f"{domain}_{path}.{format_type}"
        else:
            filename = f"{domain}.{format_type}"
        
        # Limit filename length
        if len(filename) > 200:
            filename = filename[:200] + f".{format_type}"
        
        return filename

    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        return {
            "session_info": self.session_manager.get_session_info(),
            "output_directory": self.output_dir,
            "supported_parsers": ["html", "json"],
            "supported_formats": ["csv", "json"],
        }

    def close(self) -> None:
        """Close scraper and cleanup resources."""
        self.session_manager.close()
        self.logger.info("Scraper closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()