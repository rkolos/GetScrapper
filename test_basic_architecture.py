"""
Базовый тест новой архитектуры без сложных зависимостей
"""

import sys
import os
import logging

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'getscrapper'))

from getscrapper.utils.logger import setup_logger

# Настройка логирования
logger = setup_logger("test_basic_architecture", "INFO")

def test_imports():
    """Тестируем импорты основных компонентов."""
    try:
        from getscrapper.core.detection_engine import DetectionEngine
        logger.info("✓ DetectionEngine импортирован успешно")
        
        from getscrapper.core.fetchers.base_fetcher import FetcherStrategy
        logger.info("✓ FetcherStrategy импортирован успешно")
        
        from getscrapper.core.fetchers.static_fetcher import StaticFetcher
        logger.info("✓ StaticFetcher импортирован успешно")
        
        from getscrapper.core.detection_controller import DetectionController, EscalationLevel
        logger.info("✓ DetectionController и EscalationLevel импортированы успешно")
        
        # Тестируем импорт без pydantic зависимостей
        from getscrapper.config.simple_settings import SimpleSettings
        logger.info("✓ SimpleSettings импортирован успешно")
        
        from getscrapper.processors.simple_validators import DataValidator
        logger.info("✓ DataValidator импортирован успешно")
        
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка импорта: {e}")
        return False

def test_detection_engine():
    """Тестируем DetectionEngine."""
    try:
        from getscrapper.core.detection_engine import DetectionEngine
        
        engine = DetectionEngine()
        logger.info("✓ DetectionEngine создан успешно")
        
        # Тестовые данные
        test_data = {
            'html_content': '<html><head><title>Normal Page</title></head><body><h1>Hello World</h1></body></html>',
            'page_title': 'Normal Page',
            'final_url': 'https://example.com',
            'status_code': 200,
            'content_length': 100
        }
        
        is_blocked, analysis = engine.analyze(test_data)
        logger.info(f"✓ Анализ выполнен: заблокировано={is_blocked}, уверенность={analysis['confidence_score']:.2f}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка DetectionEngine: {e}")
        return False

def test_escalation_levels():
    """Тестируем EscalationLevel."""
    try:
        from getscrapper.core.detection_controller import EscalationLevel
        
        levels = [EscalationLevel.STATIC, EscalationLevel.LOCAL_BROWSER, EscalationLevel.BROWSERBASE]
        logger.info(f"✓ EscalationLevel: {[level.value for level in levels]}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка EscalationLevel: {e}")
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
        logger.info("✓ DetectionController создан успешно")
        
        available = controller.get_available_strategies()
        logger.info(f"✓ Доступные стратегии: {available}")
        
        info = controller.get_strategy_info()
        logger.info(f"✓ Информация о стратегиях: {list(info.keys())}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка DetectionController: {e}")
        return False

def main():
    """Главная функция тестирования."""
    logger.info("=== Тестирование базовой архитектуры GetScrapper ===\n")
    
    tests = [
        ("Импорты", test_imports),
        ("DetectionEngine", test_detection_engine),
        ("EscalationLevel", test_escalation_levels),
        ("DetectionController", test_detection_controller),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"Тест: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} - ПРОЙДЕН\n")
            else:
                logger.error(f"✗ {test_name} - ПРОВАЛЕН\n")
        except Exception as e:
            logger.error(f"✗ {test_name} - ОШИБКА: {e}\n")
    
    logger.info(f"=== Результаты: {passed}/{total} тестов пройдено ===")
    
    if passed == total:
        logger.info("🎉 Все базовые тесты пройдены успешно!")
        return True
    else:
        logger.info("❌ Некоторые тесты провалены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)