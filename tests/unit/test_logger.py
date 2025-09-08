"""Tests for logging utilities."""

import logging
import os
import tempfile
from unittest.mock import patch

import pytest

from getscrapper.utils.logger import setup_logger


class TestLogger:
    """Test logging utilities."""

    def test_setup_logger_default(self):
        """Test logger setup with default parameters."""
        logger = setup_logger()
        
        assert logger.name == "getscrapper"
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1

    def test_setup_logger_custom_name(self):
        """Test logger setup with custom name."""
        logger = setup_logger(name="custom_logger")
        
        assert logger.name == "custom_logger"
        assert logger.level == logging.INFO

    def test_setup_logger_custom_level(self):
        """Test logger setup with custom level."""
        logger = setup_logger(level="DEBUG")
        
        assert logger.level == logging.DEBUG

    def test_setup_logger_with_file(self):
        """Test logger setup with log file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            log_file = f.name
        
        try:
            logger = setup_logger(log_file=log_file)
            
            assert logger.name == "getscrapper"
            assert len(logger.handlers) >= 2  # Console + file handler
            
            # Test logging to file
            logger.info("Test message")
            
            # Verify message was written to file
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test message" in content
                
        finally:
            os.unlink(log_file)

    def test_setup_logger_clears_existing_handlers(self):
        """Test that setup_logger clears existing handlers."""
        logger = setup_logger()
        initial_handler_count = len(logger.handlers)
        
        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        logger.addHandler(dummy_handler)
        assert len(logger.handlers) == initial_handler_count + 1
        
        # Setup logger again
        logger = setup_logger()
        assert len(logger.handlers) == 1  # Should have only console handler

    def test_setup_logger_formatter(self):
        """Test logger formatter."""
        logger = setup_logger()
        
        # Check that formatter is set
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                formatter = handler.formatter
                assert formatter is not None
                assert "%(asctime)s" in formatter._fmt
                assert "%(name)s" in formatter._fmt
                assert "%(levelname)s" in formatter._fmt
                assert "%(message)s" in formatter._fmt

    def test_setup_logger_different_levels(self):
        """Test logger setup with different levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            logger = setup_logger(level=level)
            assert logger.level == getattr(logging, level)

    def test_setup_logger_case_insensitive_level(self):
        """Test logger setup with case insensitive level."""
        logger = setup_logger(level="debug")
        assert logger.level == logging.DEBUG
        
        logger = setup_logger(level="ERROR")
        assert logger.level == logging.ERROR

    def test_setup_logger_invalid_level(self):
        """Test logger setup with invalid level."""
        # Should not raise exception, just use default level
        logger = setup_logger(level="INVALID")
        assert logger.level == logging.INFO  # Default level

    def test_setup_logger_multiple_handlers(self):
        """Test logger setup with multiple handlers."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            log_file = f.name
        
        try:
            logger = setup_logger(log_file=log_file)
            
            # Should have console handler and file handler
            assert len(logger.handlers) == 2
            
            # Check handler types
            handler_types = [type(h).__name__ for h in logger.handlers]
            assert "StreamHandler" in handler_types
            assert "FileHandler" in handler_types
            
        finally:
            os.unlink(log_file)

    def test_setup_logger_file_creation(self):
        """Test that log file is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            # File should not exist initially
            assert not os.path.exists(log_file)
            
            logger = setup_logger(log_file=log_file)
            
            # File should be created
            assert os.path.exists(log_file)

    def test_setup_logger_file_permissions(self):
        """Test logger setup with file permission issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory that we can't write to
            restricted_dir = os.path.join(temp_dir, "restricted")
            os.makedirs(restricted_dir, mode=0o444)  # Read-only
            
            log_file = os.path.join(restricted_dir, "test.log")
            
            # Should raise exception for permission denied
            with pytest.raises(PermissionError):
                setup_logger(log_file=log_file)

    def test_setup_logger_console_output(self):
        """Test that logger outputs to console."""
        logger = setup_logger()
        
        # Test that we can log without errors
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

    def test_setup_logger_thread_safety(self):
        """Test logger thread safety."""
        import threading
        import time
        
        logger = setup_logger()
        messages = []
        
        def log_messages():
            for i in range(10):
                logger.info(f"Thread message {i}")
                messages.append(f"Thread message {i}")
                time.sleep(0.01)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=log_messages)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have logged messages from all threads
        assert len(messages) == 30

    def test_setup_logger_singleton_behavior(self):
        """Test that logger setup returns the same logger instance."""
        logger1 = setup_logger(name="test_logger")
        logger2 = setup_logger(name="test_logger")
        
        # Should return the same logger instance
        assert logger1 is logger2

    def test_setup_logger_different_names(self):
        """Test that different logger names return different instances."""
        logger1 = setup_logger(name="logger1")
        logger2 = setup_logger(name="logger2")
        
        # Should return different logger instances
        assert logger1 is not logger2
        assert logger1.name == "logger1"
        assert logger2.name == "logger2"