# Universal HTML Renderer

Универсальный сервис рендеринга HTML с интеллектуальной эскалацией. Автоматически определяет блокировки анти-бот систем и переключается на более мощные методы рендеринга.

## Архитектура

### Уровень 2 (Baseline): Локальный Playwright
- Основной метод рендеринга
- Быстрый и бесплатный
- Работает в Docker контейнере

### Уровень 3 (Fallback): Browserbase
- Дорогой, но мощный API
- Используется только при обнаружении блокировок
- Обходит большинство анти-бот систем

### Движок Детекции
Анализирует результаты локального рендеринга по 5 правилам:

1. **Анализ заголовка** (высокий приоритет)
   - Поиск ключевых слов: "Just a moment", "Checking your browser", "Verify you are human"

2. **Анализ URL** (высокий приоритет)
   - Поиск паттернов челленджей: `/cdn-cgi/`, `/challenge-platform/`, `?chk=`

3. **Структурный анализ HTML** (высокий приоритет)
   - Поиск селекторов блокировщиков: `div[id*="cf-challenge"]`, `iframe[src*="hcaptcha.com"]`

4. **Анализ контента** (средний приоритет)
   - Поиск фраз: "DDoS protection by Cloudflare", "Protected by Incapsula"

5. **Эвристика пустой страницы** (низкий приоритет)
   - Проверка на очень маленькие страницы (< 500 байт)

## Установка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Установка браузеров Playwright
playwright install chromium

# Настройка переменных окружения (опционально)
export BROWSERBASE_API_KEY="your_api_key"
export BROWSERBASE_PROJECT_ID="your_project_id"
```

## Использование

### Python API

```python
import asyncio
from main_controller import get_universal_html

async def main():
    result = await get_universal_html("https://example.com")
    
    print(f"Source: {result['source']}")  # 'local' или 'browserbase'
    print(f"Title: {result['page_title']}")
    print(f"HTML Length: {result['content_length']}")
    print(f"Render Time: {result['render_time']:.2f}s")
    
    if result.get('escalation_reason'):
        print(f"Escalated: {result['escalation_reason']}")

asyncio.run(main())
```

### CLI Интерфейс

```bash
# Рендеринг одного URL
python cli.py https://example.com

# С детальным анализом детекции
python cli.py https://example.com --analysis

# Сохранение HTML в файл
python cli.py https://example.com --output page.html

# Пакетный рендеринг
python cli.py --batch urls.txt --output-dir results/

# С Browserbase credentials
python cli.py https://example.com --browserbase-key YOUR_KEY --browserbase-project YOUR_PROJECT
```

### Docker

```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Установка Playwright
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Копирование кода
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Запуск
CMD ["python", "cli.py"]
```

## Конфигурация

### Переменные окружения

- `BROWSERBASE_API_KEY` - API ключ Browserbase
- `BROWSERBASE_PROJECT_ID` - ID проекта Browserbase
- `RENDERER_LOG_LEVEL` - Уровень логирования (DEBUG, INFO, WARNING, ERROR)
- `RENDERER_HEADLESS` - Headless режим браузера (true/false)
- `RENDERER_TIMEOUT` - Таймаут в миллисекундах

### Настройки в config.py

```python
DEFAULT_CONFIG = {
    'local_browser': {
        'headless': True,
        'timeout': 30000,
        'wait_after_load': 2,
    },
    'detection': {
        'confidence_threshold': 0.3,
        'enable_title_check': True,
        # ... другие настройки
    }
}
```

## Структура проекта

```
universal_renderer/
├── universal_renderer.py    # Локальный рендеринг (Playwright)
├── detection_engine.py      # Движок детекции блокировок
├── browserbase_client.py    # Клиент Browserbase API
├── main_controller.py       # Главный контроллер
├── config.py               # Конфигурация
├── cli.py                  # CLI интерфейс
├── requirements.txt        # Зависимости
└── README.md              # Документация
```

## Примеры использования

### Базовый пример

```python
from main_controller import UniversalRenderer

async def render_website():
    renderer = UniversalRenderer()
    result = await renderer.get_universal_html("https://quotes.toscrape.com/js/")
    
    if result['source'] == 'local':
        print("✅ Локальный рендеринг успешен")
    else:
        print("🔄 Эскалация на Browserbase")
        print(f"Причина: {result['escalation_reason']}")
    
    return result['html_content']
```

### Пакетная обработка

```python
import asyncio
from main_controller import UniversalRenderer

async def batch_render(urls):
    renderer = UniversalRenderer()
    results = []
    
    for url in urls:
        result = await renderer.get_universal_html(url)
        results.append({
            'url': url,
            'success': not result.get('error'),
            'source': result.get('source'),
            'escalated': result.get('escalation_reason') is not None
        })
    
    return results

urls = [
    "https://httpbin.org/html",
    "https://quotes.toscrape.com/js/",
    "https://example.com"
]

results = asyncio.run(batch_render(urls))
```

## Логирование

Система ведет подробные логи:

```
2024-01-15 10:30:15 - INFO - Starting universal render for URL: https://example.com
2024-01-15 10:30:15 - INFO - Attempting local render for: https://example.com
2024-01-15 10:30:17 - INFO - Local render completed: https://example.com -> https://example.com (200) in 2.15s
2024-01-15 10:30:17 - INFO - Analyzing local render result for blocking detection
2024-01-15 10:30:17 - INFO - URL: https://example.com | Local render successful.
2024-01-15 10:30:17 - INFO - Confidence score: 0.00
```

При эскалации:

```
2024-01-15 10:30:17 - WARN - URL: https://blocked-site.com | Local render BLOCKED. Escalating to Browserbase.
2024-01-15 10:30:17 - WARN - Blocking reasons: Blocking keywords in title: Just a moment
2024-01-15 10:30:17 - WARN - Confidence score: 0.40
2024-01-15 10:30:17 - INFO - Escalating to Browserbase for: https://blocked-site.com (reason: blocking_detected)
```

## Тестирование

```bash
# Запуск тестов
python -m pytest tests/

# Тестирование CLI
python cli.py https://httpbin.org/html --analysis

# Тестирование пакетного режима
echo "https://httpbin.org/html" > test_urls.txt
echo "https://example.com" >> test_urls.txt
python cli.py --batch test_urls.txt --output-dir test_results/
```

## Производительность

- **Локальный рендеринг**: ~2-5 секунд на страницу
- **Browserbase**: ~5-15 секунд на страницу
- **Детекция блокировок**: <100ms
- **Память**: ~50-100MB на браузер

## Ограничения

1. **Browserbase**: Требует API ключ и имеет лимиты
2. **Playwright**: Может быть заблокирован продвинутыми анти-бот системами
3. **Детекция**: Ложные срабатывания возможны на легитимных страницах
4. **Производительность**: Один браузер на запрос (можно оптимизировать пулом)

## Развитие

### Планируемые улучшения

1. **Пул браузеров** для параллельной обработки
2. **Кэширование** результатов рендеринга
3. **Машинное обучение** для улучшения детекции
4. **Метрики** и мониторинг производительности
5. **Поддержка других API** (ScrapingBee, ScraperAPI)

### Добавление новых правил детекции

```python
# В detection_engine.py
def _check_custom_blocking(self, html_content: str) -> Dict[str, Any]:
    """Новое правило детекции"""
    result = {'blocked': False, 'reasons': []}
    
    # Ваша логика детекции
    if 'custom_blocking_pattern' in html_content:
        result['blocked'] = True
        result['reasons'].append("Custom blocking pattern detected")
    
    return result
```

## Лицензия

MIT License