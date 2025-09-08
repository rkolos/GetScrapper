"""Static HTML fetcher using requests library."""

import time
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base_fetcher import FetcherStrategy
from ...utils.exceptions import NetworkError


class StaticFetcher(FetcherStrategy):
    """Fetcher strategy for static HTML content using requests."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize static fetcher.
        
        Args:
            config: Configuration with keys:
                - timeout: Request timeout in seconds (default: 30)
                - retries: Number of retries (default: 3)
                - backoff_factor: Backoff factor for retries (default: 0.3)
                - user_agent: User agent string
                - headers: Additional headers
                - cookies: Cookies to use
                - proxies: Proxy configuration
                - verify_ssl: Whether to verify SSL certificates (default: True)
        """
        super().__init__(config)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()
        
        # Configuration
        timeout = self.config.get("timeout", 30)
        retries = self.config.get("retries", 3)
        backoff_factor = self.config.get("backoff_factor", 0.3)
        user_agent = self.config.get("user_agent", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        headers = self.config.get("headers", {})
        cookies = self.config.get("cookies", {})
        proxies = self.config.get("proxies", {})
        verify_ssl = self.config.get("verify_ssl", True)
        
        # Set default headers
        default_headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        default_headers.update(headers)
        session.headers.update(default_headers)
        
        # Set cookies
        if cookies:
            session.cookies.update(cookies)
        
        # Set proxies
        if proxies:
            session.proxies.update(proxies)
        
        # Configure retries
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    async def fetch_html(self, url: str) -> Dict[str, Any]:
        """
        Fetch static HTML content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with fetch results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Fetching static HTML from: {url}")
            
            # Make request
            response = self.session.get(url, timeout=self.config.get("timeout", 30))
            response.raise_for_status()
            
            # Extract content
            html_content = response.text
            page_title = self._extract_title(html_content)
            final_url = response.url
            status_code = response.status_code
            content_length = len(html_content)
            render_time = time.time() - start_time
            
            result = {
                'html_content': html_content,
                'page_title': page_title,
                'final_url': final_url,
                'status_code': status_code,
                'content_length': content_length,
                'render_time': render_time,
                'error': None,
                'source': self.get_strategy_name()
            }
            
            self.logger.info(f"Static fetch completed: {url} -> {final_url} ({status_code}) in {render_time:.2f}s")
            return result
            
        except requests.exceptions.RequestException as e:
            render_time = time.time() - start_time
            error_msg = f"Static fetch failed: {str(e)}"
            self.logger.error(f"{error_msg} for URL: {url}")
            
            return {
                'html_content': '',
                'page_title': '',
                'final_url': url,
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'content_length': 0,
                'render_time': render_time,
                'error': error_msg,
                'source': self.get_strategy_name()
            }
    
    def _extract_title(self, html_content: str) -> str:
        """Extract page title from HTML content."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.get_text().strip() if title_tag else ''
        except Exception:
            return ''
    
    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "static"
    
    def close(self) -> None:
        """Close the session."""
        if hasattr(self, 'session'):
            self.session.close()
            self.logger.debug("Static fetcher session closed")