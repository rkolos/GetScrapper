# Критические исправления GetScrapper

Этот документ описывает критические исправления, которые были применены к GetScrapper для устранения проблем, которые могли привести к сбою скрипта, бану IP или некорректной работе на большинстве сайтов.

## 🔴 Исправленные критические проблемы

### 1. Отсутствие User-Agent (Самая критическая проблема)

**Проблема:** Скрипт отправлял запросы без заголовка User-Agent или с нереалистичным User-Agent. Серверы видели, что запрос идет от скрипта (например, `python-requests/2.x.x`), а не от браузера. 99% сайтов немедленно блокируют такие запросы (часто выдавая ошибку 403 Forbidden).

**Исправление:** 
- Заменен User-Agent на реалистичный браузерный: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36`
- Добавлены дополнительные браузерные заголовки в `SessionManager`

**Файл:** `getscrapper/core/session.py`
```python
self.user_agent = self.config.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
```

### 2. Отсутствие кодировки при записи файла

**Проблема:** При записи файлов не была явно указана кодировка UTF-8. Если сайт содержал кириллицу, эмодзи или любые символы, кроме базовых латинских, скрипт мог аварийно завершиться с ошибкой `UnicodeEncodeError` или записать "кракозябры".

**Исправление:** 
- Все операции записи файлов теперь явно используют кодировку UTF-8
- Настроена кодировка по умолчанию в классах хранения

**Файлы:** `getscrapper/storage/csv_storage.py`, `getscrapper/storage/json_storage.py`
```python
# CSV Storage
self.encoding = self.config.get("encoding", "utf-8")
df.to_csv(output_path, encoding=self.encoding, ...)

# JSON Storage  
with open(output_path, 'w', encoding=self.encoding) as f:
    json.dump(data, f, ...)
```

### 3. Некорректная обработка ссылок (Рекурсия)

**Проблема:** Логика обработки ссылок была фундаментально ошибочной. Скрипт проверял только `if link.startswith('http')`, игнорируя относительные ссылки (например, `/about` или `products/item1`). Парсер никогда не переходил вглубь сайта.

**Исправление:**
- Добавлена нормализация ссылок с использованием `urllib.parse.urljoin`
- Относительные пути теперь правильно превращаются в полные URL
- Добавлена поддержка базового URL в HTML парсере

**Файлы:** `getscrapper/parsers/html_parser.py`, `getscrapper/core/scraper.py`
```python
# В HTMLParser
from urllib.parse import urljoin, urlparse

def _extract_links(self, soup: BeautifulSoup, base_url: str = "") -> List[Dict[str, Any]]:
    for link in links:
        href = link.get("href")
        # Нормализация URL: превращаем /path в https://domain.com/path
        if base_url and href:
            full_url = urljoin(base_url, href)
        else:
            full_url = href
```

### 4. Добавлена функциональность рекурсивного скрапинга

**Новая функциональность:**
- Метод `scrape_recursive()` для рекурсивного скрапинга с контролем глубины
- Отслеживание посещенных URL для предотвращения зацикливания
- Возможность ограничить скрапинг только одним доменом
- Контроль глубины рекурсии

**Файл:** `getscrapper/core/scraper.py`
```python
def scrape_recursive(self, start_url: str, max_depth: int = 2, **kwargs) -> List[Dict[str, Any]]:
    """
    Scrape URLs recursively following links.
    
    Args:
        start_url: Starting URL to scrape
        max_depth: Maximum depth to follow links (default: 2)
        **kwargs: Additional scraping parameters:
            - same_domain_only: Only follow links from the same domain (default: True)
            - extract_links: Whether to extract links (default: True)
            - continue_on_error: Whether to continue on errors (default: True)
    """
```

### 5. Предотвращение зацикливания

**Проблема:** Рекурсивный скрапинг мог привести к бесконечным циклам при наличии циклических ссылок.

**Исправление:**
- Добавлено отслеживание посещенных URL в множестве `self.visited_urls`
- Каждый URL проверяется перед повторным посещением
- Автоматическая очистка при новом рекурсивном скрапинге

## 🚀 Использование исправленного скрапера

### Простой скрапинг
```python
from getscrapper import Scraper

config = {
    "session": {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "timeout": 10,
        "delay": 1
    },
    "storage": {
        "encoding": "utf-8"
    }
}

with Scraper(config) as scraper:
    data = scraper.scrape_url(
        "https://example.com",
        extract_links=True,
        save_data=True,
        output_format="json"
    )
```

### Рекурсивный скрапинг
```python
with Scraper(config) as scraper:
    data = scraper.scrape_recursive(
        "https://example.com",
        max_depth=2,
        same_domain_only=True,
        save_data=True,
        output_format="json"
    )
```

## ✅ Результат исправлений

После применения этих исправлений GetScrapper:

1. **Не блокируется сайтами** - реалистичный User-Agent позволяет проходить большинство проверок
2. **Корректно работает с кириллицей** - UTF-8 кодировка обеспечивает правильное сохранение данных
3. **Правильно обрабатывает ссылки** - относительные ссылки превращаются в полные URL
4. **Поддерживает рекурсивный скрапинг** - может исследовать сайт на заданную глубину
5. **Предотвращает зацикливание** - отслеживание посещенных URL исключает бесконечные циклы

## ⚠️ Важные замечания

- Всегда используйте разумные задержки между запросами (`delay` параметр)
- Ограничивайте глубину рекурсии для больших сайтов
- Соблюдайте `robots.txt` и условия использования сайтов
- Используйте `same_domain_only=True` для предотвращения ухода на внешние сайты
- Тестируйте на небольших сайтах перед масштабным скрапингом

## 📁 Затронутые файлы

- `getscrapper/core/session.py` - исправлен User-Agent
- `getscrapper/core/scraper.py` - добавлен рекурсивный скрапинг
- `getscrapper/parsers/html_parser.py` - исправлена обработка ссылок
- `getscrapper/storage/csv_storage.py` - проверена кодировка UTF-8
- `getscrapper/storage/json_storage.py` - проверена кодировка UTF-8