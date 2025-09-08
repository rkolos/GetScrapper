"""Main scraper class for GetScrapper."""

import os
import asyncio
from typing import Any, Dict, List, Optional, Union, Set
from urllib.parse import urljoin, urlparse

from .detection_controller import DetectionController, EscalationLevel
from ..parsers.html_parser import HTMLParser
from ..parsers.json_parser import JSONParser
from ..processors.data_processor import DataProcessor
try:
    from ..storage.csv_storage import CSVStorage
except ImportError:
    from ..storage.simple_csv_storage import SimpleCSVStorage as CSVStorage
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
                - detection_controller: Detection controller configuration
                - parser: Parser configuration
                - processor: Data processor configuration
                - storage: Storage configuration
                - output_dir: Output directory for saved files
                - default_escalation_level: Default escalation level to start with
        """
        self.config = config or {}
        self.logger = setup_logger("getscrapper.scraper")
        
        # Initialize detection controller with fetcher strategies
        detection_config = self.config.get("detection_controller", {})
        self.detection_controller = DetectionController(detection_config)
        
        # Initialize parsers
        self.html_parser = HTMLParser(self.config.get("parser", {}))
        self.json_parser = JSONParser(self.config.get("parser", {}))
        self.data_processor = DataProcessor(self.config.get("processor", {}))
        
        # Initialize storage
        self.csv_storage = CSVStorage(self.config.get("storage", {}))
        self.json_storage = JSONStorage(self.config.get("storage", {}))
        
        # Output directory
        self.output_dir = self.config.get("output_dir", "./output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Default escalation level
        self.default_escalation_level = self.config.get("default_escalation_level", EscalationLevel.STATIC)
        
        # Recursive scraping state
        self.visited_urls: Set[str] = set()

    async def scrape_url(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape a single URL using intelligent escalation.
        
        Args:
            url: URL to scrape
            **kwargs: Additional scraping parameters:
                - escalation_level: Starting escalation level (default: from config)
                - max_escalations: Maximum number of escalations (default: 2)
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
            
            # Get escalation parameters
            escalation_level = kwargs.get("escalation_level", self.default_escalation_level)
            max_escalations = kwargs.get("max_escalations", 2)
            
            # Fetch content using intelligent escalation
            fetch_result = await self.detection_controller.fetch_html_with_escalation(
                url, 
                start_level=escalation_level,
                max_escalations=max_escalations
            )
            
            # Check if fetch was successful
            if fetch_result.get('error') and not fetch_result.get('html_content'):
                raise GetScrapperError(f"Failed to fetch content: {fetch_result['error']}")
            
            # Get HTML content
            html_content = fetch_result.get('html_content', '')
            content_type = 'text/html'  # Default for browser-rendered content
            
            # Determine parser type
            parser_type = kwargs.get("parser_type", "html")
            
            # Parse content
            if parser_type == "html":
                # Pass base URL for resolving relative links
                parse_kwargs = kwargs.copy()
                parse_kwargs["base_url"] = fetch_result.get('final_url', url)
                parsed_data = self.html_parser.parse(html_content, **parse_kwargs)
            elif parser_type == "json":
                parsed_data = self.json_parser.parse(html_content, **kwargs)
            else:
                raise ParsingError(f"Unsupported parser type: {parser_type}")
            
            # Add metadata to each data item
            for item in parsed_data:
                item["url"] = url
                item["final_url"] = fetch_result.get('final_url', url)
                item["content_type"] = content_type
                item["status_code"] = fetch_result.get('status_code', 0)
                item["render_time"] = fetch_result.get('render_time', 0)
                item["strategy_used"] = fetch_result.get('strategy_used', 'unknown')
                item["escalation_level"] = fetch_result.get('escalation_level', 0)
                item["escalation_successful"] = fetch_result.get('escalation_successful', False)
                
                # Add detection analysis if available
                if fetch_result.get('detection_analysis'):
                    item["detection_analysis"] = fetch_result['detection_analysis']
            
            # Process data if requested
            if kwargs.get("process_data", True):
                parsed_data = self.data_processor.process(parsed_data)
            
            # Save data if requested
            if kwargs.get("save_data", False):
                output_format = kwargs.get("output_format", "json")
                self._save_data(parsed_data, url, output_format)
            
            self.logger.info(f"Successfully scraped {len(parsed_data)} items from {url} using {fetch_result.get('strategy_used', 'unknown')} strategy")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {str(e)}")
            raise GetScrapperError(f"Failed to scrape {url}: {str(e)}")

    async def scrape_urls(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
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
                data = await self.scrape_url(url, **kwargs)
                all_data.extend(data)
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {str(e)}")
                if not kwargs.get("continue_on_error", True):
                    raise
        
        return all_data

    async def scrape_recursive(self, start_url: str, max_depth: int = 2, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape URLs recursively following links.
        
        Args:
            start_url: Starting URL to scrape
            max_depth: Maximum depth to follow links (default: 2)
            **kwargs: Additional scraping parameters:
                - same_domain_only: Only follow links from the same domain (default: True)
                - extract_links: Whether to extract links (default: True)
                - continue_on_error: Whether to continue on errors (default: True)
                
        Returns:
            List of all scraped data dictionaries
        """
        self.visited_urls.clear()  # Reset visited URLs for new recursive scraping
        return await self._scrape_recursive_internal(start_url, max_depth, 0, **kwargs)

    async def _scrape_recursive_internal(self, url: str, max_depth: int, current_depth: int, **kwargs) -> List[Dict[str, Any]]:
        """Internal recursive scraping method."""
        all_data = []
        
        # Check if we've already visited this URL or exceeded max depth
        if url in self.visited_urls or current_depth > max_depth:
            return all_data
        
        # Mark URL as visited
        self.visited_urls.add(url)
        
        try:
            self.logger.info(f"[Depth {current_depth}] Scraping: {url}")
            
            # Scrape current URL with link extraction enabled
            scrape_kwargs = kwargs.copy()
            scrape_kwargs["extract_links"] = True
            data = await self.scrape_url(url, **scrape_kwargs)
            all_data.extend(data)
            
            # If we haven't reached max depth, follow links
            if current_depth < max_depth:
                links = self._extract_links_from_data(data)
                same_domain_only = kwargs.get("same_domain_only", True)
                base_domain = self._get_domain(url) if same_domain_only else None
                
                for link_url in links:
                    # Skip if we've already visited this URL
                    if link_url in self.visited_urls:
                        continue
                    
                    # Skip if it's from a different domain (when same_domain_only is True)
                    if same_domain_only and base_domain and self._get_domain(link_url) != base_domain:
                        continue
                    
                    # Recursively scrape the link
                    recursive_data = await self._scrape_recursive_internal(
                        link_url, max_depth, current_depth + 1, **kwargs
                    )
                    all_data.extend(recursive_data)
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url} at depth {current_depth}: {str(e)}")
            if not kwargs.get("continue_on_error", True):
                raise
        
        return all_data

    def _extract_links_from_data(self, data: List[Dict[str, Any]]) -> List[str]:
        """Extract links from scraped data."""
        links = []
        for item in data:
            if item.get("type") == "link" and item.get("full_url"):
                links.append(item["full_url"])
        return links

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    async def scrape_from_file(self, file_path: str, **kwargs) -> List[Dict[str, Any]]:
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
            
            return await self.scrape_urls(urls, **kwargs)
            
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
            "detection_controller_info": self.detection_controller.get_strategy_info(),
            "available_strategies": self.detection_controller.get_available_strategies(),
            "output_directory": self.output_dir,
            "supported_parsers": ["html", "json"],
            "supported_formats": ["csv", "json"],
            "visited_urls_count": len(self.visited_urls),
            "recursive_scraping_enabled": True,
            "default_escalation_level": self.default_escalation_level.value,
        }

    def close(self) -> None:
        """Close scraper and cleanup resources."""
        self.detection_controller.close()
        self.logger.info("Scraper closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()