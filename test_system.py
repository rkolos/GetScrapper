#!/usr/bin/env python3
"""
Тестирование универсального рендерера
"""

import asyncio
import sys
import logging
from main_controller import UniversalRenderer
from detection_engine import DetectionEngine
from getscrapper.utils.logger import setup_logger

# Настройка логирования
logger = setup_logger("test_system", "INFO")


async def test_detection_engine():
    """Тестирование движка детекции"""
    logger.info("=== Testing Detection Engine ===")
    
    engine = DetectionEngine()
    
    # Тестовые случаи
    test_cases = [
        {
            'name': 'Normal page',
            'data': {
                'html_content': '<html><head><title>Welcome to Example</title></head><body><h1>Hello World</h1><p>This is a normal page.</p></body></html>',
                'page_title': 'Welcome to Example',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 150
            },
            'expected_blocked': False
        },
        {
            'name': 'Cloudflare challenge',
            'data': {
                'html_content': '<html><head><title>Just a moment...</title></head><body><div id="cf-challenge">Checking your browser before accessing</div></body></html>',
                'page_title': 'Just a moment...',
                'final_url': 'https://example.com/cdn-cgi/challenge',
                'status_code': 200,
                'content_length': 200
            },
            'expected_blocked': True
        },
        {
            'name': 'Empty page',
            'data': {
                'html_content': '<html><head><title></title></head><body></body></html>',
                'page_title': '',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 80
            },
            'expected_blocked': True
        },
        {
            'name': 'Captcha page',
            'data': {
                'html_content': '<html><head><title>Verify you are human</title></head><body><div class="g-recaptcha">Please complete the captcha</div></body></html>',
                'page_title': 'Verify you are human',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 180
            },
            'expected_blocked': True
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n--- {test_case['name']} ---")
        is_blocked, analysis = engine.analyze(test_case['data'])
        
        logger.info(f"Expected blocked: {test_case['expected_blocked']}")
        logger.info(f"Actual blocked: {is_blocked}")
        logger.info(f"Confidence: {analysis['confidence_score']:.2f}")
        
        if analysis['blocking_reasons']:
            logger.info(f"Reasons: {', '.join(analysis['blocking_reasons'])}")
        
        # Проверяем результат
        if is_blocked == test_case['expected_blocked']:
            logger.info("✅ PASS")
        else:
            logger.error("❌ FAIL")
            return False
    
    logger.info("\n✅ All detection engine tests passed!")
    return True


async def test_universal_renderer():
    """Тестирование универсального рендерера"""
    logger.info("\n=== Testing Universal Renderer ===")
    
    # Создаем рендерер без Browserbase для тестирования
    renderer = UniversalRenderer()
    
    # Тестовые URL
    test_urls = [
        {
            'url': 'https://httpbin.org/html',
            'name': 'Static HTML page',
            'expect_local': True
        },
        {
            'url': 'https://example.com',
            'name': 'Basic example page',
            'expect_local': True
        }
    ]
    
    for test_case in test_urls:
        logger.info(f"\n--- {test_case['name']} ---")
        logger.info(f"URL: {test_case['url']}")
        
        try:
            result = await renderer.get_universal_html(test_case['url'])
            
            logger.info(f"Source: {result.get('source', 'unknown')}")
            logger.info(f"Title: {result.get('page_title', 'N/A')}")
            logger.info(f"Status: {result.get('status_code', 'N/A')}")
            logger.info(f"Content Length: {result.get('content_length', 0)}")
            logger.info(f"Render Time: {result.get('render_time', 0):.2f}s")
            
            if result.get('escalation_reason'):
                logger.info(f"Escalation: {result['escalation_reason']}")
            
            if result.get('error'):
                logger.info(f"Error: {result['error']}")
                logger.error("❌ FAIL - Render error")
                return False
            
            # Проверяем ожидания
            if test_case['expect_local'] and result.get('source') != 'local':
                logger.error("❌ FAIL - Expected local render")
                return False
            
            logger.info("✅ PASS")
            
        except Exception as e:
            logger.error(f"❌ FAIL - Exception: {str(e)}")
            return False
    
    logger.info("\n✅ All universal renderer tests passed!")
    return True


async def test_integration():
    """Интеграционный тест"""
    logger.info("\n=== Integration Test ===")
    
    renderer = UniversalRenderer()
    
    # Тестируем полный цикл
    test_url = "https://httpbin.org/html"
    logger.info(f"Testing full cycle with: {test_url}")
    
    result = await renderer.get_universal_html(test_url)
    
    # Проверяем структуру результата
    required_fields = ['html_content', 'page_title', 'final_url', 'status_code', 
                      'content_length', 'render_time', 'source']
    
    for field in required_fields:
        if field not in result:
            logger.error(f"❌ FAIL - Missing field: {field}")
            return False
    
    # Проверяем, что HTML не пустой
    if not result['html_content']:
        logger.error("❌ FAIL - Empty HTML content")
        return False
    
    # Проверяем, что время рендеринга разумное
    if result['render_time'] < 0 or result['render_time'] > 60:
        logger.error(f"❌ FAIL - Unreasonable render time: {result['render_time']}")
        return False
    
    logger.info("✅ Integration test passed!")
    return True


async def main():
    """Главная функция тестирования"""
    logger.info("Universal Renderer System Test")
    logger.info("=" * 50)
    
    tests = [
        ("Detection Engine", test_detection_engine),
        ("Universal Renderer", test_universal_renderer),
        ("Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                logger.error(f"\n❌ {test_name} test failed!")
                sys.exit(1)
        except Exception as e:
            logger.error(f"\n❌ {test_name} test crashed: {str(e)}")
            sys.exit(1)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"All tests passed! ({passed}/{total})")
    logger.info("✅ System is ready for use!")


if __name__ == "__main__":
    asyncio.run(main())