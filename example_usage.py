#!/usr/bin/env python3
"""
Примеры использования универсального рендерера
"""

import asyncio
import json
import logging
from main_controller import UniversalRenderer, get_universal_html
from getscrapper.utils.logger import setup_logger

# Настройка логирования
logger = setup_logger("example_usage", "INFO")


async def basic_usage_example():
    """Базовый пример использования"""
    logger.info("=== Basic Usage Example ===")
    
    # Простое использование
    url = "https://example.com"
    result = await get_universal_html(url)
    
    logger.info(f"URL: {url}")
    logger.info(f"Source: {result['source']}")
    logger.info(f"Title: {result['page_title']}")
    logger.info(f"Content Length: {result['content_length']} bytes")
    logger.info(f"Render Time: {result['render_time']:.2f}s")
    
    if result.get('escalation_reason'):
        logger.info(f"Escalated: {result['escalation_reason']}")


async def advanced_usage_example():
    """Продвинутый пример с настройками"""
    logger.info("\n=== Advanced Usage Example ===")
    
    # Создаем рендерер с настройками
    renderer = UniversalRenderer(
        local_timeout=15000,  # 15 секунд
        local_headless=True
    )
    
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://quotes.toscrape.com/js/"
    ]
    
    results = []
    
    for url in urls:
        logger.info(f"\nProcessing: {url}")
        result = await renderer.get_universal_html(url)
        
        results.append({
            'url': url,
            'source': result['source'],
            'title': result['page_title'],
            'content_length': result['content_length'],
            'render_time': result['render_time'],
            'escalated': result.get('escalation_reason') is not None
        })
        
        logger.info(f"  Source: {result['source']}")
        logger.info(f"  Title: {result['page_title']}")
        logger.info(f"  Content: {result['content_length']} bytes")
        logger.info(f"  Time: {result['render_time']:.2f}s")
        
        if result.get('escalation_reason'):
            logger.info(f"  Escalated: {result['escalation_reason']}")
    
    # Сохраняем результаты
    with open('render_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\nResults saved to render_results.json")


async def batch_processing_example():
    """Пример пакетной обработки"""
    logger.info("\n=== Batch Processing Example ===")
    
    # Список URL для обработки
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://quotes.toscrape.com/js/",
        "https://httpbin.org/json",
        "https://httpbin.org/xml"
    ]
    
    renderer = UniversalRenderer()
    
    # Обрабатываем URL последовательно
    successful = 0
    failed = 0
    escalated = 0
    
    for i, url in enumerate(urls, 1):
        logger.info(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        try:
            result = await renderer.get_universal_html(url)
            
            if result.get('error'):
                logger.info(f"  ❌ Failed: {result['error']}")
                failed += 1
            else:
                logger.info(f"  ✅ Success: {result['content_length']} bytes in {result['render_time']:.2f}s")
                successful += 1
                
                if result.get('escalation_reason'):
                    logger.info(f"  🔄 Escalated: {result['escalation_reason']}")
                    escalated += 1
        
        except Exception as e:
            logger.info(f"  ❌ Exception: {str(e)}")
            failed += 1
    
    logger.info(f"\nBatch Processing Summary:")
    logger.info(f"  Total URLs: {len(urls)}")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Escalated: {escalated}")
    logger.info(f"  Success Rate: {successful/len(urls)*100:.1f}%")


async def error_handling_example():
    """Пример обработки ошибок"""
    logger.info("\n=== Error Handling Example ===")
    
    # Тестируем различные типы ошибок
    test_cases = [
        {
            'url': 'https://httpbin.org/status/404',
            'description': '404 Not Found'
        },
        {
            'url': 'https://httpbin.org/status/500',
            'description': '500 Server Error'
        },
        {
            'url': 'https://nonexistent-domain-12345.com',
            'description': 'DNS Error'
        },
        {
            'url': 'https://httpbin.org/delay/10',
            'description': 'Timeout (may fail)'
        }
    ]
    
    renderer = UniversalRenderer(local_timeout=5000)  # 5 секунд
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['description']}")
        logger.info(f"URL: {test_case['url']}")
        
        try:
            result = await renderer.get_universal_html(test_case['url'])
            
            if result.get('error'):
                logger.info(f"  ❌ Error: {result['error']}")
            else:
                logger.info(f"  ✅ Success: Status {result['status_code']}")
                logger.info(f"  Content: {result['content_length']} bytes")
        
        except Exception as e:
            logger.info(f"  ❌ Exception: {str(e)}")


async def detection_analysis_example():
    """Пример анализа детекции"""
    logger.info("\n=== Detection Analysis Example ===")
    
    # Тестируем детекцию на различных типах контента
    test_urls = [
        {
            'url': 'https://example.com',
            'expected': 'Normal page'
        },
        {
            'url': 'https://httpbin.org/html',
            'expected': 'Static HTML'
        },
        {
            'url': 'https://quotes.toscrape.com/js/',
            'expected': 'JS-rendered content'
        }
    ]
    
    renderer = UniversalRenderer()
    
    for test_case in test_urls:
        logger.info(f"\n--- {test_case['expected']} ---")
        logger.info(f"URL: {test_case['url']}")
        
        result = await renderer.get_universal_html(test_case['url'])
        
        if result.get('detection_analysis'):
            analysis = result['detection_analysis']
            
            logger.info(f"Detection Results:")
            logger.info(f"  Blocked: {analysis['is_blocked']}")
            logger.info(f"  Confidence: {analysis['confidence_score']:.2f}")
            
            if analysis['blocking_reasons']:
                logger.info("  Blocking Reasons:")
                for reason in analysis['blocking_reasons']:
                    logger.info(f"    - {reason}")
            
            logger.info("  Rule Results:")
            for rule, rule_result in analysis['rule_results'].items():
                status = "BLOCKED" if rule_result.get('blocked') else "OK"
                logger.info(f"    {rule}: {status}")


async def main():
    """Главная функция с примерами"""
    logger.info("Universal HTML Renderer - Usage Examples")
    logger.info("=" * 60)
    
    await basic_usage_example()
    await advanced_usage_example()
    await batch_processing_example()
    await error_handling_example()
    await detection_analysis_example()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ All examples completed!")
    logger.info("\nTo use with Browserbase fallback:")
    logger.info("1. Set environment variables:")
    logger.info("   export BROWSERBASE_API_KEY='your_api_key'")
    logger.info("   export BROWSERBASE_PROJECT_ID='your_project_id'")
    logger.info("2. Or pass credentials directly:")
    logger.info("   renderer = UniversalRenderer(browserbase_api_key='key', browserbase_project_id='id')")


if __name__ == "__main__":
    asyncio.run(main())