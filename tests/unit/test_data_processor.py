"""Tests for data processor."""

import pytest
from datetime import datetime

from getscrapper.processors.data_processor import DataProcessor


class TestDataProcessor:
    """Test DataProcessor class."""

    def test_init_default_config(self):
        """Test processor initialization with default config."""
        processor = DataProcessor()
        assert processor.auto_clean is True
        assert processor.validate_data is True
        assert processor.transform_dates is True
        assert processor.extract_numbers is False

    def test_init_custom_config(self):
        """Test processor initialization with custom config."""
        config = {
            "auto_clean": False,
            "validate_data": False,
            "transform_dates": False,
            "extract_numbers": True
        }
        processor = DataProcessor(config)
        assert processor.auto_clean is False
        assert processor.validate_data is False
        assert processor.transform_dates is False
        assert processor.extract_numbers is True

    def test_process_basic_data(self, sample_data):
        """Test processing basic data."""
        processor = DataProcessor()
        results = processor.process(sample_data)
        
        assert len(results) == 2
        
        for result in results:
            assert "_processed_at" in result
            assert "_processor_version" in result
            assert "_validation" in result

    def test_process_with_auto_clean(self):
        """Test processing with auto cleaning."""
        data = [
            {
                "url": "https://example.com",
                "content": "  dirty   content  \n\t",
                "title": "  Test Title  "
            }
        ]
        
        processor = DataProcessor({"auto_clean": True})
        results = processor.process(data)
        
        assert results[0]["content"] == "dirty content"
        assert results[0]["title"] == "Test Title"

    def test_process_without_auto_clean(self):
        """Test processing without auto cleaning."""
        data = [
            {
                "url": "https://example.com",
                "content": "  dirty   content  \n\t"
            }
        ]
        
        processor = DataProcessor({"auto_clean": False})
        results = processor.process(data)
        
        assert results[0]["content"] == "  dirty   content  \n\t"

    def test_process_with_date_transformation(self):
        """Test processing with date transformation."""
        data = [
            {
                "url": "https://example.com",
                "created_date": "2023-01-01",
                "updated_date": "01/15/2023"
            }
        ]
        
        processor = DataProcessor({"transform_dates": True})
        results = processor.process(data)
        
        # Check that dates were transformed
        assert "created_date_original" in results[0]
        assert "updated_date_original" in results[0]

    def test_process_without_date_transformation(self):
        """Test processing without date transformation."""
        data = [
            {
                "url": "https://example.com",
                "created_date": "2023-01-01"
            }
        ]
        
        processor = DataProcessor({"transform_dates": False})
        results = processor.process(data)
        
        # Check that dates were not transformed
        assert "created_date_original" not in results[0]
        assert results[0]["created_date"] == "2023-01-01"

    def test_process_with_number_extraction(self):
        """Test processing with number extraction."""
        data = [
            {
                "url": "https://example.com",
                "price_text": "Price: $19.99",
                "count_text": "Items: 42"
            }
        ]
        
        processor = DataProcessor({"extract_numbers": True})
        results = processor.process(data)
        
        assert "price_text_numbers" in results[0]
        assert results[0]["price_text_numbers"] == [19.99]
        assert "count_text_numbers" in results[0]
        assert results[0]["count_text_numbers"] == [42]

    def test_process_without_validation(self):
        """Test processing without validation."""
        data = [
            {
                "url": "invalid-url",
                "content": "test content"
            }
        ]
        
        processor = DataProcessor({"validate_data": False})
        results = processor.process(data)
        
        assert "_validation" not in results[0]

    def test_process_with_validation_errors(self):
        """Test processing with validation errors."""
        data = [
            {
                "url": "invalid-url",
                "content": "test content"
            }
        ]
        
        processor = DataProcessor({"validate_data": True})
        results = processor.process(data)
        
        validation = results[0]["_validation"]
        assert validation["is_valid"] is False
        assert len(validation["errors"]) > 0

    def test_process_handles_errors(self):
        """Test that processing handles errors gracefully."""
        data = [
            {
                "url": "https://example.com",
                "content": "test content"
            },
            {
                "url": "https://example.com",
                "content": None  # This might cause an error
            }
        ]
        
        processor = DataProcessor()
        results = processor.process(data)
        
        assert len(results) == 2
        # Both items should be processed successfully (None content is handled)
        assert "_processed_at" in results[0]
        assert "_processed_at" in results[1]

    def test_filter_data(self, sample_data):
        """Test data filtering."""
        processor = DataProcessor()
        
        # Filter by URL
        filters = {"url": "https://example.com"}
        filtered = processor.filter_data(sample_data, filters)
        assert len(filtered) == 1
        assert filtered[0]["url"] == "https://example.com"
        
        # Filter by title
        filters = {"title": "Test Page 2"}
        filtered = processor.filter_data(sample_data, filters)
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Test Page 2"

    def test_filter_data_complex_criteria(self):
        """Test data filtering with complex criteria."""
        data = [
            {"name": "Product 1", "price": 19.99, "category": "electronics"},
            {"name": "Product 2", "price": 29.99, "category": "electronics"},
            {"name": "Product 3", "price": 9.99, "category": "books"}
        ]
        
        processor = DataProcessor()
        
        # Filter by price range
        filters = {
            "price": {"min": 20, "max": 30},
            "category": "electronics"
        }
        filtered = processor.filter_data(data, filters)
        assert len(filtered) == 1
        assert filtered[0]["name"] == "Product 2"

    def test_filter_data_contains(self):
        """Test data filtering with contains criteria."""
        data = [
            {"name": "Apple iPhone", "description": "Latest smartphone"},
            {"name": "Samsung Galaxy", "description": "Android phone"},
            {"name": "Google Pixel", "description": "Google smartphone"}
        ]
        
        processor = DataProcessor()
        
        filters = {"description": {"contains": "smartphone"}}
        filtered = processor.filter_data(data, filters)
        assert len(filtered) == 2

    def test_group_data(self, sample_data):
        """Test data grouping."""
        processor = DataProcessor()
        
        # Group by title
        grouped = processor.group_data(sample_data, "title")
        assert len(grouped) == 2
        assert "Test Page" in grouped
        assert "Test Page 2" in grouped
        assert len(grouped["Test Page"]) == 1
        assert len(grouped["Test Page 2"]) == 1

    def test_aggregate_data(self):
        """Test data aggregation."""
        data = [
            {"name": "Product 1", "price": 19.99, "category": "electronics"},
            {"name": "Product 2", "price": 29.99, "category": "electronics"},
            {"name": "Product 3", "price": 9.99, "category": "books"},
            {"name": "Product 4", "price": 19.99, "category": "books"}
        ]
        
        processor = DataProcessor()
        
        aggregations = {
            "price": "avg",
            "name": "count",
            "category": "unique"
        }
        
        result = processor.aggregate_data(data, aggregations)
        
        assert result["price"] == pytest.approx(19.99, rel=1e-2)  # Average price
        assert result["name"] == 4  # Count of products
        assert set(result["category"]) == {"electronics", "books"}  # Unique categories

    def test_aggregate_data_with_none_values(self):
        """Test data aggregation with None values."""
        data = [
            {"price": 19.99},
            {"price": None},
            {"price": 29.99}
        ]
        
        processor = DataProcessor()
        
        aggregations = {"price": "sum"}
        result = processor.aggregate_data(data, aggregations)
        
        assert result["price"] == 49.98  # Sum of non-None values

    def test_aggregate_data_empty(self):
        """Test data aggregation with empty data."""
        processor = DataProcessor()
        
        aggregations = {"price": "sum"}
        result = processor.aggregate_data([], aggregations)
        
        assert result["price"] is None