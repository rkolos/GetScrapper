"""
FastAPI сервер для универсального рендерера
Предоставляет REST API для рендеринга веб-страниц
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
import uvicorn
from main_controller import UniversalRenderer, get_universal_html
from config import config, validate_config

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Universal HTML Renderer API",
    description="API для универсального рендеринга веб-страниц с интеллектуальной эскалацией",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить конкретными доменами
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный экземпляр рендерера
renderer: Optional[UniversalRenderer] = None


# Pydantic модели для запросов и ответов
class ScrapeRequest(BaseModel):
    """Модель запроса на рендеринг"""
    url: HttpUrl = Field(..., description="URL для рендеринга")
    browserbase_api_key: Optional[str] = Field(None, description="API ключ Browserbase (опционально)")
    browserbase_project_id: Optional[str] = Field(None, description="ID проекта Browserbase (опционально)")
    local_timeout: Optional[int] = Field(None, ge=1000, le=120000, description="Таймаут для локального браузера в миллисекундах")
    local_headless: Optional[bool] = Field(None, description="Запускать локальный браузер в headless режиме")
    reuse_context: Optional[bool] = Field(None, description="Переиспользовать контекст браузера")


class ScrapeResponse(BaseModel):
    """Модель ответа с результатами рендеринга"""
    success: bool = Field(..., description="Успешность операции")
    url: str = Field(..., description="Исходный URL")
    final_url: str = Field(..., description="Финальный URL после редиректов")
    page_title: str = Field(..., description="Заголовок страницы")
    status_code: int = Field(..., description="HTTP статус код")
    content_length: int = Field(..., description="Длина HTML контента в байтах")
    render_time: float = Field(..., description="Время рендеринга в секундах")
    source: str = Field(..., description="Источник рендеринга (local/browserbase)")
    escalation_reason: Optional[str] = Field(None, description="Причина эскалации")
    html_content: str = Field(..., description="Рендеренный HTML контент")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")
    detection_analysis: Optional[Dict[str, Any]] = Field(None, description="Анализ детекции блокировок")


class HealthResponse(BaseModel):
    """Модель ответа для health check"""
    status: str = Field(..., description="Статус сервиса")
    version: str = Field(..., description="Версия API")
    browserbase_available: bool = Field(..., description="Доступность Browserbase")
    detection_rules_count: Dict[str, int] = Field(..., description="Количество правил детекции")


class BatchScrapeRequest(BaseModel):
    """Модель запроса для пакетного рендеринга"""
    urls: list[HttpUrl] = Field(..., min_items=1, max_items=50, description="Список URL для рендеринга (максимум 50)")
    browserbase_api_key: Optional[str] = Field(None, description="API ключ Browserbase")
    browserbase_project_id: Optional[str] = Field(None, description="ID проекта Browserbase")


class BatchScrapeResponse(BaseModel):
    """Модель ответа для пакетного рендеринга"""
    success: bool = Field(..., description="Успешность операции")
    total_urls: int = Field(..., description="Общее количество URL")
    successful: int = Field(..., description="Количество успешно обработанных URL")
    failed: int = Field(..., description="Количество неудачных URL")
    results: list[ScrapeResponse] = Field(..., description="Результаты рендеринга")


# Инициализация приложения
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    global renderer
    
    logger.info("Starting Universal HTML Renderer API Server")
    
    # Валидация конфигурации
    if not validate_config(config):
        logger.error("Invalid configuration")
        raise RuntimeError("Invalid configuration")
    
    # Создание глобального экземпляра рендерера
    renderer = UniversalRenderer()
    logger.info("Universal renderer initialized")
    logger.info(f"Browserbase available: {renderer.browserbase_available}")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении приложения"""
    logger.info("Shutting down Universal HTML Renderer API Server")


