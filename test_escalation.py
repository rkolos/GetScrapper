#!/usr/bin/env python3
"""
Тест эскалации - демонстрация работы детекции блокировок
"""

import asyncio
import logging
from main_controller import UniversalRenderer
from detection_engine import DetectionEngine
from getscrapper.utils.logger import setup_logger

# Настройка логирования
logger = setup_logger("test_escalation", "INFO")


async def test_escalation_scenarios():
    """Тестирование различных сценариев эскалации"""
    
    logger.info("=== Testing Escalation Scenarios ===")
    
    # Создаем рендерер без Browserbase для демонстрации детекции
    renderer = UniversalRenderer()
    engine = DetectionEngine()
    
    # Тестовые сценарии
    test_scenarios = [
        {
            'name': 'Normal Website',
            'url': 'https://example.com',
            'expected_escalation': False
        },
        {
            'name': 'JS-Heavy Website',
            'url': 'https://quotes.toscrape.com/js/',
            'expected_escalation': False
        },
        {
            'name': 'Static HTML',
            'url': 'https://httpbin.org/html',
            'expected_escalation': False
        }
    ]
    
    for scenario in test_scenarios:
        logger.info(f"\n--- {scenario['name']} ---")
        logger.info(f"URL: {scenario['url']}")
        
        try:
            result = await renderer.get_universal_html(scenario['url'])
            
            logger.info(f"Source: {result.get('source')}")
            logger.info(f"Title: {result.get('page_title', 'N/A')}")
            logger.info(f"Content Length: {result.get('content_length', 0)} bytes")
            logger.info(f"Render Time: {result.get('render_time', 0):.2f}s")
            
            # Анализ детекции
            if result.get('detection_analysis'):
                analysis = result['detection_analysis']
                logger.info(f"Detection Confidence: {analysis.get('confidence_score', 0):.2f}")
                logger.info(f"Blocked: {analysis.get('is_blocked', False)}")
                
                if analysis.get('blocking_reasons'):
                    logger.info("Blocking Reasons:")
                    for reason in analysis['blocking_reasons']:
                        logger.info(f"  - {reason}")
                
                # Проверяем ожидания
                was_escalated = result.get('escalation_reason') is not None
                expected = scenario['expected_escalation']
                
                if was_escalated == expected:
                    logger.info("✅ PASS - Escalation behavior as expected")
                else:
                    logger.error(f"❌ FAIL - Expected escalation: {expected}, Got: {was_escalated}")
            
            if result.get('error'):
                logger.error(f"Error: {result['error']}")
        
        except Exception as e:
            logger.error(f"Exception: {str(e)}")


async def test_detection_engine_detailed():
    """Детальное тестирование движка детекции"""
    
    logger.info("\n=== Detailed Detection Engine Test ===")
    
    engine = DetectionEngine()
    
    # Создаем различные тестовые случаи
    test_cases = [
        {
            'name': 'Cloudflare Challenge',
            'data': {
                'html_content': '''
                <html>
                <head><title>Just a moment...</title></head>
                <body>
                    <div id="cf-challenge">Checking your browser before accessing</div>
                    <script>setTimeout(function(){window.location.href="/"}, 5000);</script>
                </body>
                </html>
                ''',
                'page_title': 'Just a moment...',
                'final_url': 'https://example.com/cdn-cgi/challenge',
                'status_code': 200,
                'content_length': 300
            }
        },
        {
            'name': 'Captcha Page',
            'data': {
                'html_content': '''
                <html>
                <head><title>Verify you are human</title></head>
                <body>
                    <div class="g-recaptcha" data-sitekey="test"></div>
                    <p>Please complete the captcha to continue</p>
                </body>
                </html>
                ''',
                'page_title': 'Verify you are human',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 250
            }
        },
        {
            'name': 'DDoS Protection Message',
            'data': {
                'html_content': '''
                <html>
                <head><title>Access Denied</title></head>
                <body>
                    <h1>DDoS protection by Cloudflare</h1>
                    <p>This site is protected by Cloudflare</p>
                </body>
                </html>
                ''',
                'page_title': 'Access Denied',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 200
            }
        },
        {
            'name': 'Normal Content Page',
            'data': {
                'html_content': '''
                <html>
                <head><title>Welcome to Our Site</title></head>
                <body>
                    <h1>Welcome!</h1>
                    <p>This is a normal website with lots of content.</p>
                    <p>We have articles, products, and services.</p>
                    <div class="content">
                        <p>More content here...</p>
                    </div>
                </body>
                </html>
                ''',
                'page_title': 'Welcome to Our Site',
                'final_url': 'https://example.com',
                'status_code': 200,
                'content_length': 400
            }
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n--- {test_case['name']} ---")
        
        is_blocked, analysis = engine.analyze(test_case['data'])
        
        logger.info(f"Blocked: {is_blocked}")
        logger.info(f"Confidence: {analysis['confidence_score']:.2f}")
        
        if analysis['blocking_reasons']:
            logger.info("Reasons:")
            for reason in analysis['blocking_reasons']:
                logger.info(f"  - {reason}")
        
        # Показываем результаты по правилам
        logger.info("Rule Results:")
        for rule, result in analysis['rule_results'].items():
            status = "BLOCKED" if result.get('blocked') else "OK"
            logger.info(f"  {rule}: {status}")
            
            if result.get('reasons'):
                for reason in result['reasons']:
                    logger.info(f"    - {reason}")


async def main():
    """Главная функция"""
    logger.info("Universal Renderer - Escalation Testing")
    logger.info("=" * 50)
    
    await test_escalation_scenarios()
    await test_detection_engine_detailed()
    
    logger.info("\n" + "=" * 50)
    logger.info("✅ Escalation testing completed!")


if __name__ == "__main__":
    asyncio.run(main())