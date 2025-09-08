"""
Пример использования новой архитектуры GetScrapper с паттерном Стратегия
Демонстрирует интеллектуальную эскалацию и детекцию блокировок
"""

import asyncio
import logging
from getscrapper.core.scraper import Scraper
from getscrapper.core.detection_controller import EscalationLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_new_architecture():
    """Тестирование новой архитектуры с различными стратегиями."""
    
    # Конфигурация с различными стратегиями
    config = {
        "detection_controller": {
            "strategies": {
                "static": {
                    "timeout": 30,
                    "retries": 3,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                "local_browser": {
                    "headless": True,
                    "timeout": 30000,
                    "block_resources": ["image", "font", "media"]
                },
                "browserbase": {
                    # API ключи можно задать через переменные окружения
                    # BROWSERBASE_API_KEY и BROWSERBASE_PROJECT_ID
                }
            },
            "escalation_rules": {
                "max_escalations": 2,
                "confidence_threshold": 0.3
            }
        },
        "parser": {
            "extract_links": True,
            "extract_images": True,
            "extract_meta": True
        },
        "output_dir": "./output_new_arch"
    }
    
    # Создаем скрапер с новой архитектурой
    scraper = Scraper(config)
    
    # Тестовые URL
    test_urls = [
        "https://httpbin.org/html",  # Простая статическая страница
        "https://quotes.toscrape.com/js/",  # JS-рендеринг
        "https://example.com",  # Базовая страница
        # "https://httpbin.org/delay/5",  # Медленная страница
    ]
    
    logger.info("=== Новая архитектура GetScrapper ===")
    logger.info(f"Доступные стратегии: {scraper.detection_controller.get_available_strategies()}")
    logger.info(f"Информация о стратегиях: {scraper.detection_controller.get_strategy_info()}")
    logger.info()
    
    for url in test_urls:
        logger.info(f"\n{'='*60}")
        logger.info(f"Тестирование: {url}")
        logger.info('='*60)
        
        try:
            # Скрапинг с автоматической эскалацией
            data = await scraper.scrape_url(
                url,
                escalation_level=EscalationLevel.STATIC,  # Начинаем со статического
                max_escalations=2,  # Максимум 2 эскалации
                extract_links=True,
                extract_meta=True,
                save_data=False
            )
            
            if data:
                # Показываем результаты
                first_item = data[0]
                logger.info(f"Успешно получено {len(data)} элементов")
                logger.info(f"Стратегия: {first_item.get('strategy_used', 'unknown')}")
                logger.info(f"Уровень эскалации: {first_item.get('escalation_level', 0)}")
                logger.info(f"Эскалация успешна: {first_item.get('escalation_successful', False)}")
                logger.info(f"Финальный URL: {first_item.get('final_url', 'N/A')}")
                logger.info(f"Время рендеринга: {first_item.get('render_time', 0):.2f}s")
                
                # Показываем анализ детекции если есть
                if 'detection_analysis' in first_item:
                    analysis = first_item['detection_analysis']
                    logger.info(f"Анализ детекции:")
                    logger.info(f"  - Заблокировано: {analysis.get('is_blocked', False)}")
                    logger.info(f"  - Уверенность: {analysis.get('confidence_score', 0):.2f}")
                    if analysis.get('blocking_reasons'):
                        logger.info(f"  - Причины блокировки: {', '.join(analysis['blocking_reasons'])}")
                
                # Показываем извлеченные данные
                if first_item.get('type') == 'link':
                    logger.info(f"Извлеченные ссылки: {len([item for item in data if item.get('type') == 'link'])}")
                if first_item.get('type') == 'image':
                    logger.info(f"Извлеченные изображения: {len([item for item in data if item.get('type') == 'image'])}")
                
            else:
                logger.info("Не удалось получить данные")
                
        except Exception as e:
            logger.info(f"Ошибка при скрапинге: {str(e)}")
    
    # Показываем статистику
    logger.info(f"\n{'='*60}")
    logger.info("Статистика скрапинга:")
    logger.info('='*60)
    stats = scraper.get_scraping_stats()
    logger.info(f"Посещенные URL: {stats['visited_urls_count']}")
    logger.info(f"Доступные стратегии: {stats['available_strategies']}")
    logger.info(f"Уровень эскалации по умолчанию: {stats['default_escalation_level']}")
    
    # Закрываем скрапер
    scraper.close()


async def test_escalation_levels():
    """Тестирование различных уровней эскалации."""
    
    config = {
        "detection_controller": {
            "strategies": {
                "static": {"timeout": 10},  # Короткий таймаут для демонстрации
                "local_browser": {"headless": True, "timeout": 15000},
                "browserbase": {}  # Без API ключей для демонстрации
            }
        }
    }
    
    scraper = Scraper(config)
    
    test_url = "https://quotes.toscrape.com/js/"
    
    logger.info(f"\n{'='*60}")
    logger.info("Тестирование различных уровней эскалации")
    logger.info('='*60)
    
    # Тест 1: Начинаем со статического
    logger.info(f"\n1. Начинаем со статического уровня:")
    data = await scraper.scrape_url(
        test_url,
        escalation_level=EscalationLevel.STATIC,
        max_escalations=2
    )
    if data:
        logger.info(f"   Результат: {data[0].get('strategy_used')} (уровень {data[0].get('escalation_level')})")
    
    # Тест 2: Начинаем с локального браузера
    logger.info(f"\n2. Начинаем с локального браузера:")
    data = await scraper.scrape_url(
        test_url,
        escalation_level=EscalationLevel.LOCAL_BROWSER,
        max_escalations=1
    )
    if data:
        logger.info(f"   Результат: {data[0].get('strategy_used')} (уровень {data[0].get('escalation_level')})")
    
    # Тест 3: Начинаем с Browserbase (если доступен)
    logger.info(f"\n3. Начинаем с Browserbase:")
    data = await scraper.scrape_url(
        test_url,
        escalation_level=EscalationLevel.BROWSERBASE,
        max_escalations=0
    )
    if data:
        logger.info(f"   Результат: {data[0].get('strategy_used')} (уровень {data[0].get('escalation_level')})")
    
    scraper.close()


async def test_recursive_scraping():
    """Тестирование рекурсивного скрапинга с новой архитектурой."""
    
    config = {
        "detection_controller": {
            "strategies": {
                "static": {"timeout": 30},
                "local_browser": {"headless": True, "timeout": 30000}
            }
        },
        "parser": {"extract_links": True}
    }
    
    scraper = Scraper(config)
    
    logger.info(f"\n{'='*60}")
    logger.info("Тестирование рекурсивного скрапинга")
    logger.info('='*60)
    
    start_url = "https://quotes.toscrape.com/"
    
    try:
        data = await scraper.scrape_recursive(
            start_url,
            max_depth=1,  # Ограничиваем глубину для демонстрации
            same_domain_only=True,
            escalation_level=EscalationLevel.STATIC
        )
        
        logger.info(f"Рекурсивно получено {len(data)} элементов")
        
        # Группируем по типам
        links = [item for item in data if item.get('type') == 'link']
        texts = [item for item in data if item.get('type') == 'text']
        
        logger.info(f"Ссылки: {len(links)}")
        logger.info(f"Тексты: {len(texts)}")
        
        # Показываем уникальные стратегии
        strategies_used = set(item.get('strategy_used', 'unknown') for item in data)
        logger.info(f"Использованные стратегии: {', '.join(strategies_used)}")
        
    except Exception as e:
        logger.info(f"Ошибка при рекурсивном скрапинге: {str(e)}")
    
    scraper.close()


async def main():
    """Главная функция для запуска всех тестов."""
    logger.info("Запуск тестов новой архитектуры GetScrapper...")
    
    try:
        await test_new_architecture()
        await test_escalation_levels()
        await test_recursive_scraping()
        
        logger.info(f"\n{'='*60}")
        logger.info("Все тесты завершены успешно!")
        logger.info('='*60)
        
    except Exception as e:
        logger.info(f"Ошибка в тестах: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())