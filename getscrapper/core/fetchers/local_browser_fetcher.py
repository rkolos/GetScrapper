"""Local browser fetcher using Playwright."""

import asyncio
import time
from typing import Dict, Any, Optional

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Создаем заглушки для типов
    Browser = None
    Page = None

from .base_fetcher import FetcherStrategy


class LocalBrowserFetcher(FetcherStrategy):
    """Fetcher strategy for JavaScript-rendered content using local Playwright browser."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize local browser fetcher.
        
        Args:
            config: Configuration with keys:
                - headless: Run browser in headless mode (default: True)
                - timeout: Page load timeout in milliseconds (default: 30000)
                - user_agent: User agent string
                - headers: Additional headers
                - block_resources: List of resource types to block (default: ['image', 'font', 'media'])
                - wait_for: What to wait for ('networkidle', 'load', 'domcontentloaded')
        """
        super().__init__(config)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self._initialized = False
    
    async def _ensure_initialized(self) -> None:
        """Ensure browser is initialized."""
        if not self._initialized:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.get("headless", True),
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            self._initialized = True
    
    async def fetch_html(self, url: str) -> Dict[str, Any]:
        """
        Fetch HTML content using local browser.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with fetch results
        """
        start_time = time.time()
        
        try:
            await self._ensure_initialized()
            self.logger.info(f"Fetching HTML with local browser from: {url}")
            
            # Create new page
            page = await self.browser.new_page()
            
            # Set headers
            headers = self.config.get("headers", {})
            user_agent = self.config.get("user_agent", 
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            await page.set_extra_http_headers({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                **headers
            })
            
            # Block resources if configured
            block_resources = self.config.get("block_resources", ['image', 'font', 'media'])
            if block_resources:
                await page.route("**/*", self._create_route_handler(block_resources))
            
            # Navigate to page
            timeout = self.config.get("timeout", 30000)
            wait_for = self.config.get("wait_for", "networkidle")
            
            response = await page.goto(
                url, 
                wait_until=wait_for,
                timeout=timeout
            )
            
            # Wait for additional JS rendering
            await asyncio.sleep(2)
            
            # Get page data
            final_url = page.url
            page_title = await page.title()
            html_content = await page.content()
            status_code = response.status if response else 0
            
            # Close page
            await page.close()
            
            render_time = time.time() - start_time
            
            result = {
                'html_content': html_content,
                'page_title': page_title,
                'final_url': final_url,
                'status_code': status_code,
                'content_length': len(html_content),
                'render_time': render_time,
                'error': None,
                'source': self.get_strategy_name()
            }
            
            self.logger.info(f"Local browser fetch completed: {url} -> {final_url} ({status_code}) in {render_time:.2f}s")
            return result
            
        except Exception as e:
            render_time = time.time() - start_time
            error_msg = f"Local browser fetch failed: {str(e)}"
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
    
    def _create_route_handler(self, block_resources: list):
        """Create route handler for blocking resources."""
        async def route_handler(route):
            resource_type = route.request.resource_type
            if resource_type in block_resources:
                await route.abort()
            else:
                await route.continue_()
        return route_handler
    
    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "local_browser"
    
    def is_available(self) -> bool:
        """Check if Playwright is available."""
        return PLAYWRIGHT_AVAILABLE
    
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self._initialized = False
        self.logger.debug("Local browser fetcher closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()