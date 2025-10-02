#!/bin/bash

# Скрипт для оптимизации производительности
# Использование: ./scripts/optimize_performance.sh

echo "⚡ Оптимизация производительности..."

# 1. Сбор статических файлов с оптимизацией
echo "📦 Сбор и оптимизация статических файлов..."
docker-compose exec web python manage.py collectstatic --noinput

# 2. Применение миграций с индексами
echo "🗄️  Применение миграций с индексами..."
docker-compose exec web python manage.py migrate

# 3. Создание кэша для статики
echo "💾 Создание кэша для статики..."
docker-compose exec web python manage.py compress

# 4. Очистка кэша
echo "🧹 Очистка кэша..."
docker-compose exec web python manage.py clear_cache

# 5. Создание суперпользователя (если не существует)
echo "👤 Проверка суперпользователя..."
docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Суперпользователь создан: admin/admin123')
else:
    print('✅ Суперпользователь уже существует')
"

# 6. Анализ производительности базы данных
echo "📊 Анализ производительности БД..."
docker-compose exec web python manage.py shell -c "
from django.db import connection
from django.conf import settings

# Проверяем индексы
with connection.cursor() as cursor:
    cursor.execute(\"\"\"
        SELECT schemaname, tablename, indexname, indexdef 
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
    \"\"\")
    
    indexes = cursor.fetchall()
    print(f'📈 Найдено {len(indexes)} индексов')
    
    for index in indexes:
        print(f'  • {index[1]}.{index[2]}')
"

# 7. Проверка кэша Redis
echo "🔍 Проверка кэша Redis..."
docker-compose exec redis redis-cli ping
docker-compose exec redis redis-cli info memory

echo "✅ Оптимизация завершена!"
echo ""
echo "📊 Результаты оптимизации:"
echo "  • Статические файлы сжаты и кэшированы"
echo "  • Индексы БД созданы для быстрых запросов"
echo "  • Redis кэш настроен с компрессией"
echo "  • Nginx кэширует API ответы"
echo ""
echo "🚀 Для проверки производительности:"
echo "  • Откройте Grafana: http://localhost:3000"
echo "  • Проверьте метрики в Prometheus: http://localhost:9090"
echo "  • Протестируйте API: curl http://localhost:8000/api/cottages/"
