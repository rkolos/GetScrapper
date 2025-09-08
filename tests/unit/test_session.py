"""Tests for session manager."""

import pytest
import requests
from unittest.mock import Mock, patch

from getscrapper.core.session import SessionManager
from getscrapper.utils.exceptions import NetworkError


class TestSessionManager:
    """Test SessionManager class."""

    def test_init_default_config(self):
        """Test session initialization with default config."""
        session = SessionManager()
        assert session.timeout == 30
        assert session.retries == 3
        assert session.backoff_factor == 0.3
        assert session.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        assert session.delay == 1
        assert session.verify_ssl is True

    def test_init_custom_config(self):
        """Test session initialization with custom config."""
        config = {
            "timeout": 60,
            "retries": 5,
            "backoff_factor": 0.5,
            "user_agent": "Custom Agent",
            "delay": 2.0,
            "verify_ssl": False,
            "headers": {"Custom-Header": "value"},
            "cookies": {"session": "abc123"},
            "proxies": {"http": "http://proxy:8080"}
        }
        session = SessionManager(config)
        assert session.timeout == 60
        assert session.retries == 5
        assert session.backoff_factor == 0.5
        assert session.user_agent == "Custom Agent"
        assert session.delay == 2.0
        assert session.verify_ssl is False

    @patch('getscrapper.core.session.requests.Session')
    def test_get_success(self, mock_session_class):
        """Test successful GET request."""
        # Mock session and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        session = SessionManager({"delay": 0})  # No delay for testing
        response = session.get("https://example.com")
        
        assert response.status_code == 200
        assert response.text == "Success"
        mock_session.get.assert_called_once()

    @patch('getscrapper.core.session.requests.Session')
    def test_post_success(self, mock_session_class):
        """Test successful POST request."""
        # Mock session and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = "Created"
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        session = SessionManager({"delay": 0})  # No delay for testing
        response = session.post("https://example.com", data={"key": "value"})
        
        assert response.status_code == 201
        assert response.text == "Created"
        mock_session.post.assert_called_once()

    @patch('getscrapper.core.session.requests.Session')
    def test_request_with_network_error(self, mock_session_class):
        """Test request with network error."""
        # Mock session to raise exception
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        mock_session_class.return_value = mock_session
        
        session = SessionManager({"delay": 0})
        
        with pytest.raises(NetworkError, match="Request failed"):
            session.get("https://example.com")

    @patch('getscrapper.core.session.requests.Session')
    def test_request_with_http_error(self, mock_session_class):
        """Test request with HTTP error."""
        # Mock session and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        session = SessionManager({"delay": 0})
        
        with pytest.raises(NetworkError, match="Request failed"):
            session.get("https://example.com")

    @patch('getscrapper.core.session.requests.Session')
    def test_request_with_timeout(self, mock_session_class):
        """Test request with timeout."""
        # Mock session to raise timeout
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.Timeout("Request timeout")
        mock_session_class.return_value = mock_session
        
        session = SessionManager({"delay": 0})
        
        with pytest.raises(NetworkError, match="Request failed"):
            session.get("https://example.com")

    def test_get_domain(self):
        """Test domain extraction from URL."""
        session = SessionManager()
        
        assert session.get_domain("https://example.com/path") == "example.com"
        assert session.get_domain("http://www.test.org/page") == "www.test.org"
        assert session.get_domain("https://subdomain.example.com") == "subdomain.example.com"

    def test_is_same_domain(self):
        """Test same domain checking."""
        session = SessionManager()
        
        assert session.is_same_domain("https://example.com/page1", "https://example.com/page2") is True
        assert session.is_same_domain("https://example.com", "https://test.com") is False
        assert session.is_same_domain("http://example.com", "https://example.com") is True

    def test_resolve_url(self):
        """Test URL resolution."""
        session = SessionManager()
        
        base_url = "https://example.com/path/"
        
        assert session.resolve_url(base_url, "page.html") == "https://example.com/path/page.html"
        assert session.resolve_url(base_url, "/absolute/path") == "https://example.com/absolute/path"
        assert session.resolve_url(base_url, "https://other.com/page") == "https://other.com/page"

    def test_get_session_info(self):
        """Test getting session information."""
        config = {
            "timeout": 60,
            "retries": 5,
            "user_agent": "Test Agent",
            "headers": {"Test": "value"},
            "cookies": {"session": "abc123"},
            "proxies": {"http": "http://proxy:8080"},
            "verify_ssl": False,
            "delay": 2.0
        }
        session = SessionManager(config)
        
        info = session.get_session_info()
        
        assert info["timeout"] == 60
        assert info["retries"] == 5
        assert info["user_agent"] == "Test Agent"
        assert info["verify_ssl"] is False
        assert info["delay"] == 2.0

    def test_context_manager(self):
        """Test session as context manager."""
        with SessionManager() as session:
            assert session.session is not None
        
        # Session should be closed after context exit
        # (We can't easily test this without mocking, but the structure is correct)

    def test_close(self):
        """Test session closing."""
        session = SessionManager()
        session.close()
        # Session should be closed (structure is correct)

    @patch('getscrapper.core.session.time.sleep')
    @patch('getscrapper.core.session.time.time')
    def test_rate_limiting(self, mock_time, mock_sleep):
        """Test rate limiting functionality."""
        # Mock time to simulate rate limiting
        # Each call to _apply_rate_limit makes 2 calls to time.time()
        # First call: current_time = 0, _last_request_time = 0, sleep for 1.0, then _last_request_time = 0
        # Second call: current_time = 0.5, _last_request_time = 0, sleep for 0.5, then _last_request_time = 0.5
        # Third call: current_time = 2.0, _last_request_time = 0.5, no sleep needed, then _last_request_time = 2.0
        mock_time.side_effect = [0, 0, 0.5, 0.5, 2.0, 2.0]
        
        session = SessionManager({"delay": 1.0})
        
        # First request should sleep for 1.0 seconds (initial delay)
        session._apply_rate_limit()
        mock_sleep.assert_called_once_with(1.0)
        
        # Reset mock
        mock_sleep.reset_mock()
        
        # Second request should sleep for 0.5 seconds
        session._apply_rate_limit()
        mock_sleep.assert_called_once_with(0.5)
        
        # Reset mock
        mock_sleep.reset_mock()
        
        # Third request should not sleep (enough time has passed)
        session._apply_rate_limit()
        mock_sleep.assert_not_called()

    def test_unsupported_method(self):
        """Test unsupported HTTP method."""
        session = SessionManager({"delay": 0})
        
        with pytest.raises(NetworkError, match="Unsupported HTTP method"):
            session._make_request("PUT", "https://example.com")