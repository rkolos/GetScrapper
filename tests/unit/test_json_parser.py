"""Tests for JSON parser."""

import json
import pytest

from getscrapper.parsers.json_parser import JSONParser
from getscrapper.utils.exceptions import ParsingError


class TestJSONParser:
    """Test JSONParser class."""

    def test_init_default_config(self):
        """Test parser initialization with default config."""
        parser = JSONParser()
        assert parser.encoding == "utf-8"
        assert parser.strict is True
        assert parser.object_hook is None

    def test_init_custom_config(self):
        """Test parser initialization with custom config."""
        def custom_hook(obj):
            return obj
        
        config = {
            "encoding": "latin-1",
            "strict": False,
            "object_hook": custom_hook
        }
        parser = JSONParser(config)
        assert parser.encoding == "latin-1"
        assert parser.strict is False
        assert parser.object_hook == custom_hook

    def test_invalid_config(self):
        """Test parser with invalid configuration."""
        config = {"strict": "not_a_boolean"}
        with pytest.raises(ParsingError, match="'strict' must be a boolean"):
            JSONParser(config)

    def test_parse_basic_json(self, sample_json):
        """Test parsing basic JSON content."""
        parser = JSONParser()
        results = parser.parse(sample_json)
        
        assert len(results) == 1
        result = results[0]
        assert "users" in result
        assert "products" in result
        assert "metadata" in result

    def test_parse_with_path(self, sample_json):
        """Test parsing with JSONPath."""
        parser = JSONParser()
        results = parser.parse(sample_json, path="users")
        
        assert len(results) == 1
        result = results[0]
        assert result["_type"] == "array"
        assert result["_length"] == 2

    def test_parse_with_path_array_element(self, sample_json):
        """Test parsing with path to array element."""
        parser = JSONParser()
        results = parser.parse(sample_json, path="users[0]")
        
        assert len(results) == 1
        result = results[0]
        assert result["id"] == 1
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"

    def test_parse_with_path_nested(self, sample_json):
        """Test parsing with nested path."""
        parser = JSONParser()
        results = parser.parse(sample_json, path="metadata.total_users")
        
        assert len(results) == 1
        result = results[0]
        assert result["value"] == 2
        assert result["_type"] == "int"

    def test_parse_extract_arrays(self, sample_json):
        """Test parsing with array extraction."""
        parser = JSONParser()
        results = parser.parse(sample_json, path="users", extract_arrays=True)
        
        assert len(results) == 2
        
        # Check first user
        user1 = results[0]
        assert user1["id"] == 1
        assert user1["name"] == "John Doe"
        assert user1["_array_index"] == 0
        
        # Check second user
        user2 = results[1]
        assert user2["id"] == 2
        assert user2["name"] == "Jane Smith"
        assert user2["_array_index"] == 1

    def test_parse_flatten(self, sample_json):
        """Test parsing with flattening."""
        parser = JSONParser()
        results = parser.parse(sample_json, path="metadata", flatten=True)
        
        assert len(results) == 1
        result = results[0]
        assert result["total_users"] == 2
        assert result["total_products"] == 2
        assert result["last_updated"] == "2023-01-01T00:00:00Z"

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        parser = JSONParser()
        invalid_json = '{"invalid": json}'
        
        with pytest.raises(ParsingError, match="Invalid JSON format"):
            parser.parse(invalid_json)

    def test_parse_invalid_path(self, sample_json):
        """Test parsing with invalid path."""
        parser = JSONParser()
        
        with pytest.raises(ParsingError, match="Failed to parse JSON"):
            parser.parse(sample_json, path="nonexistent.field")

    def test_parse_invalid_array_index(self, sample_json):
        """Test parsing with invalid array index."""
        parser = JSONParser()
        
        with pytest.raises(ParsingError, match="Invalid array index"):
            parser.parse(sample_json, path="users[10]")

    def test_parse_array_wildcard(self, sample_json):
        """Test parsing with array wildcard."""
        parser = JSONParser()
        results = parser.parse(sample_json, path="users[*]")
        
        assert len(results) == 1
        result = results[0]
        assert result["_type"] == "array"
        assert len(result["data"]) == 2

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        parser = JSONParser()
        formats = parser.get_supported_formats()
        
        expected_formats = ["application/json", "text/json", "json"]
        assert all(fmt in formats for fmt in expected_formats)

    def test_is_supported(self):
        """Test format support checking."""
        parser = JSONParser()
        
        assert parser.is_supported("application/json") is True
        assert parser.is_supported("text/json") is True
        assert parser.is_supported("text/html") is False
        assert parser.is_supported("application/xml") is False

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = JSONParser()
        
        with pytest.raises(ParsingError, match="Invalid JSON format"):
            parser.parse("")

    def test_parse_none_content(self):
        """Test parsing None content."""
        parser = JSONParser()
        
        with pytest.raises(ParsingError):
            parser.parse(None)

    def test_parse_primitive_values(self):
        """Test parsing primitive JSON values."""
        parser = JSONParser()
        
        # Test string
        results = parser.parse('"hello world"')
        assert len(results) == 1
        assert results[0]["value"] == "hello world"
        assert results[0]["_type"] == "str"
        
        # Test number
        results = parser.parse('42')
        assert len(results) == 1
        assert results[0]["value"] == 42
        assert results[0]["_type"] == "int"
        
        # Test boolean
        results = parser.parse('true')
        assert len(results) == 1
        assert results[0]["value"] is True
        assert results[0]["_type"] == "bool"
        
        # Test null
        results = parser.parse('null')
        assert len(results) == 1
        assert results[0]["value"] is None
        assert results[0]["_type"] == "NoneType"

    def test_parse_array_of_primitives(self):
        """Test parsing array of primitive values."""
        parser = JSONParser()
        results = parser.parse('[1, 2, 3, "four", true]')
        
        assert len(results) == 1
        result = results[0]
        assert result["_type"] == "array"
        assert result["_length"] == 5
        assert result["data"] == [1, 2, 3, "four", True]

    def test_parse_array_of_primitives_extract(self):
        """Test parsing array of primitives with extraction."""
        parser = JSONParser()
        results = parser.parse('[1, 2, 3]', extract_arrays=True)
        
        assert len(results) == 3
        assert results[0]["value"] == 1
        assert results[0]["_array_index"] == 0
        assert results[1]["value"] == 2
        assert results[1]["_array_index"] == 1
        assert results[2]["value"] == 3
        assert results[2]["_array_index"] == 2