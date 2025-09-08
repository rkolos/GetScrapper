#!/bin/bash

# Скрипт для быстрого запуска Universal HTML Renderer API

set -e

echo "Universal HTML Renderer API - Quick Start"
echo "========================================"

# Проверяем, установлен ли Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker для запуска API сервера."
    exit 1
fi

# Проверяем, установлен ли Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose для запуска API сервера."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создаем необходимые директории
mkdir -p output logs

echo "📁 Созданы директории: output/, logs/"

# Собираем Docker образ
echo "🔨 Сборка Docker образа..."
docker-compose build api-server

# Запускаем API сервер
echo "🚀 Запуск API сервера..."
docker-compose up -d api-server

# Ждем запуска сервера
echo "⏳ Ожидание запуска сервера..."
sleep 10

# Проверяем состояние
echo "🔍 Проверка состояния API..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API сервер успешно запущен!"
    echo ""
    echo "🌐 API доступен по адресу: http://localhost:8000"
    echo "📚 Документация: http://localhost:8000/docs"
    echo "🔧 ReDoc: http://localhost:8000/redoc"
    echo ""
    echo "📋 Полезные команды:"
    echo "  make api-logs    - просмотр логов"
    echo "  make api-test    - тестирование API"
    echo "  make api-stop    - остановка сервера"
    echo "  make api-restart - перезапуск сервера"
    echo ""
    echo "🧪 Тестирование API..."
    python test_api.py
else
    echo "❌ API сервер не отвечает. Проверьте логи:"
    echo "   make api-logs"
    exit 1
fi