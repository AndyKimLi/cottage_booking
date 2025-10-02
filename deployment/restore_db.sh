#!/bin/bash

# Скрипт для восстановления базы данных из бэкапа
# Использование: ./restore_db.sh backup_file.sql

if [ $# -eq 0 ]; then
    echo "❌ Ошибка: Укажите файл бэкапа"
    echo "Использование: ./restore_db.sh backup_file.sql"
    echo ""
    echo "Доступные бэкапы:"
    ls -la backups/*.sql 2>/dev/null || echo "Бэкапы не найдены"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "backups/$BACKUP_FILE" ]; then
    echo "❌ Файл бэкапа не найден: backups/$BACKUP_FILE"
    exit 1
fi

echo "🔄 Восстановление базы данных из файла: $BACKUP_FILE"
echo "⚠️  ВНИМАНИЕ: Это удалит все текущие данные!"

read -p "Продолжить? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Отменено"
    exit 1
fi

# Останавливаем приложение
echo "🛑 Остановка приложения..."
docker-compose stop web celery telegram_bot

# Удаляем текущую базу данных
echo "🗑️  Удаление текущей базы данных..."
docker-compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS cottage_booking;"
docker-compose exec -T db psql -U postgres -c "CREATE DATABASE cottage_booking;"

# Восстанавливаем из бэкапа
echo "📥 Восстановление из бэкапа..."

# Проверяем, сжат ли файл
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "📦 Распаковка сжатого файла..."
    gunzip -c "backups/$BACKUP_FILE" | docker-compose exec -T db psql -U postgres -d cottage_booking
else
    docker-compose exec -T db psql -U postgres -d cottage_booking < "backups/$BACKUP_FILE"
fi

# Запускаем приложение
echo "🚀 Запуск приложения..."
docker-compose up -d

echo "✅ База данных успешно восстановлена!"
echo "🌐 Приложение доступно по адресу: http://localhost:8000"
