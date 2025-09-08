#!/usr/bin/env python3
"""
Примеры использования универсального рендерера
"""

import asyncio
import json
from main_controller import UniversalRenderer, get_universal_html


async def basic_usage_example():
    """Базовый пример использования"""
    print("=== Basic Usage Example ===")
    
    # Простое использование
    url = "https://example.com"
    result = await get_universal_html(url)
    
    print(f"URL: {url}")
    print(f"Source: {result['source']}")
    print(f"Title: {result['page_title']}")
    print(f"Content Length: {result['content_length']} bytes")
    print(f"Render Time: {result['render_time']:.2f}s")
    
    if result.get('escalation_reason'):
        print(f"Escalated: {result['escalation_reason']}")


async def advanced_usage_example():
    """Продвинутый пример с настройками"""
    print("\n=== Advanced Usage Example ===")
    
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
        print(f"\nProcessing: {url}")
        result = await renderer.get_universal_html(url)
        
        results.append({
            'url': url,
            'source': result['source'],
            'title': result['page_title'],
            'content_length': result['content_length'],
            'render_time': result['render_time'],
            'escalated': result.get('escalation_reason') is not None
        })
        
        print(f"  Source: {result['source']}")
        print(f"  Title: {result['page_title']}")
        print(f"  Content: {result['content_length']} bytes")
        print(f"  Time: {result['render_time']:.2f}s")
        
        if result.get('escalation_reason'):
            print(f"  Escalated: {result['escalation_reason']}")
    
    # Сохраняем результаты
    with open('render_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to render_results.json")


async def batch_processing_example():
    """Пример пакетной обработки"""
    print("\n=== Batch Processing Example ===")
    
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
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        try:
            result = await renderer.get_universal_html(url)
            
            if result.get('error'):
                print(f"  ❌ Failed: {result['error']}")
                failed += 1
            else:
                print(f"  ✅ Success: {result['content_length']} bytes in {result['render_time']:.2f}s")
                successful += 1
                
                if result.get('escalation_reason'):
                    print(f"  🔄 Escalated: {result['escalation_reason']}")
                    escalated += 1
        
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            failed += 1
    
    print(f"\nBatch Processing Summary:")
    print(f"  Total URLs: {len(urls)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Escalated: {escalated}")
    print(f"  Success Rate: {successful/len(urls)*100:.1f}%")


async def error_handling_example():
    """Пример обработки ошибок"""
    print("\n=== Error Handling Example ===")
    
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
        print(f"\nTesting: {test_case['description']}")
        print(f"URL: {test_case['url']}")
        
        try:
            result = await renderer.get_universal_html(test_case['url'])
            
            if result.get('error'):
                print(f"  ❌ Error: {result['error']}")
            else:
                print(f"  ✅ Success: Status {result['status_code']}")
                print(f"  Content: {result['content_length']} bytes")
        
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")


async def detection_analysis_example():
    """Пример анализа детекции"""
    print("\n=== Detection Analysis Example ===")
    
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
        print(f"\n--- {test_case['expected']} ---")
        print(f"URL: {test_case['url']}")
        
        result = await renderer.get_universal_html(test_case['url'])
        
        if result.get('detection_analysis'):
            analysis = result['detection_analysis']
            
            print(f"Detection Results:")
            print(f"  Blocked: {analysis['is_blocked']}")
            print(f"  Confidence: {analysis['confidence_score']:.2f}")
            
            if analysis['blocking_reasons']:
                print("  Blocking Reasons:")
                for reason in analysis['blocking_reasons']:
                    print(f"    - {reason}")
            
            print("  Rule Results:")
            for rule, rule_result in analysis['rule_results'].items():
                status = "BLOCKED" if rule_result.get('blocked') else "OK"
                print(f"    {rule}: {status}")


async def main():
    """Главная функция с примерами"""
    print("Universal HTML Renderer - Usage Examples")
    print("=" * 60)
    
    await basic_usage_example()
    await advanced_usage_example()
    await batch_processing_example()
    await error_handling_example()
    await detection_analysis_example()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("\nTo use with Browserbase fallback:")
    print("1. Set environment variables:")
    print("   export BROWSERBASE_API_KEY='your_api_key'")
    print("   export BROWSERBASE_PROJECT_ID='your_project_id'")
    print("2. Or pass credentials directly:")
    print("   renderer = UniversalRenderer(browserbase_api_key='key', browserbase_project_id='id')")


if __name__ == "__main__":
    asyncio.run(main())