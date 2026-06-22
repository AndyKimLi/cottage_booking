#!/bin/bash

# Скрипт для обновления проекта на сервере после git push

set -e  # Остановка при ошибке

echo "🚀 Начало обновления проекта..."

# Переход в директорию проекта (измените путь если нужно)
cd /path/to/cottage || cd ~/cottage || cd /app/cottage || {
    echo "❌ Не удалось найти директорию проекта!"
    echo "Укажите правильный путь в скрипте"
    exit 1
}

echo "📥 Получение изменений из GitHub..."
git pull origin main || git pull origin master

echo "🔨 Пересборка Docker контейнеров..."
docker compose build web

echo "🔄 Перезапуск сервисов..."
docker compose up -d

echo "📦 Компиляция переводов..."
docker compose exec web python manage.py compilemessages

echo "📊 Проверка статуса сервисов..."
docker compose ps

echo "✅ Обновление завершено!"
echo "📝 Проверьте логи если что-то пошло не так:"
echo "   docker compose logs -f web"

