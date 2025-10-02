#!/bin/bash

# Скрипт для локального тестирования без домена
# Использование: ./scripts/test_local.sh

echo "🧪 Локальное тестирование Cottage Booking System..."

# 1. Остановка всех контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose -f docker-compose.local.yml down

# 2. Сборка образов
echo "🔨 Сборка Docker образов..."
docker-compose -f docker-compose.local.yml build

# 3. Запуск сервисов
echo "🚀 Запуск сервисов..."
docker-compose -f docker-compose.local.yml up -d

# 4. Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 30

# 5. Применение миграций
echo "🗄️  Применение миграций..."
docker-compose -f docker-compose.local.yml exec web python manage.py migrate

# 6. Создание суперпользователя
echo "👤 Создание суперпользователя..."
docker-compose -f docker-compose.local.yml exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Суперпользователь создан: admin/admin123')
else:
    print('✅ Суперпользователь уже существует')
"

# 7. Сбор статических файлов
echo "📦 Сбор статических файлов..."
docker-compose -f docker-compose.local.yml exec web python manage.py collectstatic --noinput

# 8. Проверка статуса
echo "📊 Проверка статуса сервисов..."
docker-compose -f docker-compose.local.yml ps

echo ""
echo "🎉 Локальное тестирование готово!"
echo ""
echo "🌐 Доступные интерфейсы:"
echo "   • Приложение: http://localhost:8000"
echo "   • Админка: http://localhost:8000/admin (admin/admin123)"
echo "   • RabbitMQ: http://localhost:15672 (admin/password)"
echo ""
echo "📊 Проверка работы:"
echo "   • curl http://localhost:8000"
echo "   • curl http://localhost:8000/api/cottages/"
echo ""
echo "🛑 Для остановки:"
echo "   docker-compose -f docker-compose.local.yml down"