# Эндпоинты API
@app.get("/", response_model=Dict[str, str])
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Universal HTML Renderer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния сервиса"""
    if not renderer:
        raise HTTPException(status_code=503, detail="Renderer not initialized")
    
    stats = renderer.get_stats()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        browserbase_available=stats["browserbase_available"],
        detection_rules_count=stats["detection_rules_count"]
    )


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest):
    """
    Рендеринг одного URL
    
    Принимает URL и возвращает рендеренный HTML с метаданными.
    Использует интеллектуальную эскалацию: сначала локальный браузер,
    затем Browserbase при обнаружении блокировок.
    """
    if not renderer:
        raise HTTPException(status_code=503, detail="Renderer not initialized")
    
    try:
        logger.info(f"Scraping URL: {request.url}")
        
        # Создаем временный рендерер с пользовательскими настройками
        temp_renderer = UniversalRenderer(
            browserbase_api_key=request.browserbase_api_key,
            browserbase_project_id=request.browserbase_project_id,
            local_timeout=request.local_timeout,
            local_headless=request.local_headless,
            reuse_context=request.reuse_context
        )
        
        # Выполняем рендеринг
        result = await temp_renderer.get_universal_html(str(request.url))
        
        # Проверяем на ошибки
        if result.get('error'):
            logger.error(f"Scraping failed for {request.url}: {result['error']}")
            raise HTTPException(
                status_code=500, 
                detail=f"Scraping failed: {result['error']}"
            )
        
        # Формируем ответ
        response = ScrapeResponse(
            success=True,
            url=str(request.url),
            final_url=result.get('final_url', str(request.url)),
            page_title=result.get('page_title', ''),
            status_code=result.get('status_code', 0),
            content_length=result.get('content_length', 0),
            render_time=result.get('render_time', 0),
            source=result.get('source', 'unknown'),
            escalation_reason=result.get('escalation_reason'),
            html_content=result.get('html_content', ''),
            error=result.get('error'),
            detection_analysis=result.get('detection_analysis')
        )
        
        logger.info(f"Successfully scraped {request.url} via {result.get('source')} in {result.get('render_time', 0):.2f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error scraping {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/scrape/batch", response_model=BatchScrapeResponse)
async def scrape_batch(request: BatchScrapeRequest, background_tasks: BackgroundTasks):
    """
    Пакетный рендеринг множества URL
    
    Принимает список URL и возвращает результаты рендеринга для каждого.
    Обрабатывает до 50 URL за один запрос.
    """
    if not renderer:
        raise HTTPException(status_code=503, detail="Renderer not initialized")
    
    if len(request.urls) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 URLs allowed per batch")
    
    logger.info(f"Batch scraping {len(request.urls)} URLs")
    
    try:
        # Создаем временный рендерер
        temp_renderer = UniversalRenderer(
            browserbase_api_key=request.browserbase_api_key,
            browserbase_project_id=request.browserbase_project_id
        )
        
        results = []
        successful = 0
        failed = 0
        
        # Обрабатываем каждый URL
        for url in request.urls:
            try:
                result = await temp_renderer.get_universal_html(str(url))
                
                response = ScrapeResponse(
                    success=not bool(result.get('error')),
                    url=str(url),
                    final_url=result.get('final_url', str(url)),
                    page_title=result.get('page_title', ''),
                    status_code=result.get('status_code', 0),
                    content_length=result.get('content_length', 0),
                    render_time=result.get('render_time', 0),
                    source=result.get('source', 'unknown'),
                    escalation_reason=result.get('escalation_reason'),
                    html_content=result.get('html_content', ''),
                    error=result.get('error'),
                    detection_analysis=result.get('detection_analysis')
                )
                
                results.append(response)
                
                if response.success:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                error_response = ScrapeResponse(
                    success=False,
                    url=str(url),
                    final_url=str(url),
                    page_title='',
                    status_code=0,
                    content_length=0,
                    render_time=0,
                    source='error',
                    escalation_reason=None,
                    html_content='',
                    error=str(e),
                    detection_analysis=None
                )
                results.append(error_response)
                failed += 1
        
        logger.info(f"Batch scraping completed: {successful} successful, {failed} failed")
        
        return BatchScrapeResponse(
            success=failed == 0,
            total_urls=len(request.urls),
            successful=successful,
            failed=failed,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Batch scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@app.get("/stats", response_model=Dict[str, Any])
async def get_stats():
    """Получение статистики рендерера"""
    if not renderer:
        raise HTTPException(status_code=503, detail="Renderer not initialized")
    
    return renderer.get_stats()


# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )