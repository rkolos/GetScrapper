"""
Главный контроллер универсального сервиса рендеринга
Объединяет локальный рендеринг, детекцию блокировок и эскалацию
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from universal_renderer import fetch_js_local
from detection_engine import DetectionEngine
from browserbase_client import fetch_via_browserbase
from config import config

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UniversalRenderer:
    """Главный класс универсального рендерера с интеллектуальной эскалацией"""
    
    def __init__(self, 
                 browserbase_api_key: Optional[str] = None,
                 browserbase_project_id: Optional[str] = None,
                 local_timeout: Optional[int] = None,
                 local_headless: Optional[bool] = None,
                 reuse_context: Optional[bool] = None):
        """
        Инициализация рендерера
        
        Args:
            browserbase_api_key: API ключ Browserbase (из переменной окружения если не указан)
            browserbase_project_id: ID проекта Browserbase (из переменной окружения если не указан)
            local_timeout: Таймаут для локального браузера в миллисекундах
            local_headless: Запускать локальный браузер в headless режиме
            reuse_context: Переиспользовать контекст браузера
        """
        self.detection_engine = DetectionEngine()
        
        # Используем конфигурацию из переменных окружения с возможностью переопределения
        self.local_timeout = local_timeout or config.PLAYWRIGHT_TIMEOUT
        self.local_headless = local_headless if local_headless is not None else config.PLAYWRIGHT_HEADLESS
        self.reuse_context = reuse_context if reuse_context is not None else config.PLAYWRIGHT_REUSE_CONTEXT
        
        # Настройка Browserbase
        self.browserbase_api_key = browserbase_api_key or config.BROWSERBASE_API_KEY
        self.browserbase_project_id = browserbase_project_id or config.BROWSERBASE_PROJECT_ID
        
        if not self.browserbase_api_key or not self.browserbase_project_id:
            logger.warning("Browserbase credentials not provided. Fallback will not be available.")
            self.browserbase_available = False
        else:
            self.browserbase_available = True
            logger.info("Browserbase fallback is available")
    
    async def get_universal_html(self, url: str) -> Dict[str, Any]:
        """
        Главная функция универсального рендеринга
        
        Архитектура:
        1. Уровень 2 (Baseline): Локальный Playwright браузер
        2. Анализ результата через DetectionEngine
        3. Уровень 3 (Fallback): Browserbase при обнаружении блокировки
        
        Args:
            url: URL для рендеринга
            
        Returns:
            Словарь с результатами рендеринга:
            - html_content: Финальный HTML
            - page_title: Заголовок страницы
            - final_url: Финальный URL
            - status_code: HTTP статус
            - content_length: Длина контента
            - render_time: Время рендеринга
            - source: Источник рендеринга ('local' или 'browserbase')
            - escalation_reason: Причина эскалации (если была)
            - detection_analysis: Результаты анализа детекции
        """
        logger.info(f"[INFO] Starting universal render for URL: {url}")
        
        # Шаг 1: Локальный рендеринг (Уровень 2)
        logger.info(f"[INFO] Attempting local render for: {url}")
        result_l2 = await fetch_js_local(
            url, 
            headless=self.local_headless, 
            timeout=self.local_timeout,
            reuse_context=self.reuse_context
        )
        
        # Шаг 2: Проверка на явный сбой рендеринга
        if result_l2.get('error'):
            logger.error(f"[ERROR] Local render failed for {url}: {result_l2['error']}")
            # Технический сбой - не эскалируем до Browserbase, сразу возвращаем ошибку
            return {
                **result_l2,
                'source': 'local',
                'escalation_reason': 'technical_failure',
                'detection_analysis': None
            }
        
        # Шаг 3: Анализ через DetectionEngine
        logger.info(f"[INFO] Analyzing local render result for blocking detection")
        is_blocked, detection_analysis = self.detection_engine.analyze(result_l2)
        
        # Шаг 4: Принятие решения об эскалации
        if is_blocked:
            logger.warning(f"[WARN] URL: {url} | Local render BLOCKED. Escalating to Browserbase.")
            logger.warning(f"[WARN] Blocking reasons: {', '.join(detection_analysis['blocking_reasons'])}")
            logger.warning(f"[WARN] Confidence score: {detection_analysis['confidence_score']:.2f}")
            
            if not self.browserbase_available:
                logger.error(f"[ERROR] Browserbase not available for escalation")
                return {
                    **result_l2,
                    'source': 'local',
                    'escalation_reason': 'blocked_no_fallback',
                    'detection_analysis': detection_analysis
                }
            
            # Эскалация только при успешной работе L2, которая вернула страницу-блокировщик
            return await self._escalate_to_browserbase(url, "blocking_detected", detection_analysis)
        else:
            logger.info(f"[INFO] URL: {url} | Local render successful.")
            logger.info(f"[INFO] Confidence score: {detection_analysis['confidence_score']:.2f}")
            return {
                **result_l2,
                'source': 'local',
                'escalation_reason': None,
                'detection_analysis': detection_analysis
            }
    
    async def _escalate_to_browserbase(self, url: str, reason: str, detection_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Эскалация запроса на Browserbase (Уровень 3)
        
        Args:
            url: URL для рендеринга
            reason: Причина эскалации
            detection_analysis: Результаты анализа детекции
            
        Returns:
            Результат рендеринга через Browserbase
        """
        logger.info(f"[INFO] Escalating to Browserbase for: {url} (reason: {reason})")
        
        try:
            result_browserbase = await fetch_via_browserbase(
                url, 
                self.browserbase_api_key, 
                self.browserbase_project_id
            )
            
            if result_browserbase.get('error'):
                logger.error(f"[ERROR] Browserbase render also failed: {result_browserbase['error']}")
                return {
                    **result_browserbase,
                    'source': 'browserbase',
                    'escalation_reason': reason,
                    'detection_analysis': detection_analysis
                }
            else:
                logger.info(f"[INFO] Browserbase render successful for: {url}")
                return {
                    **result_browserbase,
                    'source': 'browserbase',
                    'escalation_reason': reason,
                    'detection_analysis': detection_analysis
                }
        
        except Exception as e:
            logger.error(f"[ERROR] Browserbase escalation failed: {str(e)}")
            return {
                'html_content': '',
                'page_title': '',
                'final_url': url,
                'status_code': 0,
                'content_length': 0,
                'render_time': 0,
                'error': f"Browserbase escalation failed: {str(e)}",
                'source': 'browserbase',
                'escalation_reason': reason,
                'detection_analysis': detection_analysis
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику использования рендерера"""
        return {
            'browserbase_available': self.browserbase_available,
            'local_timeout': self.local_timeout,
            'local_headless': self.local_headless,
            'detection_rules_count': {
                'title_keywords': len(self.detection_engine.title_blocking_keywords),
                'url_patterns': len(self.detection_engine.url_challenge_patterns),
                'html_selectors': len(self.detection_engine.html_blocking_selectors),
                'content_phrases': len(self.detection_engine.content_blocking_phrases)
            }
        }


# Удобная функция для быстрого использования
async def get_universal_html(url: str, 
                           browserbase_api_key: Optional[str] = None,
                           browserbase_project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Удобная функция для универсального рендеринга URL
    
    Args:
        url: URL для рендеринга
        browserbase_api_key: API ключ Browserbase (опционально)
        browserbase_project_id: ID проекта Browserbase (опционально)
        
    Returns:
        Результат рендеринга
    """
    renderer = UniversalRenderer(browserbase_api_key, browserbase_project_id)
    return await renderer.get_universal_html(url)


# Пример использования и тестирования
if __name__ == "__main__":
    async def test_universal_renderer():
        """Тестирование универсального рендерера"""
        
        # Тестовые URL
        test_urls = [
            "https://httpbin.org/html",  # Простая статическая страница
            "https://quotes.toscrape.com/js/",  # JS-рендеринг
            "https://example.com",  # Базовая страница
            # "https://httpbin.org/delay/5",  # Медленная страница
        ]
        
        # Создаем рендерер (без Browserbase для тестирования)
        renderer = UniversalRenderer()
        
        logger.info("=== Universal Renderer Test ===")
        logger.info(f"Browserbase available: {renderer.browserbase_available}")
        logger.info(f"Stats: {renderer.get_stats()}")
        
        for url in test_urls:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing: {url}")
            logger.info('='*60)
            
            result = await renderer.get_universal_html(url)
            
            logger.info(f"Source: {result.get('source', 'unknown')}")
            logger.info(f"Title: {result.get('page_title', 'N/A')}")
            logger.info(f"Final URL: {result.get('final_url', 'N/A')}")
            logger.info(f"Status: {result.get('status_code', 'N/A')}")
            logger.info(f"Content Length: {result.get('content_length', 0)}")
            logger.info(f"Render Time: {result.get('render_time', 0):.2f}s")
            
            if result.get('escalation_reason'):
                logger.warning(f"Escalation Reason: {result['escalation_reason']}")
            
            if result.get('detection_analysis'):
                analysis = result['detection_analysis']
                logger.info(f"Detection Confidence: {analysis.get('confidence_score', 0):.2f}")
                if analysis.get('blocking_reasons'):
                    logger.warning(f"Blocking Reasons: {', '.join(analysis['blocking_reasons'])}")
            
            if result.get('error'):
                logger.error(f"Error: {result['error']}")
    
    # Запуск тестов
    asyncio.run(test_universal_renderer())