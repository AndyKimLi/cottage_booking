#!/bin/bash

# Скрипт для восстановления базы данных из резервной копии
# Использование: ./restore.sh backup_file.sql.gz

if [ $# -eq 0 ]; then
    echo "❌ Укажите файл резервной копии!"
    echo "Использование: ./restore.sh backup_file.sql.gz"
    exit 1
fi

BACKUP_FILE=$1
DB_CONTAINER="cottage-db-1"
DB_NAME="cottage_booking"
DB_USER="postgres"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Файл $BACKUP_FILE не найден!"
    exit 1
fi

echo "🔄 Восстановление базы данных из $BACKUP_FILE..."

# Распаковываем если файл сжат
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "📦 Распаковка файла..."
    gunzip -c $BACKUP_FILE | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
else
    docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < $BACKUP_FILE
fi

if [ $? -eq 0 ]; then
    echo "✅ База данных успешно восстановлена!"
else
    echo "❌ Ошибка восстановления базы данных!"
    exit 1
fi
