# Universal HTML Renderer API

REST API для универсального рендеринга веб-страниц с интеллектуальной эскалацией.

## Архитектура

API использует двухуровневую архитектуру рендеринга:

1. **Уровень 2 (Baseline)**: Локальный Playwright браузер
2. **Уровень 3 (Fallback)**: Browserbase при обнаружении блокировок

## Быстрый старт

### Запуск API сервера

```bash
# Запуск через Docker Compose
docker-compose up api-server

# Или локально
pip install -r requirements.txt
python api_server.py
```

API будет доступен по адресу: `http://localhost:8000`

### Документация API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Эндпоинты

### 1. Проверка состояния

```http
GET /health
```

**Ответ:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "browserbase_available": true,
  "detection_rules_count": {
    "title_keywords": 15,
    "url_patterns": 8,
    "html_selectors": 12,
    "content_phrases": 20
  }
}
```

### 2. Рендеринг одного URL

```http
POST /scrape
Content-Type: application/json

{
  "url": "https://example.com",
  "browserbase_api_key": "optional",
  "browserbase_project_id": "optional",
  "local_timeout": 30000,
  "local_headless": true,
  "reuse_context": false
}
```

**Ответ:**
```json
{
  "success": true,
  "url": "https://example.com",
  "final_url": "https://example.com",
  "page_title": "Example Domain",
  "status_code": 200,
  "content_length": 1256,
  "render_time": 2.34,
  "source": "local",
  "escalation_reason": null,
  "html_content": "<!DOCTYPE html>...",
  "error": null,
  "detection_analysis": {
    "confidence_score": 0.95,
    "is_blocked": false,
    "blocking_reasons": [],
    "rule_results": {...}
  }
}
```

### 3. Пакетный рендеринг

```http
POST /scrape/batch
Content-Type: application/json

{
  "urls": [
    "https://example.com",
    "https://httpbin.org/html"
  ],
  "browserbase_api_key": "optional",
  "browserbase_project_id": "optional"
}
```

**Ответ:**
```json
{
  "success": true,
  "total_urls": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "success": true,
      "url": "https://example.com",
      "final_url": "https://example.com",
      "page_title": "Example Domain",
      "status_code": 200,
      "content_length": 1256,
      "render_time": 2.34,
      "source": "local",
      "escalation_reason": null,
      "html_content": "<!DOCTYPE html>...",
      "error": null,
      "detection_analysis": {...}
    }
  ]
}
```

### 4. Статистика

```http
GET /stats
```

**Ответ:**
```json
{
  "browserbase_available": true,
  "local_timeout": 30000,
  "local_headless": true,
  "detection_rules_count": {
    "title_keywords": 15,
    "url_patterns": 8,
    "html_selectors": 12,
    "content_phrases": 20
  }
}
```

## Примеры использования

### Python клиент

```python
import asyncio
import aiohttp

async def scrape_url():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/scrape",
            json={"url": "https://example.com"}
        ) as response:
            result = await response.json()
            print(f"Title: {result['page_title']}")
            print(f"Content Length: {result['content_length']}")

asyncio.run(scrape_url())
```

### cURL

```bash
# Рендеринг одного URL
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Пакетный рендеринг
curl -X POST "http://localhost:8000/scrape/batch" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://httpbin.org/html"]}'

# Проверка состояния
curl "http://localhost:8000/health"
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function scrapeUrl() {
  try {
    const response = await axios.post('http://localhost:8000/scrape', {
      url: 'https://example.com'
    });
    
    console.log('Title:', response.data.page_title);
    console.log('Content Length:', response.data.content_length);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

scrapeUrl();
```

## Конфигурация

### Переменные окружения

```bash
# Настройки рендерера
RENDERER_LOG_LEVEL=INFO
RENDERER_HEADLESS=true
RENDERER_TIMEOUT=30000

# Browserbase credentials
BROWSERBASE_API_KEY=your_api_key_here
BROWSERBASE_PROJECT_ID=your_project_id_here
```

### Docker Compose

```yaml
version: '3.8'
services:
  api-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - RENDERER_LOG_LEVEL=INFO
      - RENDERER_HEADLESS=true
      - RENDERER_TIMEOUT=30000
      # - BROWSERBASE_API_KEY=your_api_key_here
      # - BROWSERBASE_PROJECT_ID=your_project_id_here
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    restart: unless-stopped
    command: ["python3", "api_server.py"]
```

## Мониторинг

### Health Check

```bash
curl http://localhost:8000/health
```

### Логи

```bash
# Просмотр логов контейнера
docker-compose logs -f api-server

# Логи в файле
tail -f logs/api.log
```

### Метрики

API предоставляет следующие метрики:

- Время рендеринга
- Источник рендеринга (local/browserbase)
- Причины эскалации
- Статистика детекции блокировок

## Обработка ошибок

### Коды ошибок

- `200` - Успешный рендеринг
- `400` - Неверный запрос (некорректный URL, превышение лимитов)
- `500` - Ошибка рендеринга
- `503` - Сервис недоступен

### Примеры ошибок

```json
{
  "detail": "Scraping failed: Connection timeout"
}
```

```json
{
  "detail": "Maximum 50 URLs allowed per batch"
}
```

## Производительность

### Рекомендации

1. **Пакетная обработка**: Используйте `/scrape/batch` для множественных URL
2. **Переиспользование контекста**: Включите `reuse_context: true` для повышения производительности
3. **Таймауты**: Настройте подходящие таймауты для ваших URL
4. **Мониторинг**: Отслеживайте метрики через `/stats` и `/health`

### Ограничения

- Максимум 50 URL в пакетном запросе
- Таймаут по умолчанию: 30 секунд
- Максимальный размер ответа: ограничен настройками сервера

## Безопасность

### CORS

По умолчанию CORS настроен для всех доменов. В продакшене ограничьте:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Аутентификация

Для продакшена добавьте аутентификацию:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    if not verify_api_key(token.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return token

@app.post("/scrape")
async def scrape_url(request: ScrapeRequest, token = Depends(verify_token)):
    # ...
```

## Разработка

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск в режиме разработки
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Тестирование

```bash
# Запуск примеров
python api_examples.py

# Тестирование API
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}'
```

### Логирование

Логи записываются в:
- Консоль (stdout)
- Файл `logs/api.log` (если настроено)

Уровни логирования:
- `DEBUG` - Детальная отладочная информация
- `INFO` - Общая информация о работе
- `WARNING` - Предупреждения
- `ERROR` - Ошибки