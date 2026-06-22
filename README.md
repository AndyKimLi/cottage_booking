# 🏡 Cottage Booking System

Система бронирования коттеджей с полным стеком продакшена.

## 📁 Структура проекта

```
cottage/
├── 📁 apps/                    # Django приложения
│   ├── bookings/              # Бронирования
│   ├── cottages/              # Коттеджи
│   ├── users/                 # Пользователи
│   ├── payments/              # Платежи
│   └── ...
├── 📁 config/                 # Конфигурации
│   ├── nginx/                 # Nginx конфигурация
│   └── monitoring/            # Prometheus, Grafana, Loki
├── 📁 deployment/             # Скрипты развертывания
│   ├── backup.sh             # Бэкапы
│   ├── restore_db.sh         # Восстановление
│   └── list_backups.sh       # Список бэкапов
├── 📁 docs/                   # Документация
│   ├── SECURITY_SETUP.md     # Настройка безопасности
│   ├── MONITORING_SETUP.md   # Настройка мониторинга
│   ├── CDN_SETUP.md          # Настройка CDN
│   └── SETUP.md              # Основная настройка
├── 📁 scripts/               # Утилиты
│   ├── setup_ssl.sh         # SSL сертификаты
│   ├── setup_monitoring.sh  # Мониторинг
│   └── optimize_performance.sh # Оптимизация
├── 📁 templates/            # HTML шаблоны
├── 📁 static/               # Статические файлы
├── 📁 logs/                 # Логи
├── 📁 backups/              # Бэкапы БД
├── 📁 cottage_booking/      # Django проект
├── docker-compose.yml      # Docker конфигурация
├── Dockerfile              # Docker образ
├── requirements.txt        # Python зависимости
└── README.md              # Этот файл
```

## 🚀 Быстрый старт

### 1. Клонирование и настройка
```bash
git clone <repository>
cd cottage
cp .env.example .env  # Настройте переменные
```

### 2. Запуск в разработке
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 3. Настройка для продакшена
```bash
# SSL сертификаты
./scripts/setup_ssl.sh yourdomain.com your@email.com

# Мониторинг
./scripts/setup_monitoring.sh

# Оптимизация
./scripts/optimize_performance.sh
```

## 🌐 Доступные интерфейсы

| Сервис | URL | Описание |
|--------|-----|----------|
| **Приложение** | http://localhost:8000 | Основное приложение |
| **Grafana** | http://localhost:3000 | Мониторинг (admin/admin123) |
| **Prometheus** | http://localhost:9090 | Метрики |
| **AlertManager** | http://localhost:9093 | Алерты |

## 📚 Документация

- [🔒 Безопасность](docs/SECURITY_SETUP.md) - HTTPS, CORS, Rate Limiting
- [📊 Мониторинг](docs/MONITORING_SETUP.md) - Prometheus, Grafana, Loki
- [⚡ CDN](docs/CDN_SETUP.md) - Cloudflare настройка
- [🔄 Бэкапы](docs/BACKUP.md) - Автоматические бэкапы
- [⚙️ Настройка](docs/SETUP.md) - Полная настройка

## 🛠️ Разработка

### Локальная разработка
```bash
# Активация виртуального окружения
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Запуск сервера
python manage.py runserver
```

### Тестирование
```bash
# Запуск тестов
pytest

# С покрытием
pytest --cov=apps
```

## 🔧 Управление

### Бэкапы
```bash
# Создание бэкапа
./deployment/backup.sh

# Список бэкапов
./deployment/list_backups.sh

# Восстановление
./deployment/restore_db.sh backup_file.sql
```

### Мониторинг
```bash
# Просмотр логов
docker-compose logs -f web

# Статус сервисов
docker-compose ps

# Перезапуск
docker-compose restart web
```

## 🚀 Продакшен

### Требования
- Docker & Docker Compose
- Домен с DNS
- SSL сертификат (автоматически)
- Минимум 2GB RAM
- 20GB дискового пространства

### Развертывание
1. Настройте домен в DNS
2. Запустите `./scripts/setup_ssl.sh`
3. Настройте мониторинг
4. Оптимизируйте производительность

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs`
2. Изучите документацию в `docs/`
3. Проверьте статус сервисов в Grafana

## 🎯 Особенности

- ✅ **Безопасность**: HTTPS, защита от DDoS, Rate Limiting
- ✅ **Мониторинг**: Prometheus + Grafana + Loki
- ✅ **Производительность**: Nginx кэширование, Redis, CDN
- ✅ **Надежность**: Автобэкапы, алерты, CI/CD
- ✅ **Масштабируемость**: Docker, микросервисы