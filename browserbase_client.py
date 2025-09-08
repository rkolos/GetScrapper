"""
Клиент для Browserbase API (Уровень 3 - Fallback)
Используется когда локальный браузер заблокирован
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import aiohttp
import json
import time

logger = logging.getLogger(__name__)


class BrowserbaseClient:
    """Клиент для работы с Browserbase API"""
    
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = "https://www.browserbase.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
    
    async def create_session(self) -> str:
        """Создает новую сессию браузера"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        payload = {
            "projectId": self.project_id,
            "headless": True,
            "timeout": 30000
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
    
    async def navigate_to_url(self, session_id: str, url: str) -> Dict[str, Any]:
        """Переходит на указанный URL в сессии"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
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
    
    async def get_page_content(self, session_id: str) -> Dict[str, Any]:
        """Получает содержимое страницы"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        async with self.session.get(
            f"{self.base_url}/sessions/{session_id}/content"
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to get content: {response.status} - {error_text}")
            
            return await response.json()
    
    async def get_page_info(self, session_id: str) -> Dict[str, Any]:
        """Получает информацию о странице (title, URL)"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        async with self.session.get(
            f"{self.base_url}/sessions/{session_id}/info"
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to get page info: {response.status} - {error_text}")
            
            return await response.json()
    
    async def close_session(self, session_id: str):
        """Закрывает сессию браузера"""
        if not self.session:
            return
        
        async with self.session.delete(
            f"{self.base_url}/sessions/{session_id}"
        ) as response:
            if response.status not in [200, 404]:
                error_text = await response.text()
                logger.warning(f"Failed to close session: {response.status} - {error_text}")
    
    async def fetch_via_browserbase(self, url: str) -> Dict[str, Any]:
        """
        Основная функция для получения HTML через Browserbase
        
        Args:
            url: URL для рендеринга
            
        Returns:
            Словарь с результатами рендеринга
        """
        start_time = time.time()
        session_id = None
        
        try:
            # Создаем сессию
            session_id = await self.create_session()
            logger.info(f"Created Browserbase session: {session_id}")
            
            # Переходим на URL
            await self.navigate_to_url(session_id, url)
            
            # Ждем дополнительное время для JS-рендеринга
            await asyncio.sleep(3)
            
            # Получаем содержимое и информацию о странице
            content_result = await self.get_page_content(session_id)
            info_result = await self.get_page_info(session_id)
            
            render_time = time.time() - start_time
            
            result = {
                'html_content': content_result.get('html', ''),
                'page_title': info_result.get('title', ''),
                'final_url': info_result.get('url', url),
                'status_code': 200,  # Browserbase всегда возвращает 200 при успехе
                'content_length': len(content_result.get('html', '')),
                'render_time': render_time,
                'error': None,
                'source': 'browserbase'
            }
            
            logger.info(f"Browserbase render completed: {url} in {render_time:.2f}s")
            return result
            
        except Exception as e:
            render_time = time.time() - start_time
            error_msg = f"Browserbase render failed: {str(e)}"
            logger.error(f"{error_msg} for URL: {url}")
            
            return {
                'html_content': '',
                'page_title': '',
                'final_url': url,
                'status_code': 0,
                'content_length': 0,
                'render_time': render_time,
                'error': error_msg,
                'source': 'browserbase'
            }
        
        finally:
            # Закрываем сессию
            if session_id:
                await self.close_session(session_id)


async def fetch_via_browserbase(url: str, api_key: str, project_id: str) -> Dict[str, Any]:
    """
    Удобная функция для рендеринга URL через Browserbase
    
    Args:
        url: URL для рендеринга
        api_key: API ключ Browserbase
        project_id: ID проекта Browserbase
        
    Returns:
        Словарь с результатами рендеринга
    """
    async with BrowserbaseClient(api_key, project_id) as client:
        return await client.fetch_via_browserbase(url)


# Пример использования
if __name__ == "__main__":
    async def test_browserbase():
        # Замените на ваши реальные данные
        API_KEY = "your_browserbase_api_key"
        PROJECT_ID = "your_project_id"
        
        test_url = "https://example.com"
        
        logger.info(f"Testing Browserbase with URL: {test_url}")
        result = await fetch_via_browserbase(test_url, API_KEY, PROJECT_ID)
        
        logger.info(f"Title: {result['page_title']}")
        logger.info(f"Final URL: {result['final_url']}")
        logger.info(f"Content Length: {result['content_length']}")
        logger.info(f"Render Time: {result['render_time']:.2f}s")
        if result['error']:
            logger.info(f"Error: {result['error']}")
    
    # Раскомментируйте для тестирования
    # asyncio.run(test_browserbase())