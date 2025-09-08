#!/usr/bin/env python3
"""
Тестовый скрипт для проверки всех улучшений универсального рендерера
"""

import asyncio
import logging
from main_controller import UniversalRenderer
from detection_engine import DetectionEngine

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_detection_engine():
    """Тестирование улучшенного движка детекции"""
    logger.info("\n=== Тестирование движка детекции ===")
    
    engine = DetectionEngine()
    
    # Тестовые случаи
    test_cases = [
        {
            'name': 'Нормальная страница',
            'data': {
                'html_content': '<html><head><title>Нормальная страница</title></head><body><h1>Привет мир</h1></body></html>',
                'page_title': 'Нормальная страница',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 100
            }
        },
        {
            'name': 'Cloudflare challenge',
            'data': {
                'html_content': '<html><head><title>Just a moment...</title></head><body><div id="cf-challenge">Checking your browser</div></body></html>',
                'page_title': 'Just a moment...',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 200
            }
        },
        {
            'name': 'reCAPTCHA challenge',
            'data': {
                'html_content': '<html><head><title>Verify you are human</title></head><body><iframe src="https://www.google.com/recaptcha/api2/anchor"></iframe></body></html>',
                'page_title': 'Verify you are human',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 300
            }
        },
        {
            'name': 'hCaptcha challenge',
            'data': {
                'html_content': '<html><head><title>Security Check</title></head><body><iframe src="https://hcaptcha.com/1/api.js"></iframe></body></html>',
                'page_title': 'Security Check',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 250
            }
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n--- {test_case['name']} ---")
        is_blocked, analysis = engine.analyze(test_case['data'])
        logger.info(f"Заблокировано: {is_blocked}")
        logger.info(f"Уверенность: {analysis['confidence_score']:.2f}")
        if analysis['blocking_reasons']:
            logger.info(f"Причины блокировки: {', '.join(analysis['blocking_reasons'])}")


async def test_universal_renderer():
    """Тестирование универсального рендерера"""
    logger.info("\n=== Тестирование универсального рендерера ===")
    
    # Создаем рендерер с настройками по умолчанию
    renderer = UniversalRenderer()
    
    logger.info(f"Конфигурация:")
    logger.info(f"  - Browserbase доступен: {renderer.browserbase_available}")
    logger.info(f"  - Headless режим: {renderer.local_headless}")
    logger.info(f"  - Таймаут: {renderer.local_timeout}ms")
    logger.info(f"  - Переиспользование контекста: {renderer.reuse_context}")
    
    # Тестовые URL
    test_urls = [
        "https://httpbin.org/html",  # Простая статическая страница
        "https://example.com",       # Базовая страница
    ]
    
    for url in test_urls:
        logger.info(f"\n--- Тестирование: {url} ---")
        try:
            result = await renderer.get_universal_html(url)
            
            logger.info(f"Источник: {result.get('source', 'unknown')}")
            logger.info(f"Заголовок: {result.get('page_title', 'N/A')}")
            logger.info(f"Финальный URL: {result.get('final_url', 'N/A')}")
            logger.info(f"Статус: {result.get('status_code', 'N/A')}")
            logger.info(f"Длина контента: {result.get('content_length', 0)}")
            logger.info(f"Время рендеринга: {result.get('render_time', 0):.2f}s")
            
            if result.get('escalation_reason'):
                logger.info(f"Причина эскалации: {result['escalation_reason']}")
            
            if result.get('detection_analysis'):
                analysis = result['detection_analysis']
                logger.info(f"Уверенность детекции: {analysis.get('confidence_score', 0):.2f}")
                if analysis.get('blocking_reasons'):
                    logger.info(f"Причины блокировки: {', '.join(analysis['blocking_reasons'])}")
            
            if result.get('error'):
                logger.error(f"Ошибка: {result['error']}")
                
        except Exception as e:
            logger.error(f"Ошибка при тестировании {url}: {e}")


async def test_configuration():
    """Тестирование конфигурации"""
    logger.info("\n=== Тестирование конфигурации ===")
    
    from config import config
    
    logger.info("Текущая конфигурация:")
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        logger.info(f"  - {key}: {value}")
    
    logger.info(f"\nBrowserbase конфигурация валидна: {config.validate_browserbase_config()}")
    logger.info(f"User-Agent: {config.get_user_agent()}")
    logger.info(f"HTTP заголовки: {config.get_http_headers()}")


async def main():
    """Главная функция тестирования"""
    logger.info("🚀 Запуск тестирования улучшений универсального рендерера")
    
    try:
        # Тестируем конфигурацию
        await test_configuration()
        
        # Тестируем движок детекции
        await test_detection_engine()
        
        # Тестируем универсальный рендерер
        await test_universal_renderer()
        
        logger.info("\n✅ Все тесты завершены успешно!")
        
    except Exception as e:
        logger.error(f"\n❌ Ошибка при выполнении тестов: {e}")
        logger.exception("Детали ошибки:")


if __name__ == "__main__":
    asyncio.run(main())