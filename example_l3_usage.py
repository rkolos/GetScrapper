#!/usr/bin/env python3
"""
Пример использования оптимизированной L3 функции fetch_via_browserbase

Эта функция использует БЕССЕССИОННЫЙ эндпоинт /v1/scrape для получения
только текстового контента, обходя JS и защиту.
"""

import os
from getscrapper.core.fetchers.browserbase_fetcher import fetch_via_browserbase

def main():
    """Демонстрация использования L3 функции"""
    
    # Убедитесь, что установлена переменная окружения
    if not os.environ.get("BROWSERBASE_API_KEY"):
        print("❌ Установите BROWSERBASE_API_KEY в переменных окружения")
        print("export BROWSERBASE_API_KEY='your_api_key_here'")
        return
    
    # Примеры URL для тестирования
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://quotes.toscrape.com/"
    ]
    
    print("🚀 Тестирование L3 функции fetch_via_browserbase")
    print("=" * 60)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📄 Тест {i}: {url}")
        print("-" * 40)
        
        try:
            # Вызываем L3 функцию
            result = fetch_via_browserbase(url)
            
            if result is None:
                print("❌ Ошибка: функция вернула None")
                continue
            
            print(f"✅ Успешно получено {len(result)} символов")
            print(f"📝 Первые 150 символов:")
            print(result[:150])
            print("...")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    main()