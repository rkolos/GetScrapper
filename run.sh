#!/bin/bash

# Скрипт для быстрого запуска универсального рендерера

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка зависимостей
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        error "pip is not installed"
        exit 1
    fi
    
    success "Dependencies check passed"
}

# Установка зависимостей
install_dependencies() {
    log "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install --break-system-packages -r requirements.txt
        success "Python dependencies installed"
    else
        error "requirements.txt not found"
        exit 1
    fi
    
    log "Installing Playwright browsers..."
    python3 -m playwright install chromium
    success "Playwright browsers installed"
}

# Проверка конфигурации
check_config() {
    log "Checking configuration..."
    
    if [ -z "$BROWSERBASE_API_KEY" ] && [ -z "$BROWSERBASE_PROJECT_ID" ]; then
        warning "Browserbase credentials not set. Fallback will not be available."
        warning "Set BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID for full functionality."
    else
        success "Browserbase credentials found"
    fi
}

# Запуск тестов
run_tests() {
    log "Running system tests..."
    
    if python3 test_system.py; then
        success "All tests passed!"
    else
        error "Tests failed!"
        exit 1
    fi
}

# Запуск примеров
run_examples() {
    log "Running usage examples..."
    
    if python3 example_usage.py; then
        success "Examples completed successfully!"
    else
        error "Examples failed!"
        exit 1
    fi
}

# Основное меню
show_menu() {
    echo
    echo "Universal HTML Renderer - Quick Start"
    echo "====================================="
    echo "1. Install dependencies"
    echo "2. Run system tests"
    echo "3. Run usage examples"
    echo "4. Test single URL"
    echo "5. Batch process URLs"
    echo "6. Show help"
    echo "7. Exit"
    echo
}

# Тест одного URL
test_single_url() {
    echo
    read -p "Enter URL to test: " url
    
    if [ -z "$url" ]; then
        error "URL cannot be empty"
        return
    fi
    
    log "Testing URL: $url"
    python3 cli.py "$url" --analysis
}

# Пакетная обработка
batch_process() {
    echo
    read -p "Enter file with URLs (one per line): " url_file
    
    if [ ! -f "$url_file" ]; then
        error "File not found: $url_file"
        return
    fi
    
    read -p "Enter output directory (default: output): " output_dir
    output_dir=${output_dir:-output}
    
    log "Batch processing URLs from: $url_file"
    log "Output directory: $output_dir"
    
    python3 cli.py --batch "$url_file" --output-dir "$output_dir"
}

# Показать помощь
show_help() {
    echo
    echo "Universal HTML Renderer Help"
    echo "============================"
    echo
    echo "Basic usage:"
    echo "  python3 cli.py <URL>"
    echo
    echo "With analysis:"
    echo "  python3 cli.py <URL> --analysis"
    echo
    echo "Save to file:"
    echo "  python3 cli.py <URL> --output page.html"
    echo
    echo "Batch processing:"
    echo "  python3 cli.py --batch urls.txt --output-dir results/"
    echo
    echo "With Browserbase:"
    echo "  export BROWSERBASE_API_KEY='your_key'"
    echo "  export BROWSERBASE_PROJECT_ID='your_project'"
    echo "  python3 cli.py <URL>"
    echo
    echo "Environment variables:"
    echo "  BROWSERBASE_API_KEY     - Browserbase API key"
    echo "  BROWSERBASE_PROJECT_ID  - Browserbase project ID"
    echo "  RENDERER_LOG_LEVEL      - Log level (DEBUG, INFO, WARNING, ERROR)"
    echo "  RENDERER_HEADLESS       - Headless mode (true/false)"
    echo "  RENDERER_TIMEOUT        - Timeout in milliseconds"
    echo
}

# Главная функция
main() {
    echo "Universal HTML Renderer"
    echo "======================"
    
    check_dependencies
    check_config
    
    while true; do
        show_menu
        read -p "Select option (1-7): " choice
        
        case $choice in
            1)
                install_dependencies
                ;;
            2)
                run_tests
                ;;
            3)
                run_examples
                ;;
            4)
                test_single_url
                ;;
            5)
                batch_process
                ;;
            6)
                show_help
                ;;
            7)
                success "Goodbye!"
                exit 0
                ;;
            *)
                error "Invalid option. Please select 1-7."
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
    done
}

# Обработка аргументов командной строки
if [ $# -eq 0 ]; then
    main
else
    case $1 in
        --install)
            check_dependencies
            install_dependencies
            ;;
        --test)
            run_tests
            ;;
        --examples)
            run_examples
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Usage: $0 [--install|--test|--examples|--help]"
            echo "Run without arguments for interactive menu"
            exit 1
            ;;
    esac
fi