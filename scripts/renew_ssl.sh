#!/bin/bash
# Скрипт для автоматического обновления SSL сертификатов Let's Encrypt

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Пытаемся найти директорию проекта
cd "$PROJECT_DIR" 2>/dev/null || \
cd ~/cottage/cottage_booking 2>/dev/null || \
cd ~/cottage 2>/dev/null || {
    echo "❌ Не удалось найти директорию проекта!"
    echo "Укажите правильный путь в скрипте"
    exit 1
}

echo "🔄 Начало обновления SSL сертификатов..."
echo "📅 Дата: $(date)"

# Останавливаем nginx временно
echo "⏸️  Остановка nginx..."
docker compose stop nginx || true

# Обновляем сертификат
echo "🔐 Обновление сертификата..."
docker run --rm \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d kamchatka-village.ru -d www.kamchatka-village.ru \
  --force-renewal --agree-tos --non-interactive || {
    echo "❌ Ошибка обновления сертификата!"
    docker compose start nginx || true
    exit 1
}

# Запускаем nginx обратно
echo "▶️  Запуск nginx..."
docker compose start nginx || docker compose up -d nginx

# Перезагружаем nginx для применения нового сертификата
echo "🔄 Перезагрузка nginx для применения нового сертификата..."
sleep 2
docker compose exec nginx nginx -s reload || docker compose restart nginx

# Проверяем срок действия нового сертификата
echo "📋 Проверка нового сертификата..."
docker compose exec nginx cat /etc/letsencrypt/live/kamchatka-village.ru/fullchain.pem | \
  openssl x509 -noout -dates || echo "⚠️  Не удалось проверить сертификат"

echo "✅ Обновление SSL сертификатов завершено!"
echo "📅 Дата: $(date)"

