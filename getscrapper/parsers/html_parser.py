"""HTML parser implementation using BeautifulSoup."""

import re
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup, Tag
from lxml import html

from .base_parser import BaseParser
from ..utils.exceptions import ParsingError


class HTMLParser(BaseParser):
    """HTML parser using BeautifulSoup and lxml."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize HTML parser.
        
        Args:
            config: Parser configuration with keys:
                - parser: BeautifulSoup parser ('html.parser', 'lxml', 'html5lib')
                - encoding: Text encoding (default: 'utf-8')
                - extract_text: Whether to extract text content (default: True)
                - clean_text: Whether to clean extracted text (default: True)
        """
        self.config = config or {}
        self.parser = self.config.get("parser", "lxml")
        self.encoding = self.config.get("encoding", "utf-8")
        self.extract_text = self.config.get("extract_text", True)
        self.clean_text = self.config.get("clean_text", True)
        super().__init__(config)

    def parse(self, content: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Parse HTML content and extract data.
        
        Args:
            content: HTML content to parse
            **kwargs: Additional parameters:
                - selectors: Dict of CSS selectors for data extraction
                - extract_links: Whether to extract links (default: False)
                - extract_images: Whether to extract images (default: False)
                - extract_meta: Whether to extract meta tags (default: False)
                
        Returns:
            List of extracted data dictionaries
            
        Raises:
            ParsingError: If parsing fails
        """
        try:
            soup = BeautifulSoup(content, self.parser)
            results = []
            
            # Extract data based on selectors
            selectors = kwargs.get("selectors", {})
            if selectors:
                results.extend(self._extract_by_selectors(soup, selectors))
            
            # Extract links if requested
            if kwargs.get("extract_links", False):
                results.extend(self._extract_links(soup))
            
            # Extract images if requested
            if kwargs.get("extract_images", False):
                results.extend(self._extract_images(soup))
            
            # Extract meta tags if requested
            if kwargs.get("extract_meta", False):
                results.extend(self._extract_meta(soup))
            
            # If no specific extraction requested, extract basic page info
            if not any([selectors, kwargs.get("extract_links"), 
                       kwargs.get("extract_images"), kwargs.get("extract_meta")]):
                results.append(self._extract_basic_info(soup))
            
            return results
            
        except Exception as e:
            raise ParsingError(f"Failed to parse HTML: {str(e)}", "HTML")

    def _extract_by_selectors(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract data using CSS selectors."""
        results = []
        
        for field_name, selector in selectors.items():
            elements = soup.select(selector)
            for element in elements:
                data = {
                    "field": field_name,
                    "selector": selector,
                    "content": self._extract_element_content(element),
                    "attributes": dict(element.attrs) if hasattr(element, 'attrs') else {},
                }
                results.append(data)
        
        return results

    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all links from the page."""
        results = []
        links = soup.find_all("a", href=True)
        
        for link in links:
            data = {
                "type": "link",
                "text": self._clean_text_content(link.get_text()) if self.clean_text else link.get_text(),
                "url": link.get("href"),
                "title": link.get("title", ""),
                "attributes": dict(link.attrs),
            }
            results.append(data)
        
        return results

    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all images from the page."""
        results = []
        images = soup.find_all("img")
        
        for img in images:
            data = {
                "type": "image",
                "src": img.get("src", ""),
                "alt": img.get("alt", ""),
                "title": img.get("title", ""),
                "width": img.get("width", ""),
                "height": img.get("height", ""),
                "attributes": dict(img.attrs),
            }
            results.append(data)
        
        return results

    def _extract_meta(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract meta tags from the page."""
        results = []
        meta_tags = soup.find_all("meta")
        
        for meta in meta_tags:
            data = {
                "type": "meta",
                "name": meta.get("name", ""),
                "property": meta.get("property", ""),
                "content": meta.get("content", ""),
                "http_equiv": meta.get("http-equiv", ""),
                "attributes": dict(meta.attrs),
            }
            results.append(data)
        
        return results

    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract basic page information."""
        title = soup.find("title")
        description = soup.find("meta", attrs={"name": "description"})
        
        return {
            "type": "page_info",
            "title": self._clean_text_content(title.get_text()) if title else "",
            "description": description.get("content", "") if description else "",
            "url": "",  # Will be set by the scraper
            "text_content": self._extract_page_text(soup) if self.extract_text else "",
        }

    def _extract_page_text(self, soup: BeautifulSoup) -> str:
        """Extract all text content from the page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        return self._clean_text_content(text) if self.clean_text else text

    def _extract_element_content(self, element: Union[Tag, str]) -> str:
        """Extract content from an element."""
        if isinstance(element, str):
            return self._clean_text_content(element) if self.clean_text else element
        
        if hasattr(element, 'get_text'):
            content = element.get_text()
            return self._clean_text_content(content) if self.clean_text else content
        
        return str(element)

    def _clean_text_content(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

    def _validate_config(self) -> None:
        """Validate parser configuration."""
        valid_parsers = ["html.parser", "lxml", "html5lib"]
        if self.parser not in valid_parsers:
            raise ParsingError(f"Invalid parser: {self.parser}. Must be one of {valid_parsers}")

    def get_supported_formats(self) -> List[str]:
        """Get supported content formats."""
        return ["text/html", "application/xhtml+xml", "html"]