"""Browserbase fetcher for cloud-based browser rendering."""

import asyncio
import time
from typing import Dict, Any, Optional
import os

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

from .base_fetcher import FetcherStrategy


class BrowserbaseFetcher(FetcherStrategy):
    """Fetcher strategy for cloud-based browser rendering using Browserbase API."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Browserbase fetcher.
        
        Args:
            config: Configuration with keys:
                - api_key: Browserbase API key (can be from env var BROWSERBASE_API_KEY)
                - project_id: Browserbase project ID (can be from env var BROWSERBASE_PROJECT_ID)
                - base_url: Browserbase API base URL (default: https://www.browserbase.com/v1)
                - timeout: Request timeout in milliseconds (default: 30000)
                - headless: Run browser in headless mode (default: True)
        """
        super().__init__(config)
        self.api_key = self.config.get("api_key") or os.getenv('BROWSERBASE_API_KEY')
        self.project_id = self.config.get("project_id") or os.getenv('BROWSERBASE_PROJECT_ID')
        self.base_url = self.config.get("base_url", "https://www.browserbase.com/v1")
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
    
    async def _ensure_initialized(self) -> None:
        """Ensure session is initialized."""
        if not self._initialized:
            if not self.api_key or not self.project_id:
                raise ValueError("Browserbase API key and project ID are required")
            
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            )
            self._initialized = True
    
    async def _create_session(self) -> str:
        """Create a new browser session."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        payload = {
            "projectId": self.project_id,
            "headless": self.config.get("headless", True),
            "timeout": self.config.get("timeout", 30000)
        }
        
        async with self.session.post(
            f"{self.base_url}/sessions",
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to create session: {response.status} - {error_text}")
            
            data = await response.json()
            return data['id']
    
    async def _navigate_to_url(self, session_id: str, url: str) -> Dict[str, Any]:
        """Navigate to URL in session."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        payload = {
            "url": url,
            "waitUntil": "networkidle"
        }
        
        async with self.session.post(
            f"{self.base_url}/sessions/{session_id}/navigate",
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to navigate: {response.status} - {error_text}")
            
            return await response.json()
    
    async def _get_page_content(self, session_id: str) -> Dict[str, Any]:
        """Get page content."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        async with self.session.get(
            f"{self.base_url}/sessions/{session_id}/content"
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to get content: {response.status} - {error_text}")
            
            return await response.json()
    
    async def _get_page_info(self, session_id: str) -> Dict[str, Any]:
        """Get page info (title, URL)."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        async with self.session.get(
            f"{self.base_url}/sessions/{session_id}/info"
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to get page info: {response.status} - {error_text}")
            
            return await response.json()
    
    async def _close_session(self, session_id: str):
        """Close browser session."""
        if not self.session:
            return
        
        async with self.session.delete(
            f"{self.base_url}/sessions/{session_id}"
        ) as response:
            if response.status not in [200, 404]:
                error_text = await response.text()
                self.logger.warning(f"Failed to close session: {response.status} - {error_text}")
    
    async def fetch_html(self, url: str) -> Dict[str, Any]:
        """
        Fetch HTML content using Browserbase.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with fetch results
        """
        start_time = time.time()
        session_id = None
        
        try:
            await self._ensure_initialized()
            self.logger.info(f"Fetching HTML with Browserbase from: {url}")
            
            # Create session
            session_id = await self._create_session()
            self.logger.debug(f"Created Browserbase session: {session_id}")
            
            # Navigate to URL
            await self._navigate_to_url(session_id, url)
            
            # Wait for JS rendering
            await asyncio.sleep(3)
            
            # Get content and info
            content_result = await self._get_page_content(session_id)
            info_result = await self._get_page_info(session_id)
            
            render_time = time.time() - start_time
            
            result = {
                'html_content': content_result.get('html', ''),
                'page_title': info_result.get('title', ''),
                'final_url': info_result.get('url', url),
                'status_code': 200,  # Browserbase always returns 200 on success
                'content_length': len(content_result.get('html', '')),
                'render_time': render_time,
                'error': None,
                'source': self.get_strategy_name()
            }
            
            self.logger.info(f"Browserbase fetch completed: {url} in {render_time:.2f}s")
            return result
            
        except Exception as e:
            render_time = time.time() - start_time
            error_msg = f"Browserbase fetch failed: {str(e)}"
            self.logger.error(f"{error_msg} for URL: {url}")
            
            return {
                'html_content': '',
                'page_title': '',
                'final_url': url,
                'status_code': 0,
                'content_length': 0,
                'render_time': render_time,
                'error': error_msg,
                'source': self.get_strategy_name()
            }
        
        finally:
            # Close session
            if session_id:
                await self._close_session(session_id)
    
    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "browserbase"
    
    def is_available(self) -> bool:
        """Check if Browserbase is available."""
        return AIOHTTP_AVAILABLE and bool(self.api_key and self.project_id)
    
    async def close(self) -> None:
        """Close session and cleanup resources."""
        if self.session:
            await self.session.close()
        self._initialized = False
        self.logger.debug("Browserbase fetcher closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()