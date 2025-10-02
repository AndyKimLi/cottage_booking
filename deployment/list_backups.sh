#!/bin/bash

# Скрипт для просмотра доступных бэкапов
# Использование: ./list_backups.sh

BACKUP_DIR="./backups"

echo "📁 Доступные резервные копии:"
echo "================================"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Папка бэкапов не найдена: $BACKUP_DIR"
    exit 1
fi

# Подсчитываем общее количество бэкапов
TOTAL_BACKUPS=$(ls "$BACKUP_DIR"/*.sql* 2>/dev/null | wc -l)

if [ $TOTAL_BACKUPS -eq 0 ]; then
    echo "❌ Бэкапы не найдены"
    exit 1
fi

echo "📊 Всего бэкапов: $TOTAL_BACKUPS"
echo ""

# Показываем бэкапы с информацией о размере и дате
ls -lah "$BACKUP_DIR"/*.sql* 2>/dev/null | while read line; do
    # Извлекаем имя файла
    FILENAME=$(echo "$line" | awk '{print $NF}' | sed 's/.*\///')
    
    # Извлекаем размер
    SIZE=$(echo "$line" | awk '{print $5}')
    
    # Извлекаем дату
    DATE=$(echo "$line" | awk '{print $6, $7, $8}')
    
    # Определяем тип файла
    if [[ "$FILENAME" == *.gz ]]; then
        TYPE="📦 Сжатый"
    else
        TYPE="📄 Обычный"
    fi
    
    echo "$TYPE | $SIZE | $DATE | $FILENAME"
done

echo ""
echo "💡 Для восстановления используйте:"
echo "   ./restore_db.sh backup_YYYYMMDD_HHMMSS.sql.gz"

