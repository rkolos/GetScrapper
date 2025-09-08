"""
Универсальный сервис рендеринга с интеллектуальной эскалацией
Архитектура: Local Browser (baseline) -> Browserbase (fallback)
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
import time
from urllib.parse import urlparse

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LocalRenderer:
    """Класс для рендеринга страниц через локальный Playwright браузер"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Асинхронный контекстный менеджер для инициализации браузера"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
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
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие браузера при выходе из контекста"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def fetch_js_local(self, url: str) -> Dict[str, Any]:
        """
        Основная функция рендеринга через локальный браузер
        
        Args:
            url: URL для рендеринга
            
        Returns:
            Словарь с результатами сессии:
            - html_content: Итоговый HTML-код страницы
            - page_title: Финальный <title> страницы  
            - final_url: URL после всех редиректов и JS-навигации
            - status_code: Конечный HTTP-статус
            - content_length: Длина html_content
            - render_time: Время рендеринга в секундах
            - error: Информация об ошибке (если есть)
        """
        start_time = time.time()
        
        try:
            # Создаем новую страницу
            page = await self.browser.new_page()
            
            # Настраиваем User-Agent и другие заголовки
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Отключаем загрузку изображений и шрифтов для ускорения
            await page.route("**/*", self._route_handler)
            
            # Переходим на страницу с обработкой редиректов
            response = await page.goto(
                url, 
                wait_until='networkidle',
                timeout=self.timeout
            )
            
            # Ждем дополнительное время для JS-рендеринга
            await asyncio.sleep(2)
            
            # Получаем финальные данные
            final_url = page.url
            page_title = await page.title()
            html_content = await page.content()
            status_code = response.status if response else 0
            
            render_time = time.time() - start_time
            
            # Закрываем страницу
            await page.close()
            
            result = {
                'html_content': html_content,
                'page_title': page_title,
                'final_url': final_url,
                'status_code': status_code,
                'content_length': len(html_content),
                'render_time': render_time,
                'error': None
            }
            
            logger.info(f"Local render completed: {url} -> {final_url} ({status_code}) in {render_time:.2f}s")
            return result
            
        except Exception as e:
            render_time = time.time() - start_time
            error_msg = f"Local render failed: {str(e)}"
            logger.error(f"{error_msg} for URL: {url}")
            
            return {
                'html_content': '',
                'page_title': '',
                'final_url': url,
                'status_code': 0,
                'content_length': 0,
                'render_time': render_time,
                'error': error_msg
            }
    
    async def _route_handler(self, route):
        """Обработчик маршрутов для блокировки ненужных ресурсов"""
        resource_type = route.request.resource_type
        if resource_type in ['image', 'font', 'media']:
            await route.abort()
        else:
            await route.continue_()


async def fetch_js_local(url: str, headless: bool = True, timeout: int = 30000) -> Dict[str, Any]:
    """
    Удобная функция для рендеринга URL через локальный браузер
    
    Args:
        url: URL для рендеринга
        headless: Запускать браузер в headless режиме
        timeout: Таймаут в миллисекундах
        
    Returns:
        Словарь с результатами рендеринга
    """
    async with LocalRenderer(headless=headless, timeout=timeout) as renderer:
        return await renderer.fetch_js_local(url)


# Пример использования
if __name__ == "__main__":
    async def test_local_render():
        test_urls = [
            "https://httpbin.org/html",
            "https://example.com",
            "https://quotes.toscrape.com/js/"
        ]
        
        for url in test_urls:
            print(f"\n=== Testing: {url} ===")
            result = await fetch_js_local(url)
            print(f"Title: {result['page_title']}")
            print(f"Final URL: {result['final_url']}")
            print(f"Status: {result['status_code']}")
            print(f"Content Length: {result['content_length']}")
            print(f"Render Time: {result['render_time']:.2f}s")
            if result['error']:
                print(f"Error: {result['error']}")
    
    # Запуск теста
    asyncio.run(test_local_render())