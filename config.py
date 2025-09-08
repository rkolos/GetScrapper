"""
Конфигурация универсального рендерера через переменные окружения
"""

import os
from typing import Optional


class Config:
    """Класс для управления конфигурацией через переменные окружения"""
    
    # Browserbase настройки
    BROWSERBASE_API_KEY: Optional[str] = os.getenv('BROWSERBASE_API_KEY')
    BROWSERBASE_PROJECT_ID: Optional[str] = os.getenv('BROWSERBASE_PROJECT_ID')
    BROWSERBASE_URL: str = os.getenv('BROWSERBASE_URL', 'https://api.browserbase.com')
    
    # Playwright настройки
    PLAYWRIGHT_SERVER_URL: Optional[str] = os.getenv('PLAYWRIGHT_SERVER_URL')
    PLAYWRIGHT_HEADLESS: bool = os.getenv('PLAYWRIGHT_HEADLESS', 'true').lower() == 'true'
    PLAYWRIGHT_TIMEOUT: int = int(os.getenv('PLAYWRIGHT_TIMEOUT', '30000'))
    PLAYWRIGHT_REUSE_CONTEXT: bool = os.getenv('PLAYWRIGHT_REUSE_CONTEXT', 'false').lower() == 'true'
    
    # Детекция блокировок
    DETECTION_CONFIDENCE_THRESHOLD: float = float(os.getenv('DETECTION_CONFIDENCE_THRESHOLD', '0.3'))
    DETECTION_ENABLE_HTML_ANALYSIS: bool = os.getenv('DETECTION_ENABLE_HTML_ANALYSIS', 'true').lower() == 'true'
    
    # Логирование
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
    
    # Производительность
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    @classmethod
    def validate_browserbase_config(cls) -> bool:
        """Проверяет наличие необходимых настроек Browserbase"""
        return bool(cls.BROWSERBASE_API_KEY and cls.BROWSERBASE_PROJECT_ID)
    
    @classmethod
    def get_browser_args(cls) -> list:
        """Возвращает аргументы для запуска браузера"""
        return [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
        ]
    
    @classmethod
    def get_user_agent(cls) -> str:
        """Возвращает User-Agent для запросов"""
        return os.getenv('USER_AGENT', 
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    @classmethod
    def get_http_headers(cls) -> dict:
        """Возвращает стандартные HTTP заголовки"""
        return {
            'User-Agent': cls.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    @classmethod
    def to_dict(cls) -> dict:
        """Возвращает конфигурацию в виде словаря (без секретных данных)"""
        return {
            'browserbase_available': cls.validate_browserbase_config(),
            'browserbase_url': cls.BROWSERBASE_URL,
            'playwright_headless': cls.PLAYWRIGHT_HEADLESS,
            'playwright_timeout': cls.PLAYWRIGHT_TIMEOUT,
            'playwright_reuse_context': cls.PLAYWRIGHT_REUSE_CONTEXT,
            'detection_confidence_threshold': cls.DETECTION_CONFIDENCE_THRESHOLD,
            'detection_enable_html_analysis': cls.DETECTION_ENABLE_HTML_ANALYSIS,
            'log_level': cls.LOG_LEVEL,
            'max_concurrent_requests': cls.MAX_CONCURRENT_REQUESTS,
            'request_timeout': cls.REQUEST_TIMEOUT,
        }


# Глобальный экземпляр конфигурации
config = Config()