#!/bin/bash

# Скрипт для настройки SSL сертификатов с Let's Encrypt
# Использование: ./scripts/setup_ssl.sh yourdomain.com your@email.com

if [ $# -ne 2 ]; then
    echo "❌ Ошибка: Укажите домен и email"
    echo "Использование: ./scripts/setup_ssl.sh yourdomain.com your@email.com"
    exit 1
fi

DOMAIN=$1
EMAIL=$2

echo "🔒 Настройка SSL сертификатов для домена: $DOMAIN"
echo "📧 Email: $EMAIL"

# Создаем папки для certbot
mkdir -p certbot/www
mkdir -p certbot/conf

# Временно запускаем nginx без SSL для получения сертификатов
echo "🚀 Запуск временного nginx..."
docker-compose up -d nginx

# Ждем запуска nginx
sleep 10

# Получаем сертификат
echo "📜 Получение SSL сертификата..."
docker run --rm \
    -v $(pwd)/certbot/conf:/etc/letsencrypt \
    -v $(pwd)/certbot/www:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    echo "✅ SSL сертификат получен успешно!"
    
    # Обновляем nginx.conf с правильным доменом
    sed -i "s/yourdomain.com/$DOMAIN/g" config/nginx/nginx.conf
    
    # Перезапускаем nginx с SSL
    echo "🔄 Перезапуск nginx с SSL..."
    docker-compose restart nginx
    
    echo "🎉 HTTPS настроен! Ваш сайт доступен по адресу: https://$DOMAIN"
    echo "💡 Не забудьте настроить DNS для домена $DOMAIN"
else
    echo "❌ Ошибка получения SSL сертификата"
    exit 1
fi

