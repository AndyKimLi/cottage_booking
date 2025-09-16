# Cottage Booking System

Система бронирования коттеджей на Django.

## Технологический стек

- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **База данных**: PostgreSQL
- **Кеширование**: Redis
- **Очереди**: Celery
- **WebSocket**: Django Channels
- **Контейнеризация**: Docker

## Структура проекта

```
cottage_booking/
├── apps/
│   ├── core/           # Основные функции
│   ├── users/          # Пользователи и аутентификация
│   ├── cottages/       # Коттеджи и их управление
│   ├── bookings/       # Система бронирования
│   ├── payments/       # Платежи
│   └── notifications/  # Уведомления
├── cottage_booking/    # Настройки Django
├── templates/          # HTML шаблоны
├── static/            # Статические файлы
└── media/             # Медиа файлы
```

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd cottage
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 5. Настройка базы данных
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Запуск сервера разработки
```bash
python manage.py runserver
```

## Запуск с Docker

```bash
docker-compose up --build
```

## Основные функции

- ✅ Регистрация и аутентификация пользователей
- ✅ Управление коттеджами (CRUD)
- ✅ Система бронирования
- ✅ Поиск и фильтрация коттеджей
- ✅ Проверка доступности
- ✅ API для мобильных приложений
- ✅ WebSocket уведомления
- ✅ Система платежей (заготовка)

## API Endpoints

### Пользователи
- `POST /api/v1/auth/register/` - Регистрация
- `POST /api/v1/auth/login/` - Вход
- `POST /api/v1/auth/logout/` - Выход
- `GET /api/v1/auth/profiles/me/` - Мой профиль

### Коттеджи
- `GET /api/v1/cottages/` - Список коттеджей
- `GET /api/v1/cottages/{id}/` - Детали коттеджа
- `GET /api/v1/cottages/search/` - Поиск коттеджей
- `GET /api/v1/cottages/{id}/availability/` - Проверка доступности

### Бронирования
- `GET /api/v1/bookings/` - Мои бронирования
- `POST /api/v1/bookings/` - Создать бронирование
- `POST /api/v1/bookings/{id}/cancel/` - Отменить бронирование

## Разработка

### Запуск тестов
```bash
pytest
```

### Линтинг
```bash
black .
flake8
isort .
```

### Pre-commit hooks
```bash
pre-commit install
```

## Production

Для production используйте:
- Gunicorn вместо runserver
- Nginx как reverse proxy
- PostgreSQL с репликацией
- Redis для кеширования
- Sentry для мониторинга ошибок

## Лицензия

MIT License
