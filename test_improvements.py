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
    print("\n=== Тестирование движка детекции ===")
    
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
        print(f"\n--- {test_case['name']} ---")
        is_blocked, analysis = engine.analyze(test_case['data'])
        print(f"Заблокировано: {is_blocked}")
        print(f"Уверенность: {analysis['confidence_score']:.2f}")
        if analysis['blocking_reasons']:
            print(f"Причины блокировки: {', '.join(analysis['blocking_reasons'])}")


async def test_universal_renderer():
    """Тестирование универсального рендерера"""
    print("\n=== Тестирование универсального рендерера ===")
    
    # Создаем рендерер с настройками по умолчанию
    renderer = UniversalRenderer()
    
    print(f"Конфигурация:")
    print(f"  - Browserbase доступен: {renderer.browserbase_available}")
    print(f"  - Headless режим: {renderer.local_headless}")
    print(f"  - Таймаут: {renderer.local_timeout}ms")
    print(f"  - Переиспользование контекста: {renderer.reuse_context}")
    
    # Тестовые URL
    test_urls = [
        "https://httpbin.org/html",  # Простая статическая страница
        "https://example.com",       # Базовая страница
    ]
    
    for url in test_urls:
        print(f"\n--- Тестирование: {url} ---")
        try:
            result = await renderer.get_universal_html(url)
            
            print(f"Источник: {result.get('source', 'unknown')}")
            print(f"Заголовок: {result.get('page_title', 'N/A')}")
            print(f"Финальный URL: {result.get('final_url', 'N/A')}")
            print(f"Статус: {result.get('status_code', 'N/A')}")
            print(f"Длина контента: {result.get('content_length', 0)}")
            print(f"Время рендеринга: {result.get('render_time', 0):.2f}s")
            
            if result.get('escalation_reason'):
                print(f"Причина эскалации: {result['escalation_reason']}")
            
            if result.get('detection_analysis'):
                analysis = result['detection_analysis']
                print(f"Уверенность детекции: {analysis.get('confidence_score', 0):.2f}")
                if analysis.get('blocking_reasons'):
                    print(f"Причины блокировки: {', '.join(analysis['blocking_reasons'])}")
            
            if result.get('error'):
                print(f"Ошибка: {result['error']}")
                
        except Exception as e:
            print(f"Ошибка при тестировании {url}: {e}")


async def test_configuration():
    """Тестирование конфигурации"""
    print("\n=== Тестирование конфигурации ===")
    
    from config import config
    
    print("Текущая конфигурация:")
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        print(f"  - {key}: {value}")
    
    print(f"\nBrowserbase конфигурация валидна: {config.validate_browserbase_config()}")
    print(f"User-Agent: {config.get_user_agent()}")
    print(f"HTTP заголовки: {config.get_http_headers()}")


async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестирования улучшений универсального рендерера")
    
    try:
        # Тестируем конфигурацию
        await test_configuration()
        
        # Тестируем движок детекции
        await test_detection_engine()
        
        # Тестируем универсальный рендерер
        await test_universal_renderer()
        
        print("\n✅ Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        logger.exception("Детали ошибки:")


if __name__ == "__main__":
    asyncio.run(main())