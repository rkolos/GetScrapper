"""Tests for HTML parser."""

import pytest

from getscrapper.parsers.html_parser import HTMLParser
from getscrapper.utils.exceptions import ParsingError


class TestHTMLParser:
    """Test HTMLParser class."""

    def test_init_default_config(self):
        """Test parser initialization with default config."""
        parser = HTMLParser()
        assert parser.parser == "lxml"
        assert parser.encoding == "utf-8"
        assert parser.extract_text is True
        assert parser.clean_text is True

    def test_init_custom_config(self):
        """Test parser initialization with custom config."""
        config = {
            "parser": "html.parser",
            "encoding": "latin-1",
            "extract_text": False,
            "clean_text": False
        }
        parser = HTMLParser(config)
        assert parser.parser == "html.parser"
        assert parser.encoding == "latin-1"
        assert parser.extract_text is False
        assert parser.clean_text is False

    def test_invalid_parser_config(self):
        """Test parser with invalid configuration."""
        config = {"parser": "invalid_parser"}
        with pytest.raises(ParsingError, match="Invalid parser"):
            HTMLParser(config)

    def test_parse_basic_html(self, sample_html):
        """Test parsing basic HTML content."""
        parser = HTMLParser()
        results = parser.parse(sample_html)
        
        assert len(results) == 1
        result = results[0]
        assert result["type"] == "page_info"
        assert result["title"] == "Test Page"
        assert result["description"] == "A test page for scraping"

    def test_parse_with_selectors(self, sample_html):
        """Test parsing with CSS selectors."""
        parser = HTMLParser()
        selectors = {
            "title": "h1",
            "content": ".content p",
            "prices": ".product .price"
        }
        
        results = parser.parse(sample_html, selectors=selectors)
        
        # Should have results for each selector
        assert len(results) >= 3
        
        # Check for title
        title_results = [r for r in results if r["field"] == "title"]
        assert len(title_results) == 1
        assert title_results[0]["content"] == "Welcome to Test Page"
        
        # Check for prices
        price_results = [r for r in results if r["field"] == "prices"]
        assert len(price_results) == 2
        assert "$19.99" in [r["content"] for r in price_results]
        assert "$29.99" in [r["content"] for r in price_results]

    def test_extract_links(self, sample_html):
        """Test link extraction."""
        parser = HTMLParser()
        results = parser.parse(sample_html, extract_links=True)
        
        # Find link results
        link_results = [r for r in results if r["type"] == "link"]
        assert len(link_results) == 1
        
        link = link_results[0]
        assert link["text"] == "Example Link"
        assert link["url"] == "https://example.com"

    def test_extract_images(self, sample_html):
        """Test image extraction."""
        parser = HTMLParser()
        results = parser.parse(sample_html, extract_images=True)
        
        # Find image results
        image_results = [r for r in results if r["type"] == "image"]
        assert len(image_results) == 1
        
        image = image_results[0]
        assert image["src"] == "test.jpg"
        assert image["alt"] == "Test Image"
        assert image["width"] == "100"
        assert image["height"] == "100"

    def test_extract_meta(self, sample_html):
        """Test meta tag extraction."""
        parser = HTMLParser()
        results = parser.parse(sample_html, extract_meta=True)
        
        # Find meta results
        meta_results = [r for r in results if r["type"] == "meta"]
        assert len(meta_results) >= 2
        
        # Check for description meta
        description_meta = [r for r in meta_results if r["name"] == "description"]
        assert len(description_meta) == 1
        assert description_meta[0]["content"] == "A test page for scraping"

    def test_clean_text_disabled(self, sample_html):
        """Test parsing with text cleaning disabled."""
        config = {"clean_text": False}
        parser = HTMLParser(config)
        results = parser.parse(sample_html, extract_links=True)
        
        # Find link results
        link_results = [r for r in results if r["type"] == "link"]
        assert len(link_results) == 1
        
        # Text should not be cleaned (may have extra whitespace)
        link_text = link_results[0]["text"]
        assert "Example Link" in link_text

    def test_extract_text_disabled(self, sample_html):
        """Test parsing with text extraction disabled."""
        config = {"extract_text": False}
        parser = HTMLParser(config)
        results = parser.parse(sample_html)
        
        assert len(results) == 1
        result = results[0]
        assert result["text_content"] == ""

    def test_parse_invalid_html(self):
        """Test parsing invalid HTML."""
        parser = HTMLParser()
        invalid_html = "<html><body><p>Unclosed paragraph"
        
        # Should not raise exception, but may produce unexpected results
        results = parser.parse(invalid_html)
        assert isinstance(results, list)

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        parser = HTMLParser()
        formats = parser.get_supported_formats()
        
        expected_formats = ["text/html", "application/xhtml+xml", "html"]
        assert all(fmt in formats for fmt in expected_formats)

    def test_is_supported(self):
        """Test format support checking."""
        parser = HTMLParser()
        
        assert parser.is_supported("text/html") is True
        assert parser.is_supported("application/xhtml+xml") is True
        assert parser.is_supported("text/plain") is False
        assert parser.is_supported("application/json") is False

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = HTMLParser()
        results = parser.parse("")
        
        assert len(results) == 1
        result = results[0]
        assert result["type"] == "page_info"
        assert result["title"] == ""
        assert result["description"] == ""

    def test_parse_none_content(self):
        """Test parsing None content."""
        parser = HTMLParser()
        
        with pytest.raises(ParsingError):
            parser.parse(None)