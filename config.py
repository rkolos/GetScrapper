"""
Конфигурация для универсального рендерера
"""

import os
from typing import Dict, Any

# Настройки по умолчанию
DEFAULT_CONFIG = {
    # Локальный браузер (Уровень 2)
    'local_browser': {
        'headless': True,
        'timeout': 30000,  # 30 секунд
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'viewport': {'width': 1920, 'height': 1080},
        'block_resources': ['image', 'font', 'media'],  # Блокируемые типы ресурсов
        'wait_after_load': 2,  # Секунды ожидания после загрузки
    },
    
    # Детекция блокировок
    'detection': {
        'confidence_threshold': 0.3,  # Порог для срабатывания блокировки
        'enable_title_check': True,
        'enable_url_check': True,
        'enable_html_check': True,
        'enable_content_check': True,
        'enable_empty_page_check': True,
    },
    
    # Browserbase (Уровень 3)
    'browserbase': {
        'timeout': 30000,
        'headless': True,
        'wait_after_load': 3,
    },
    
    # Логирование
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'enable_detailed_logs': True,
    }
}

# Переменные окружения
ENV_VARS = {
    'BROWSERBASE_API_KEY': os.getenv('BROWSERBASE_API_KEY'),
    'BROWSERBASE_PROJECT_ID': os.getenv('BROWSERBASE_PROJECT_ID'),
    'RENDERER_LOG_LEVEL': os.getenv('RENDERER_LOG_LEVEL', 'INFO'),
    'RENDERER_HEADLESS': os.getenv('RENDERER_HEADLESS', 'true').lower() == 'true',
    'RENDERER_TIMEOUT': int(os.getenv('RENDERER_TIMEOUT', '30000')),
}


def get_config() -> Dict[str, Any]:
    """Получает конфигурацию с учетом переменных окружения"""
    config = DEFAULT_CONFIG.copy()
    
    # Обновляем настройки из переменных окружения
    if ENV_VARS['RENDERER_LOG_LEVEL']:
        config['logging']['level'] = ENV_VARS['RENDERER_LOG_LEVEL']
    
    if ENV_VARS['RENDERER_HEADLESS'] is not None:
        config['local_browser']['headless'] = ENV_VARS['RENDERER_HEADLESS']
    
    if ENV_VARS['RENDERER_TIMEOUT']:
        config['local_browser']['timeout'] = ENV_VARS['RENDERER_TIMEOUT']
    
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """Валидирует конфигурацию"""
    try:
        # Проверяем обязательные настройки
        assert config['local_browser']['timeout'] > 0
        assert config['detection']['confidence_threshold'] >= 0.0
        assert config['detection']['confidence_threshold'] <= 1.0
        
        # Проверяем Browserbase настройки если они есть
        if ENV_VARS['BROWSERBASE_API_KEY'] and ENV_VARS['BROWSERBASE_PROJECT_ID']:
            assert config['browserbase']['timeout'] > 0
        
        return True
    except (AssertionError, KeyError, TypeError):
        return False


# Экспорт конфигурации
config = get_config()