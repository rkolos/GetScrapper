#!/usr/bin/env python3
"""
Тест эскалации - демонстрация работы детекции блокировок
"""

import asyncio
from main_controller import UniversalRenderer
from detection_engine import DetectionEngine


async def test_escalation_scenarios():
    """Тестирование различных сценариев эскалации"""
    
    print("=== Testing Escalation Scenarios ===")
    
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
        print(f"\n--- {scenario['name']} ---")
        print(f"URL: {scenario['url']}")
        
        try:
            result = await renderer.get_universal_html(scenario['url'])
            
            print(f"Source: {result.get('source')}")
            print(f"Title: {result.get('page_title', 'N/A')}")
            print(f"Content Length: {result.get('content_length', 0)} bytes")
            print(f"Render Time: {result.get('render_time', 0):.2f}s")
            
            # Анализ детекции
            if result.get('detection_analysis'):
                analysis = result['detection_analysis']
                print(f"Detection Confidence: {analysis.get('confidence_score', 0):.2f}")
                print(f"Blocked: {analysis.get('is_blocked', False)}")
                
                if analysis.get('blocking_reasons'):
                    print("Blocking Reasons:")
                    for reason in analysis['blocking_reasons']:
                        print(f"  - {reason}")
                
                # Проверяем ожидания
                was_escalated = result.get('escalation_reason') is not None
                expected = scenario['expected_escalation']
                
                if was_escalated == expected:
                    print("✅ PASS - Escalation behavior as expected")
                else:
                    print(f"❌ FAIL - Expected escalation: {expected}, Got: {was_escalated}")
            
            if result.get('error'):
                print(f"Error: {result['error']}")
        
        except Exception as e:
            print(f"Exception: {str(e)}")


async def test_detection_engine_detailed():
    """Детальное тестирование движка детекции"""
    
    print("\n=== Detailed Detection Engine Test ===")
    
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
        print(f"\n--- {test_case['name']} ---")
        
        is_blocked, analysis = engine.analyze(test_case['data'])
        
        print(f"Blocked: {is_blocked}")
        print(f"Confidence: {analysis['confidence_score']:.2f}")
        
        if analysis['blocking_reasons']:
            print("Reasons:")
            for reason in analysis['blocking_reasons']:
                print(f"  - {reason}")
        
        # Показываем результаты по правилам
        print("Rule Results:")
        for rule, result in analysis['rule_results'].items():
            status = "BLOCKED" if result.get('blocked') else "OK"
            print(f"  {rule}: {status}")
            
            if result.get('reasons'):
                for reason in result['reasons']:
                    print(f"    - {reason}")


async def main():
    """Главная функция"""
    print("Universal Renderer - Escalation Testing")
    print("=" * 50)
    
    await test_escalation_scenarios()
    await test_detection_engine_detailed()
    
    print("\n" + "=" * 50)
    print("✅ Escalation testing completed!")


if __name__ == "__main__":
    asyncio.run(main())