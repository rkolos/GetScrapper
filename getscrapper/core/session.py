"""Session management for web scraping."""

import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.exceptions import NetworkError
from ..utils.logger import setup_logger


class SessionManager:
    """Manages HTTP sessions for web scraping."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize session manager.
        
        Args:
            config: Session configuration with keys:
                - timeout: Request timeout in seconds (default: 30)
                - retries: Number of retries (default: 3)
                - backoff_factor: Backoff factor for retries (default: 0.3)
                - user_agent: User agent string
                - headers: Additional headers
                - cookies: Cookies to use
                - proxies: Proxy configuration
                - verify_ssl: Whether to verify SSL certificates (default: True)
                - delay: Delay between requests in seconds (default: 1)
        """
        self.config = config or {}
        self.logger = setup_logger("getscrapper.session")
        
        # Session configuration
        self.timeout = self.config.get("timeout", 30)
        self.retries = self.config.get("retries", 3)
        self.backoff_factor = self.config.get("backoff_factor", 0.3)
        self.user_agent = self.config.get("user_agent", "GetScrapper/1.0.0")
        self.headers = self.config.get("headers", {})
        self.cookies = self.config.get("cookies", {})
        self.proxies = self.config.get("proxies", {})
        self.verify_ssl = self.config.get("verify_ssl", True)
        self.delay = self.config.get("delay", 1)
        
        # Initialize session
        self.session = self._create_session()
        self._last_request_time = 0

    def _create_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()
        
        # Set default headers
        default_headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        default_headers.update(self.headers)
        session.headers.update(default_headers)
        
        # Set cookies
        if self.cookies:
            session.cookies.update(self.cookies)
        
        # Set proxies
        if self.proxies:
            session.proxies.update(self.proxies)
        
        # Configure retries
        retry_strategy = Retry(
            total=self.retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Make GET request with rate limiting and error handling.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.get
            
        Returns:
            Response object
            
        Raises:
            NetworkError: If request fails
        """
        return self._make_request("GET", url, **kwargs)

    def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """
        Make POST request with rate limiting and error handling.
        
        Args:
            url: URL to request
            data: POST data
            **kwargs: Additional arguments for requests.post
            
        Returns:
            Response object
            
        Raises:
            NetworkError: If request fails
        """
        return self._make_request("POST", url, data=data, **kwargs)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with rate limiting and error handling."""
        # Rate limiting
        self._apply_rate_limit()
        
        # Set default timeout
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        # Set SSL verification
        if "verify" not in kwargs:
            kwargs["verify"] = self.verify_ssl
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            if method.upper() == "GET":
                response = self.session.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, **kwargs)
            else:
                raise NetworkError(f"Unsupported HTTP method: {method}")
            
            # Check for HTTP errors
            response.raise_for_status()
            
            self.logger.debug(f"Request successful: {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            self.logger.error(error_msg)
            raise NetworkError(error_msg, status_code)

    def _apply_rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        if self.delay > 0:
            current_time = time.time()
            time_since_last_request = current_time - self._last_request_time
            
            if time_since_last_request < self.delay:
                sleep_time = self.delay - time_since_last_request
                self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self._last_request_time = time.time()

    def close(self) -> None:
        """Close the session."""
        self.session.close()
        self.logger.debug("Session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    def is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain."""
        return self.get_domain(url1) == self.get_domain(url2)

    def resolve_url(self, base_url: str, relative_url: str) -> str:
        """Resolve relative URL against base URL."""
        return urljoin(base_url, relative_url)

    def get_session_info(self) -> Dict[str, Any]:
        """Get session information."""
        return {
            "timeout": self.timeout,
            "retries": self.retries,
            "user_agent": self.user_agent,
            "headers": dict(self.session.headers),
            "cookies": dict(self.session.cookies),
            "proxies": self.proxies,
            "verify_ssl": self.verify_ssl,
            "delay": self.delay,
        }