"""Tests for storage modules."""

import json
import os
import pytest
import pandas as pd

from getscrapper.storage.csv_storage import CSVStorage
from getscrapper.storage.json_storage import JSONStorage
from getscrapper.utils.exceptions import StorageError


class TestCSVStorage:
    """Test CSVStorage class."""

    def test_init_default_config(self):
        """Test storage initialization with default config."""
        storage = CSVStorage()
        assert storage.encoding == "utf-8"
        assert storage.delimiter == ","
        assert storage.quotechar == '"'
        assert storage.index is False
        assert storage.na_rep == ""

    def test_init_custom_config(self):
        """Test storage initialization with custom config."""
        config = {
            "encoding": "latin-1",
            "delimiter": ";",
            "quotechar": "'",
            "index": True,
            "na_rep": "N/A"
        }
        storage = CSVStorage(config)
        assert storage.encoding == "latin-1"
        assert storage.delimiter == ";"
        assert storage.quotechar == "'"
        assert storage.index is True
        assert storage.na_rep == "N/A"

    def test_invalid_config(self):
        """Test storage with invalid configuration."""
        config = {"encoding": "invalid_encoding"}
        with pytest.raises(StorageError, match="Invalid encoding"):
            CSVStorage(config)

    def test_save_data(self, sample_data, temp_dir):
        """Test saving data to CSV."""
        storage = CSVStorage()
        output_path = os.path.join(temp_dir, "test.csv")
        
        storage.save(sample_data, output_path)
        
        assert os.path.exists(output_path)
        
        # Verify content
        df = pd.read_csv(output_path)
        assert len(df) == 2
        assert "url" in df.columns
        assert "title" in df.columns

    def test_save_empty_data(self, temp_dir):
        """Test saving empty data."""
        storage = CSVStorage()
        output_path = os.path.join(temp_dir, "empty.csv")
        
        with pytest.raises(StorageError, match="No data to save"):
            storage.save([], output_path)

    def test_load_data(self, sample_data, temp_dir):
        """Test loading data from CSV."""
        storage = CSVStorage()
        output_path = os.path.join(temp_dir, "test.csv")
        
        # Save data first
        storage.save(sample_data, output_path)
        
        # Load data
        loaded_data = storage.load(output_path)
        
        assert len(loaded_data) == 2
        assert loaded_data[0]["url"] == "https://example.com"
        assert loaded_data[1]["url"] == "https://example.com/page2"

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading from nonexistent file."""
        storage = CSVStorage()
        nonexistent_path = os.path.join(temp_dir, "nonexistent.csv")
        
        with pytest.raises(StorageError, match="File not found"):
            storage.load(nonexistent_path)

    def test_save_with_custom_delimiter(self, sample_data, temp_dir):
        """Test saving with custom delimiter."""
        config = {"delimiter": ";"}
        storage = CSVStorage(config)
        output_path = os.path.join(temp_dir, "test_semicolon.csv")
        
        storage.save(sample_data, output_path)
        
        # Verify content has semicolon delimiter
        with open(output_path, 'r') as f:
            content = f.read()
            assert ";" in content
            assert "," not in content or content.count(",") < content.count(";")

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        storage = CSVStorage()
        formats = storage.get_supported_formats()
        
        assert ".csv" in formats
        assert ".tsv" in formats

    def test_is_supported(self):
        """Test format support checking."""
        storage = CSVStorage()
        
        assert storage.is_supported(".csv") is True
        assert storage.is_supported(".tsv") is True
        assert storage.is_supported(".json") is False
        assert storage.is_supported(".xml") is False


class TestJSONStorage:
    """Test JSONStorage class."""

    def test_init_default_config(self):
        """Test storage initialization with default config."""
        storage = JSONStorage()
        assert storage.encoding == "utf-8"
        assert storage.indent == 2
        assert storage.ensure_ascii is False
        assert storage.sort_keys is False
        assert storage.separators == (",", ": ")

    def test_init_custom_config(self):
        """Test storage initialization with custom config."""
        config = {
            "encoding": "latin-1",
            "indent": 4,
            "ensure_ascii": True,
            "sort_keys": True,
            "separators": (",", ":")
        }
        storage = JSONStorage(config)
        assert storage.encoding == "latin-1"
        assert storage.indent == 4
        assert storage.ensure_ascii is True
        assert storage.sort_keys is True
        assert storage.separators == (",", ":")

    def test_invalid_config(self):
        """Test storage with invalid configuration."""
        config = {"indent": "not_a_number"}
        with pytest.raises(StorageError, match="'indent' must be an integer"):
            JSONStorage(config)

    def test_save_data(self, sample_data, temp_dir):
        """Test saving data to JSON."""
        storage = JSONStorage()
        output_path = os.path.join(temp_dir, "test.json")
        
        storage.save(sample_data, output_path)
        
        assert os.path.exists(output_path)
        
        # Verify content
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert len(loaded_data) == 2
        assert loaded_data[0]["url"] == "https://example.com"
        assert loaded_data[1]["url"] == "https://example.com/page2"

    def test_save_empty_data(self, temp_dir):
        """Test saving empty data."""
        storage = JSONStorage()
        output_path = os.path.join(temp_dir, "empty.json")
        
        with pytest.raises(StorageError, match="No data to save"):
            storage.save([], output_path)

    def test_load_data(self, sample_data, temp_dir):
        """Test loading data from JSON."""
        storage = JSONStorage()
        output_path = os.path.join(temp_dir, "test.json")
        
        # Save data first
        storage.save(sample_data, output_path)
        
        # Load data
        loaded_data = storage.load(output_path)
        
        assert len(loaded_data) == 2
        assert loaded_data[0]["url"] == "https://example.com"
        assert loaded_data[1]["url"] == "https://example.com/page2"

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading from nonexistent file."""
        storage = JSONStorage()
        nonexistent_path = os.path.join(temp_dir, "nonexistent.json")
        
        with pytest.raises(StorageError, match="File not found"):
            storage.load(nonexistent_path)

    def test_load_invalid_json(self, temp_dir):
        """Test loading invalid JSON file."""
        storage = JSONStorage()
        output_path = os.path.join(temp_dir, "invalid.json")
        
        # Create invalid JSON file
        with open(output_path, 'w') as f:
            f.write('{"invalid": json}')
        
        with pytest.raises(StorageError, match="Invalid JSON format"):
            storage.load(output_path)

    def test_load_single_object(self, temp_dir):
        """Test loading JSON file with single object."""
        storage = JSONStorage()
        output_path = os.path.join(temp_dir, "single.json")
        
        # Save single object
        single_data = {"url": "https://example.com", "title": "Test"}
        with open(output_path, 'w') as f:
            json.dump(single_data, f)
        
        # Load data
        loaded_data = storage.load(output_path)
        
        assert len(loaded_data) == 1
        assert loaded_data[0]["url"] == "https://example.com"

    def test_load_invalid_content_type(self, temp_dir):
        """Test loading JSON file with invalid content type."""
        storage = JSONStorage()
        output_path = os.path.join(temp_dir, "invalid.json")
        
        # Create file with non-dict/list content
        with open(output_path, 'w') as f:
            json.dump("just a string", f)
        
        with pytest.raises(StorageError, match="JSON file must contain a list or object"):
            storage.load(output_path)

    def test_save_with_custom_indent(self, sample_data, temp_dir):
        """Test saving with custom indentation."""
        config = {"indent": 4}
        storage = JSONStorage(config)
        output_path = os.path.join(temp_dir, "test_indent.json")
        
        storage.save(sample_data, output_path)
        
        # Verify indentation
        with open(output_path, 'r') as f:
            content = f.read()
            # Should have 4-space indentation
            assert "    " in content

    def test_save_with_sort_keys(self, sample_data, temp_dir):
        """Test saving with sorted keys."""
        config = {"sort_keys": True}
        storage = JSONStorage(config)
        output_path = os.path.join(temp_dir, "test_sorted.json")
        
        storage.save(sample_data, output_path)
        
        # Verify keys are sorted
        with open(output_path, 'r') as f:
            content = f.read()
            # Keys should be in alphabetical order
            assert content.find('"content"') < content.find('"metadata"')
            assert content.find('"metadata"') < content.find('"title"')
            assert content.find('"title"') < content.find('"url"')

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        storage = JSONStorage()
        formats = storage.get_supported_formats()
        
        assert ".json" in formats
        assert ".jsonl" in formats

    def test_is_supported(self):
        """Test format support checking."""
        storage = JSONStorage()
        
        assert storage.is_supported(".json") is True
        assert storage.is_supported(".jsonl") is True
        assert storage.is_supported(".csv") is False
        assert storage.is_supported(".xml") is False