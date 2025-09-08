"""
Базовый тест новой архитектуры без сложных зависимостей
"""

import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'getscrapper'))

def test_imports():
    """Тестируем импорты основных компонентов."""
    try:
        from getscrapper.core.detection_engine import DetectionEngine
        print("✓ DetectionEngine импортирован успешно")
        
        from getscrapper.core.fetchers.base_fetcher import FetcherStrategy
        print("✓ FetcherStrategy импортирован успешно")
        
        from getscrapper.core.fetchers.static_fetcher import StaticFetcher
        print("✓ StaticFetcher импортирован успешно")
        
        from getscrapper.core.detection_controller import DetectionController, EscalationLevel
        print("✓ DetectionController и EscalationLevel импортированы успешно")
        
        # Тестируем импорт без pydantic зависимостей
        from getscrapper.config.simple_settings import SimpleSettings
        print("✓ SimpleSettings импортирован успешно")
        
        from getscrapper.processors.simple_validators import DataValidator
        print("✓ DataValidator импортирован успешно")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка импорта: {e}")
        return False

def test_detection_engine():
    """Тестируем DetectionEngine."""
    try:
        from getscrapper.core.detection_engine import DetectionEngine
        
        engine = DetectionEngine()
        print("✓ DetectionEngine создан успешно")
        
        # Тестовые данные
        test_data = {
            'html_content': '<html><head><title>Normal Page</title></head><body><h1>Hello World</h1></body></html>',
            'page_title': 'Normal Page',
            'final_url': 'https://example.com',
            'status_code': 200,
            'content_length': 100
        }
        
        is_blocked, analysis = engine.analyze(test_data)
        print(f"✓ Анализ выполнен: заблокировано={is_blocked}, уверенность={analysis['confidence_score']:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка DetectionEngine: {e}")
        return False

def test_escalation_levels():
    """Тестируем EscalationLevel."""
    try:
        from getscrapper.core.detection_controller import EscalationLevel
        
        levels = [EscalationLevel.STATIC, EscalationLevel.LOCAL_BROWSER, EscalationLevel.BROWSERBASE]
        print(f"✓ EscalationLevel: {[level.value for level in levels]}")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка EscalationLevel: {e}")
        return False

def test_detection_controller():
    """Тестируем DetectionController (без сложных стратегий)."""
    try:
        from getscrapper.core.detection_controller import DetectionController
        
        # Конфигурация только со статическим фетчером
        config = {
            "strategies": {
                "static": {"timeout": 30}
            }
        }
        
        controller = DetectionController(config)
        print("✓ DetectionController создан успешно")
        
        available = controller.get_available_strategies()
        print(f"✓ Доступные стратегии: {available}")
        
        info = controller.get_strategy_info()
        print(f"✓ Информация о стратегиях: {list(info.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка DetectionController: {e}")
        return False

def main():
    """Главная функция тестирования."""
    print("=== Тестирование базовой архитектуры GetScrapper ===\n")
    
    tests = [
        ("Импорты", test_imports),
        ("DetectionEngine", test_detection_engine),
        ("EscalationLevel", test_escalation_levels),
        ("DetectionController", test_detection_controller),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Тест: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} - ПРОЙДЕН\n")
            else:
                print(f"✗ {test_name} - ПРОВАЛЕН\n")
        except Exception as e:
            print(f"✗ {test_name} - ОШИБКА: {e}\n")
    
    print(f"=== Результаты: {passed}/{total} тестов пройдено ===")
    
    if passed == total:
        print("🎉 Все базовые тесты пройдены успешно!")
        return True
    else:
        print("❌ Некоторые тесты провалены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)