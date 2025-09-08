#!/usr/bin/env python3
"""
Простой тест API сервера
"""

import asyncio
import aiohttp
import json
import sys


async def test_api():
    """Тестирование API сервера"""
    base_url = "http://localhost:8000"
    
    print("Testing Universal HTML Renderer API")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Тест 1: Health check
        print("1. Testing health check...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    health = await response.json()
                    print(f"   ✓ API is healthy")
                    print(f"   ✓ Browserbase available: {health['browserbase_available']}")
                    print(f"   ✓ Detection rules: {health['detection_rules_count']}")
                else:
                    print(f"   ✗ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"   ✗ Health check error: {e}")
            return False
        
        # Тест 2: Single URL scraping
        print("\n2. Testing single URL scraping...")
        try:
            test_url = "https://httpbin.org/html"
            payload = {"url": test_url}
            
            async with session.post(
                f"{base_url}/scrape",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✓ Successfully scraped: {test_url}")
                    print(f"   ✓ Source: {result['source']}")
                    print(f"   ✓ Title: {result['page_title']}")
                    print(f"   ✓ Content Length: {result['content_length']} bytes")
                    print(f"   ✓ Render Time: {result['render_time']:.2f}s")
                    
                    if result.get('escalation_reason'):
                        print(f"   ✓ Escalation: {result['escalation_reason']}")
                    
                    if result.get('detection_analysis'):
                        analysis = result['detection_analysis']
                        print(f"   ✓ Detection Confidence: {analysis.get('confidence_score', 0):.2f}")
                else:
                    error_text = await response.text()
                    print(f"   ✗ Scraping failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"   ✗ Scraping error: {e}")
            return False
        
        # Тест 3: Batch scraping
        print("\n3. Testing batch scraping...")
        try:
            test_urls = [
                "https://httpbin.org/html",
                "https://example.com"
            ]
            payload = {"urls": test_urls}
            
            async with session.post(
                f"{base_url}/scrape/batch",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✓ Batch scraping completed")
                    print(f"   ✓ Total URLs: {result['total_urls']}")
                    print(f"   ✓ Successful: {result['successful']}")
                    print(f"   ✓ Failed: {result['failed']}")
                    
                    for i, url_result in enumerate(result['results'], 1):
                        print(f"   ✓ {i}. {url_result['url']} - {url_result['source']} ({url_result['render_time']:.2f}s)")
                else:
                    error_text = await response.text()
                    print(f"   ✗ Batch scraping failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"   ✗ Batch scraping error: {e}")
            return False
        
        # Тест 4: Stats
        print("\n4. Testing stats endpoint...")
        try:
            async with session.get(f"{base_url}/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(f"   ✓ Stats retrieved")
                    print(f"   ✓ Browserbase available: {stats['browserbase_available']}")
                    print(f"   ✓ Local timeout: {stats['local_timeout']}ms")
                    print(f"   ✓ Detection rules: {stats['detection_rules_count']}")
                else:
                    print(f"   ✗ Stats failed: {response.status}")
                    return False
        except Exception as e:
            print(f"   ✗ Stats error: {e}")
            return False
        
        # Тест 5: Error handling
        print("\n5. Testing error handling...")
        try:
            # Тест с неверным URL
            payload = {"url": "not-a-valid-url"}
            
            async with session.post(
                f"{base_url}/scrape",
                json=payload
            ) as response:
                if response.status == 422:  # Validation error
                    print(f"   ✓ Properly rejected invalid URL")
                else:
                    print(f"   ⚠ Unexpected response for invalid URL: {response.status}")
        except Exception as e:
            print(f"   ✗ Error handling test failed: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("✓ All tests passed! API is working correctly.")
        return True


async def main():
    """Главная функция"""
    try:
        success = await test_api()
        if not success:
            print("\n✗ Some tests failed. Check the API server.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        print("\nMake sure the API server is running:")
        print("docker-compose up api-server")
        print("or")
        print("python api_server.py")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())