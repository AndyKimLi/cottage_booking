#!/bin/sh

# Скрипт инициализации Redis - гарантирует режим master
# Запускается при старте контейнера через entrypoint

# Запускаем Redis в фоне
redis-server /etc/redis/redis.conf &

# Ждем запуска Redis
sleep 2

# Убираем пароль, если он был установлен (на случай, если был сохранен в данных)
redis-cli CONFIG SET requirepass "" 2>/dev/null || true

# Принудительно переводим в режим master (на случай, если был сохранен старый статус)
redis-cli SLAVEOF NO ONE 2>/dev/null || redis-cli REPLICAOF NO ONE 2>/dev/null || true

# Отключаем read-only режим
redis-cli CONFIG SET replica-read-only no 2>/dev/null || true

# Ждем завершения Redis (основной процесс)
wait

