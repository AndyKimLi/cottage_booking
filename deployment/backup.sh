#!/bin/bash

# Скрипт для создания резервных копий PostgreSQL
# Использование: ./backup.sh

# Настройки
DB_CONTAINER="cottage-db-1"
DB_NAME="cottage_booking"
DB_USER="postgres"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/cottage_booking_${DATE}.sql"

# Создаем директорию для бэкапов
mkdir -p $BACKUP_DIR

echo "🔄 Создание резервной копии базы данных..."

# Создаем дамп базы данных
docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Резервная копия создана: $BACKUP_FILE"
    
    # Сжимаем файл
    gzip $BACKUP_FILE
    echo "📦 Файл сжат: ${BACKUP_FILE}.gz"
    
    # Показываем размер файла
    echo "📊 Размер файла: $(du -h ${BACKUP_FILE}.gz | cut -f1)"
else
    echo "❌ Ошибка создания резервной копии!"
    exit 1
fi

echo "🎉 Резервная копия готова!"
