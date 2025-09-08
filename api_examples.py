"""
Примеры использования Universal HTML Renderer API
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any


class RendererAPIClient:
    """Клиент для работы с Universal HTML Renderer API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка состояния API"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def scrape_url(self, 
                        url: str, 
                        browserbase_api_key: str = None,
                        browserbase_project_id: str = None,
                        local_timeout: int = None,
                        local_headless: bool = None,
                        reuse_context: bool = None) -> Dict[str, Any]:
        """
        Рендеринг одного URL
        
        Args:
            url: URL для рендеринга
            browserbase_api_key: API ключ Browserbase
            browserbase_project_id: ID проекта Browserbase
            local_timeout: Таймаут для локального браузера
            local_headless: Запускать в headless режиме
            reuse_context: Переиспользовать контекст браузера
        """
        payload = {"url": url}
        
        if browserbase_api_key:
            payload["browserbase_api_key"] = browserbase_api_key
        if browserbase_project_id:
            payload["browserbase_project_id"] = browserbase_project_id
        if local_timeout:
            payload["local_timeout"] = local_timeout
        if local_headless is not None:
            payload["local_headless"] = local_headless
        if reuse_context is not None:
            payload["reuse_context"] = reuse_context
        
        async with self.session.post(
            f"{self.base_url}/scrape",
            json=payload
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"API Error {response.status}: {error_text}")
    
    async def scrape_batch(self, 
                          urls: list[str],
                          browserbase_api_key: str = None,
                          browserbase_project_id: str = None) -> Dict[str, Any]:
        """
        Пакетный рендеринг URL
        
        Args:
            urls: Список URL для рендеринга
            browserbase_api_key: API ключ Browserbase
            browserbase_project_id: ID проекта Browserbase
        """
        payload = {"urls": urls}
        
        if browserbase_api_key:
            payload["browserbase_api_key"] = browserbase_api_key
        if browserbase_project_id:
            payload["browserbase_project_id"] = browserbase_project_id
        
        async with self.session.post(
            f"{self.base_url}/scrape/batch",
            json=payload
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"API Error {response.status}: {error_text}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики рендерера"""
        async with self.session.get(f"{self.base_url}/stats") as response:
            return await response.json()


async def example_single_scrape():
    """Пример рендеринга одного URL"""
    print("=== Single URL Scraping Example ===")
    
    async with RendererAPIClient() as client:
        # Проверяем состояние API
        health = await client.health_check()
        print(f"API Status: {health['status']}")
        print(f"Browserbase Available: {health['browserbase_available']}")
        
        # Рендерим URL
        url = "https://httpbin.org/html"
        print(f"\nScraping: {url}")
        
        result = await client.scrape_url(url)
        
        print(f"Success: {result['success']}")
        print(f"Source: {result['source']}")
        print(f"Title: {result['page_title']}")
        print(f"Final URL: {result['final_url']}")
        print(f"Status Code: {result['status_code']}")
        print(f"Content Length: {result['content_length']} bytes")
        print(f"Render Time: {result['render_time']:.2f}s")
        
        if result.get('escalation_reason'):
            print(f"Escalation Reason: {result['escalation_reason']}")
        
        if result.get('detection_analysis'):
            analysis = result['detection_analysis']
            print(f"Detection Confidence: {analysis.get('confidence_score', 0):.2f}")
            if analysis.get('blocking_reasons'):
                print(f"Blocking Reasons: {', '.join(analysis['blocking_reasons'])}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        # Показываем первые 200 символов HTML
        html_preview = result['html_content'][:200]
        print(f"\nHTML Preview:\n{html_preview}...")


async def example_batch_scrape():
    """Пример пакетного рендеринга"""
    print("\n=== Batch Scraping Example ===")
    
    urls = [
        "https://httpbin.org/html",
        "https://example.com",
        "https://quotes.toscrape.com/js/"
    ]
    
    async with RendererAPIClient() as client:
        print(f"Batch scraping {len(urls)} URLs...")
        
        result = await client.scrape_batch(urls)
        
        print(f"Success: {result['success']}")
        print(f"Total URLs: {result['total_urls']}")
        print(f"Successful: {result['successful']}")
        print(f"Failed: {result['failed']}")
        
        print("\nResults:")
        for i, url_result in enumerate(result['results'], 1):
            print(f"\n{i}. {url_result['url']}")
            print(f"   Source: {url_result['source']}")
            print(f"   Title: {url_result['page_title']}")
            print(f"   Content Length: {url_result['content_length']} bytes")
            print(f"   Render Time: {url_result['render_time']:.2f}s")
            
            if url_result.get('escalation_reason'):
                print(f"   Escalation: {url_result['escalation_reason']}")
            
            if url_result.get('error'):
                print(f"   Error: {url_result['error']}")


async def example_with_browserbase():
    """Пример с использованием Browserbase"""
    print("\n=== Browserbase Example ===")
    
    # Замените на ваши реальные credentials
    browserbase_api_key = "your_browserbase_api_key"
    browserbase_project_id = "your_browserbase_project_id"
    
    async with RendererAPIClient() as client:
        url = "https://httpbin.org/html"
        print(f"Scraping with Browserbase: {url}")
        
        try:
            result = await client.scrape_url(
                url,
                browserbase_api_key=browserbase_api_key,
                browserbase_project_id=browserbase_project_id
            )
            
            print(f"Source: {result['source']}")
            print(f"Title: {result['page_title']}")
            print(f"Render Time: {result['render_time']:.2f}s")
            
        except Exception as e:
            print(f"Error: {e}")


async def example_stats():
    """Пример получения статистики"""
    print("\n=== Stats Example ===")
    
    async with RendererAPIClient() as client:
        stats = await client.get_stats()
        
        print("Renderer Stats:")
        print(f"Browserbase Available: {stats['browserbase_available']}")
        print(f"Local Timeout: {stats['local_timeout']}ms")
        print(f"Local Headless: {stats['local_headless']}")
        
        rules = stats['detection_rules_count']
        print(f"Detection Rules:")
        print(f"  Title Keywords: {rules['title_keywords']}")
        print(f"  URL Patterns: {rules['url_patterns']}")
        print(f"  HTML Selectors: {rules['html_selectors']}")
        print(f"  Content Phrases: {rules['content_phrases']}")


async def main():
    """Главная функция с примерами"""
    print("Universal HTML Renderer API Examples")
    print("=" * 50)
    
    try:
        # Примеры использования
        await example_single_scrape()
        await example_batch_scrape()
        await example_stats()
        
        # Раскомментируйте для тестирования с Browserbase
        # await example_with_browserbase()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the API server is running:")
        print("docker-compose up api-server")


if __name__ == "__main__":
    asyncio.run(main())