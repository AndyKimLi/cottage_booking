#!/bin/bash

# Скрипт для принудительного перевода Redis в режим master
# Используется при проблемах с репликацией

set -e

echo "🔧 Проверка статуса Redis..."

# Проверяем роль Redis
ROLE=$(docker compose exec -T redis redis-cli INFO replication | grep "role:" | cut -d: -f2 | tr -d '\r\n ')

if [ "$ROLE" = "master" ]; then
    echo "✅ Redis уже в режиме master"
    exit 0
fi

echo "⚠️  Redis в режиме $ROLE, переводим в master..."

# Переводим в режим master
docker compose exec -T redis redis-cli SLAVEOF NO ONE || docker compose exec -T redis redis-cli REPLICAOF NO ONE

# Отключаем read-only режим
docker compose exec -T redis redis-cli CONFIG SET replica-read-only no

# Проверяем результат
sleep 1
NEW_ROLE=$(docker compose exec -T redis redis-cli INFO replication | grep "role:" | cut -d: -f2 | tr -d '\r\n ')

if [ "$NEW_ROLE" = "master" ]; then
    echo "✅ Redis успешно переведен в режим master"
    exit 0
else
    echo "❌ Ошибка: Redis все еще в режиме $NEW_ROLE"
    exit 1
fi

