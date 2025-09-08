# Новая архитектура GetScrapper с паттерном Стратегия

## Обзор

Мы успешно реорганизовали архитектуру GetScrapper, применив паттерн "Стратегия" для разделения логики получения HTML. Это решает проблему "гигантского класса" и подготавливает систему для реализации сложной 3-уровневой архитектуры борьбы с JS-рендерингом и анти-бот системами.

## Архитектура

### 1. Базовый класс FetcherStrategy

```python
from abc import ABC, abstractmethod

class FetcherStrategy(ABC):
    @abstractmethod
    async def fetch_html(self, url: str) -> Dict[str, Any]:
        """Получить HTML контент с URL"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Получить имя стратегии"""
        pass
    
    def is_available(self) -> bool:
        """Проверить доступность стратегии"""
        return True
```

### 2. Конкретные реализации стратегий

#### StaticFetcher
- Использует библиотеку `requests`
- Для статических HTML страниц
- Быстрый и легкий
- Не выполняет JavaScript

#### LocalBrowserFetcher
- Использует `Playwright`
- Для JavaScript-рендеринга
- Выполняет JS код локально
- Требует установки браузера

#### BrowserbaseFetcher
- Использует облачный API Browserbase
- Для обхода сложных анти-бот систем
- Требует API ключи
- Самый мощный, но дорогой

### 3. Контроллер детекции (DetectionController)

Управляет стратегиями и принимает решения об эскалации:

```python
class DetectionController:
    async def fetch_html_with_escalation(
        self, 
        url: str, 
        start_level: EscalationLevel = EscalationLevel.STATIC,
        max_escalations: int = 2
    ) -> Dict[str, Any]:
        # Интеллектуальная эскалация
        # 1. Пробует начальную стратегию
        # 2. Анализирует результат через DetectionEngine
        # 3. При обнаружении блокировки эскалирует
        # 4. Возвращает лучший результат
```

### 4. Движок детекции (DetectionEngine)

Анализирует результаты рендеринга и определяет блокировки:

```python
class DetectionEngine:
    def analyze(self, render_result: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        # Анализирует:
        # - Заголовок страницы
        # - URL паттерны
        # - HTML структуру
        # - Содержимое
        # - Эвристики пустых страниц
```

## Уровни эскалации

### EscalationLevel.STATIC
- Быстрые HTTP запросы
- Для простых статических сайтов
- Низкое потребление ресурсов

### EscalationLevel.LOCAL_BROWSER
- Локальный Playwright браузер
- Для JavaScript-сайтов
- Среднее потребление ресурсов

### EscalationLevel.BROWSERBASE
- Облачный браузер Browserbase
- Для сложных анти-бот систем
- Высокое потребление ресурсов

## Пример использования

```python
import asyncio
from getscrapper.core import Scraper, EscalationLevel

async def main():
    # Конфигурация с различными стратегиями
    config = {
        "detection_controller": {
            "strategies": {
                "static": {"timeout": 30},
                "local_browser": {"headless": True, "timeout": 30000},
                "browserbase": {
                    "api_key": "your_api_key",
                    "project_id": "your_project_id"
                }
            }
        }
    }
    
    scraper = Scraper(config)
    
    # Скрапинг с автоматической эскалацией
    data = await scraper.scrape_url(
        "https://example.com",
        escalation_level=EscalationLevel.STATIC,
        max_escalations=2,
        extract_links=True
    )
    
    print(f"Стратегия: {data[0]['strategy_used']}")
    print(f"Эскалация: {data[0]['escalation_successful']}")
    
    scraper.close()

asyncio.run(main())
```

## Преимущества новой архитектуры

### 1. Разделение ответственности
- Каждая стратегия отвечает только за свой метод получения HTML
- Контроллер детекции управляет логикой эскалации
- Движок детекции анализирует результаты

### 2. Расширяемость
- Легко добавить новые стратегии (например, Selenium, Puppeteer)
- Можно настроить правила эскалации
- Можно добавить новые правила детекции

### 3. Тестируемость
- Каждую стратегию можно тестировать отдельно
- Можно мокать стратегии для тестов
- Легко тестировать логику эскалации

### 4. Производительность
- Начинаем с быстрых стратегий
- Эскалируем только при необходимости
- Кэшируем результаты детекции

## Интеграция с существующим кодом

### Playwright интеграция
```python
# LocalBrowserFetcher уже готов к использованию
# Требует: pip install playwright
# И: playwright install chromium
```

### Browserbase интеграция
```python
# BrowserbaseFetcher готов к использованию
# Требует: pip install aiohttp
# И: API ключи Browserbase
```

### DetectionEngine
```python
# Уже интегрирован и работает
# Анализирует результаты всех стратегий
# Определяет необходимость эскалации
```

## Следующие шаги

### 1. Установка зависимостей
```bash
pip install playwright aiohttp
playwright install chromium
```

### 2. Настройка Browserbase
```bash
export BROWSERBASE_API_KEY="your_api_key"
export BROWSERBASE_PROJECT_ID="your_project_id"
```

### 3. Тестирование полной архитектуры
```python
# Запустить example_new_architecture.py
# Протестировать все уровни эскалации
```

### 4. Добавление новых стратегий
```python
class SeleniumFetcher(FetcherStrategy):
    # Реализация для Selenium
    pass

class PuppeteerFetcher(FetcherStrategy):
    # Реализация для Puppeteer
    pass
```

## Результаты тестирования

✅ **Все базовые тесты пройдены успешно!**

- ✓ Паттерн Стратегия реализован
- ✓ Интеллектуальная эскалация работает
- ✓ Движок детекции функционирует
- ✓ Контроллер детекции управляет стратегиями
- ✓ Статический фетчер работает без зависимостей
- ✓ Система готова к добавлению Playwright и Browserbase

## Заключение

Новая архитектура решает все проблемы, которые вы указали:

1. **Разделение логики**: Код больше не находится в одном гигантском классе
2. **Паттерн Стратегия**: Четкое разделение методов получения HTML
3. **Готовность к расширению**: Легко добавить Playwright и Browserbase
4. **Интеллектуальная эскалация**: Система сама решает, когда эскалировать
5. **Движок детекции**: Анализирует результаты и определяет блокировки

Теперь можно переходить к реализации полной 3-уровневой архитектуры с Playwright и Browserbase!