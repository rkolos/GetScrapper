# 🚀 Развертывание Universal HTML Renderer API

## Обзор

Ваш Python-скрипт успешно превращен в полноценный **API-сервис**! Теперь у вас есть:

- ✅ **FastAPI сервер** с REST API
- ✅ **Docker контейнеризация** 
- ✅ **Docker Compose** для оркестрации
- ✅ **Автоматическая документация** (Swagger/ReDoc)
- ✅ **Health checks** и мониторинг
- ✅ **Пакетная обработка** URL
- ✅ **Интеллектуальная эскалация** (Local → Browserbase)

## 📁 Структура проекта

```
/workspace/
├── api_server.py          # 🎯 Основной FastAPI сервер
├── test_api.py            # 🧪 Тесты API
├── api_examples.py        # 📚 Примеры использования
├── docker-compose.yml     # 🐳 Docker Compose конфигурация
├── Dockerfile             # 🐳 Docker образ
├── requirements.txt       # 📦 Python зависимости
├── start_api.sh           # 🚀 Скрипт быстрого запуска
├── Makefile               # ⚙️ Команды управления
├── README_API.md          # 📖 Документация API
└── DEPLOYMENT.md          # 🚀 Этот файл
```

## 🚀 Быстрый запуск

### 1. Автоматический запуск (рекомендуется)

```bash
# Клонируйте проект и перейдите в директорию
cd /workspace

# Запустите автоматический скрипт
./start_api.sh
```

### 2. Ручной запуск через Docker Compose

```bash
# Сборка и запуск
docker-compose up -d api-server

# Проверка состояния
curl http://localhost:8000/health

# Просмотр логов
docker-compose logs -f api-server
```

### 3. Локальный запуск (для разработки)

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск API сервера
python api_server.py
```

## 🌐 Доступ к API

После запуска API будет доступен по адресу: **http://localhost:8000**

### Основные эндпоинты:

- **`GET /`** - Информация об API
- **`GET /health`** - Проверка состояния
- **`POST /scrape`** - Рендеринг одного URL
- **`POST /scrape/batch`** - Пакетный рендеринг
- **`GET /stats`** - Статистика рендерера

### Документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Тестирование

### Автоматические тесты

```bash
# Полное тестирование API
make api-test

# Или напрямую
python test_api.py
```

### Ручное тестирование

```bash
# Health check
curl http://localhost:8000/health

# Рендеринг URL
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}'

# Пакетный рендеринг
curl -X POST "http://localhost:8000/scrape/batch" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://httpbin.org/html"]}'
```

## ⚙️ Конфигурация

### Переменные окружения

```bash
# Настройки рендерера
RENDERER_LOG_LEVEL=INFO          # Уровень логирования
RENDERER_HEADLESS=true           # Headless режим браузера
RENDERER_TIMEOUT=30000           # Таймаут в миллисекундах

# Browserbase credentials (опционально)
BROWSERBASE_API_KEY=your_key     # API ключ Browserbase
BROWSERBASE_PROJECT_ID=your_id   # ID проекта Browserbase
```

### Настройка в docker-compose.yml

```yaml
environment:
  - RENDERER_LOG_LEVEL=INFO
  - RENDERER_HEADLESS=true
  - RENDERER_TIMEOUT=30000
  # Раскомментируйте для Browserbase
  # - BROWSERBASE_API_KEY=your_api_key_here
  # - BROWSERBASE_PROJECT_ID=your_project_id_here
```

## 🐳 Docker команды

### Основные команды

```bash
# Запуск API сервера
make api-start

# Остановка
make api-stop

# Перезапуск
make api-restart

# Просмотр логов
make api-logs

# Сборка образа
make docker-build

# Очистка
make docker-clean
```

### Прямые Docker команды

```bash
# Сборка образа
docker-compose build api-server

# Запуск в фоне
docker-compose up -d api-server

# Просмотр логов
docker-compose logs -f api-server

# Остановка
docker-compose down

# Перезапуск
docker-compose restart api-server
```

## 📊 Мониторинг

### Health Check

```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**
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
docker-compose logs -f api-server

# Или через Makefile
make api-logs
```

## 🔧 Архитектура

### Двухуровневая система рендеринга

1. **Уровень 2 (Baseline)**: Локальный Playwright браузер
   - Быстрый рендеринг простых страниц
   - Низкая стоимость
   - Высокая доступность

2. **Уровень 3 (Fallback)**: Browserbase
   - Обход сложных блокировок
   - Высокая надежность
   - Платный сервис

### Интеллектуальная эскалация

- Автоматическое обнаружение блокировок
- Анализ контента на предмет блокировщиков
- Переключение на Browserbase при необходимости
- Детальный анализ причин блокировки

## 🚀 Продакшен развертывание

### 1. Безопасность

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
    # Ограничения ресурсов
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 2. Масштабирование

```yaml
# Множественные инстансы
deploy:
  replicas: 3
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
```

### 3. Load Balancer (nginx)

```nginx
upstream api_backend {
    server api-server-1:8000;
    server api-server-2:8000;
    server api-server-3:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Мониторинг (Prometheus/Grafana)

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🔍 Troubleshooting

### Проблемы с запуском

1. **API не отвечает**:
   ```bash
   # Проверьте логи
   docker-compose logs api-server
   
   # Проверьте статус контейнера
   docker-compose ps
   ```

2. **Ошибки рендеринга**:
   ```bash
   # Проверьте health check
   curl http://localhost:8000/health
   
   # Проверьте статистику
   curl http://localhost:8000/stats
   ```

3. **Проблемы с Browserbase**:
   ```bash
   # Проверьте credentials
   echo $BROWSERBASE_API_KEY
   echo $BROWSERBASE_PROJECT_ID
   ```

### Логи и отладка

```bash
# Подробные логи
docker-compose logs -f api-server

# Логи с временными метками
docker-compose logs -f -t api-server

# Логи за последние 100 строк
docker-compose logs --tail=100 api-server
```

## 📚 Дополнительные ресурсы

- [README_API.md](README_API.md) - Подробная документация API
- [api_examples.py](api_examples.py) - Примеры использования
- [test_api.py](test_api.py) - Тесты API
- [Makefile](Makefile) - Команды управления

## 🎉 Готово!

Ваш Python-скрипт теперь работает как полноценный API-сервис!

**Следующие шаги:**
1. ✅ Запустите API: `./start_api.sh`
2. ✅ Откройте документацию: http://localhost:8000/docs
3. ✅ Протестируйте API: `make api-test`
4. ✅ Интегрируйте в ваше приложение

**Для продакшена:**
1. 🔒 Настройте аутентификацию
2. 📊 Добавьте мониторинг
3. ⚖️ Настройте масштабирование
4. 🔐 Используйте HTTPS

---

**🎯 Ваш "движок" теперь функционально завершен и готов к продакшену!**