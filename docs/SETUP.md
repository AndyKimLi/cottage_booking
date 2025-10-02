# Настройка проекта

## Переменные окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```bash
# Django настройки
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# База данных
DB_NAME=cottage_booking
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email настройки
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery
CELERY_BROKER_URL=amqp://admin:password@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here

# Stripe
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

## Запуск

```bash
docker-compose up -d
```

## Первоначальная настройка

```bash
# Миграции
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Заполнение базы данных
docker-compose exec web python manage.py populate_cottages
```
