# Universal HTML Renderer API

🚀 **Готовый к продакшену API-сервис** для универсального рендеринга веб-страниц с интеллектуальной эскалацией.

## 🎯 Что это?

Ваш Python-скрипт теперь превращен в полноценный **REST API-сервис**, который:

- ✅ Работает 24/7 как веб-сервис
- ✅ Принимает HTTP-запросы с URL для рендеринга
- ✅ Возвращает JSON с результатами
- ✅ Поддерживает пакетную обработку
- ✅ Имеет автоматическую документацию
- ✅ Включает health checks и мониторинг

## 🚀 Быстрый старт

### 1. Запуск через Docker (рекомендуется)

```bash
# Автоматический запуск
./start_api.sh

# Или вручную
make api-start
```

### 2. Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск API сервера
python api_server.py
```

### 3. Проверка работы

```bash
# Тестирование API
make api-test

# Или вручную
curl http://localhost:8000/health
```

## 📡 API Эндпоинты

### Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Информация об API |
| `GET` | `/health` | Проверка состояния |
| `POST` | `/scrape` | Рендеринг одного URL |
| `POST` | `/scrape/batch` | Пакетный рендеринг |
| `GET` | `/stats` | Статистика рендерера |

### Документация

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💡 Примеры использования

### 1. Рендеринг одного URL

```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
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
    "blocking_reasons": []
  }
}
```

### 2. Пакетный рендеринг

```bash
curl -X POST "http://localhost:8000/scrape/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com",
      "https://httpbin.org/html"
    ]
  }'
```

### 3. Python клиент

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
            print(f"Content: {result['html_content'][:100]}...")

asyncio.run(scrape_url())
```

## 🐳 Docker Compose

### Структура сервисов

```yaml
services:
  api-server:     # Основной API сервис (порт 8000)
  cli-service:    # CLI для пакетной обработки (профиль cli)
```

### Команды управления

```bash
# Запуск API сервера
make api-start

# Остановка
make api-stop

# Перезапуск
make api-restart

# Просмотр логов
make api-logs

# Тестирование
make api-test
```

## ⚙️ Конфигурация

### Переменные окружения

```bash
# Настройки рендерера
RENDERER_LOG_LEVEL=INFO
RENDERER_HEADLESS=true
RENDERER_TIMEOUT=30000

# Browserbase credentials (опционально)
BROWSERBASE_API_KEY=your_api_key_here
BROWSERBASE_PROJECT_ID=your_project_id_here
```

### Настройка в docker-compose.yml

```yaml
environment:
  - RENDERER_LOG_LEVEL=INFO
  - RENDERER_HEADLESS=true
  - RENDERER_TIMEOUT=30000
  # - BROWSERBASE_API_KEY=your_api_key_here
  # - BROWSERBASE_PROJECT_ID=your_project_id_here
```

## 🔧 Архитектура

### Двухуровневая система рендеринга

1. **Уровень 2 (Baseline)**: Локальный Playwright браузер
2. **Уровень 3 (Fallback)**: Browserbase при обнаружении блокировок

### Интеллектуальная эскалация

- Автоматическое обнаружение блокировок
- Переключение на Browserbase при необходимости
- Детальный анализ причин блокировки

## 📊 Мониторинг

### Health Check

```bash
curl http://localhost:8000/health
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

### Статистика

```bash
curl http://localhost:8000/stats
```

### Логи

```bash
# Docker логи
make api-logs

# Или напрямую
docker-compose logs -f api-server
```

## 🧪 Тестирование

### Автоматические тесты

```bash
# Полное тестирование API
make api-test

# Примеры использования
make api-examples
```

### Ручное тестирование

```bash
# Тест health check
curl http://localhost:8000/health

# Тест рендеринга
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}'
```

## 🚀 Продакшен

### Рекомендации для продакшена

1. **Безопасность**:
   - Настройте CORS для конкретных доменов
   - Добавьте аутентификацию (API ключи)
   - Используйте HTTPS

2. **Масштабирование**:
   - Настройте load balancer
   - Используйте несколько инстансов
   - Настройте мониторинг (Prometheus/Grafana)

3. **Надежность**:
   - Настройте автоматические перезапуски
   - Используйте health checks
   - Настройте логирование

### Пример продакшен конфигурации

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - RENDERER_LOG_LEVEL=WARNING
      - RENDERER_HEADLESS=true
      - RENDERER_TIMEOUT=30000
      - BROWSERBASE_API_KEY=${BROWSERBASE_API_KEY}
      - BROWSERBASE_PROJECT_ID=${BROWSERBASE_PROJECT_ID}
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 📚 Дополнительные ресурсы

- [API_README.md](API_README.md) - Подробная документация API
- [api_examples.py](api_examples.py) - Примеры использования
- [test_api.py](test_api.py) - Тесты API
- [Makefile](Makefile) - Команды управления

## 🎉 Готово!

Ваш Python-скрипт теперь работает как полноценный API-сервис! 

**Следующие шаги:**
1. Запустите API: `./start_api.sh`
2. Откройте документацию: http://localhost:8000/docs
3. Протестируйте API: `make api-test`
4. Интегрируйте в ваше приложение

**Для продакшена:**
1. Настройте аутентификацию
2. Добавьте мониторинг
3. Настройте масштабирование
4. Используйте HTTPS