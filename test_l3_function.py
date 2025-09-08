#!/usr/bin/env python3
"""
Тест для оптимизированной L3 функции fetch_via_browserbase
"""

import os
import sys
from getscrapper.core.fetchers.browserbase_fetcher import fetch_via_browserbase

def test_l3_function():
    """Тестирует L3 функцию с простым URL"""
    
    # Проверяем наличие API ключа
    api_key = os.environ.get("BROWSERBASE_API_KEY")
    if not api_key:
        print("❌ BROWSERBASE_API_KEY не установлен в переменных окружения")
        print("Установите ключ: export BROWSERBASE_API_KEY='your_key_here'")
        return False
    
    print(f"✅ API ключ найден: {api_key[:10]}...")
    
    # Тестовый URL
    test_url = "https://example.com"
    print(f"🔍 Тестируем URL: {test_url}")
    
    try:
        # Вызываем L3 функцию
        result = fetch_via_browserbase(test_url)
        
        if result is None:
            print("❌ L3 функция вернула None - произошла ошибка")
            return False
        
        print(f"✅ L3 функция успешно выполнилась!")
        print(f"📄 Получено символов: {len(result)}")
        print(f"📝 Первые 200 символов:")
        print("-" * 50)
        print(result[:200])
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении L3 функции: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск теста L3 функции fetch_via_browserbase")
    print("=" * 60)
    
    success = test_l3_function()
    
    print("=" * 60)
    if success:
        print("🎉 Тест прошел успешно!")
        sys.exit(0)
    else:
        print("💥 Тест провалился!")
        sys.exit(1)