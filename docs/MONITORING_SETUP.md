# 📊 Настройка мониторинга Prometheus + Grafana

## ✅ Что настроено

### 🔧 **Prometheus** - сбор метрик
- ✅ Сбор метрик Django приложения
- ✅ Мониторинг PostgreSQL, Redis, RabbitMQ
- ✅ Системные метрики (CPU, память, диск)
- ✅ Правила алертов для критических событий

### 📈 **Grafana** - визуализация
- ✅ Дашборд Django приложения
- ✅ Графики производительности
- ✅ Статистика HTTP запросов
- ✅ Время отклика и ошибки

### 📝 **Loki** - сбор логов
- ✅ Логи Django приложения
- ✅ Логи Nginx
- ✅ Системные логи
- ✅ Интеграция с Grafana

### 🚨 **AlertManager** - уведомления
- ✅ Алерты в Telegram
- ✅ Email уведомления
- ✅ Группировка алертов
- ✅ Подавление дубликатов

## 🚀 Запуск мониторинга

### 1. Настройка мониторинга

**Linux/Mac:**
```bash
./scripts/setup_monitoring.sh
```

**Windows:**
```cmd
scripts\setup_monitoring.bat
```

### 2. Запуск всех сервисов
```bash
docker-compose up -d
```

### 3. Проверка статуса
```bash
docker-compose ps
```

## 🌐 Доступные интерфейсы

| Сервис | URL | Логин | Описание |
|--------|-----|-------|----------|
| **Grafana** | http://localhost:3000 | admin/admin123 | Дашборды и визуализация |
| **Prometheus** | http://localhost:9090 | - | Метрики и алерты |
| **AlertManager** | http://localhost:9093 | - | Управление уведомлениями |
| **Loki** | http://localhost:3100 | - | Логи |

## 📊 Дашборды Grafana

### Django Application Dashboard
- **HTTP Requests Rate** - количество запросов в секунду
- **HTTP Response Time** - время отклика (95-й процентиль)
- **HTTP Status Codes** - распределение кодов ответов
- **Database Connections** - количество подключений к БД
- **Request Duration Over Time** - график времени отклика

### Системные метрики
- Использование CPU
- Использование памяти
- Использование диска
- Сетевая активность

## 🔔 Настройка алертов

### 1. Telegram уведомления

**Получите токен бота:**
1. Напишите @BotFather в Telegram
2. Создайте нового бота: `/newbot`
3. Скопируйте токен

**Узнайте chat_id:**
1. Напишите @userinfobot в Telegram
2. Скопируйте ваш ID

**Обновите конфигурацию:**
```yaml
# monitoring/alertmanager.yml
receivers:
  - name: 'telegram-alerts'
    webhook_configs:
      - url: 'https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage'
```

### 2. Email уведомления

Обновите `monitoring/alertmanager.yml`:
```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'
```

## 🚨 Типы алертов

### Критические (Critical)
- **DjangoDown** - приложение недоступно
- **PostgreSQLDown** - база данных недоступна
- **DjangoHighErrorRate** - высокий уровень ошибок 5xx

### Предупреждения (Warning)
- **DjangoHighResponseTime** - высокое время отклика
- **PostgreSQLHighConnections** - много подключений к БД
- **HighMemoryUsage** - высокое использование памяти
- **HighCPUUsage** - высокое использование CPU

## 📈 Метрики Django

### HTTP метрики
- `django_http_requests_total` - общее количество запросов
- `django_http_request_duration_seconds` - время выполнения запросов
- `django_http_requests_by_status` - запросы по статус-кодам

### База данных
- `django_db_connections_total` - подключения к БД
- `django_db_query_duration_seconds` - время выполнения запросов
- `django_db_queries_total` - общее количество запросов к БД

### Кэш
- `django_cache_operations_total` - операции с кэшем
- `django_cache_hits_total` - попадания в кэш
- `django_cache_misses_total` - промахи кэша

## 🔍 Поиск логов

### В Grafana
1. Откройте http://localhost:3000
2. Перейдите в "Explore"
3. Выберите источник "Loki"
4. Используйте LogQL для поиска:

```logql
# Все логи Django
{job="django"}

# Ошибки Django
{job="django"} |= "ERROR"

# Логи по уровню
{job="django"} | json | level="ERROR"

# Логи Nginx
{job="nginx"}

# Ошибки 5xx
{job="nginx"} | json | status >= 500
```

## 🛠️ Настройка дашбордов

### Создание нового дашборда
1. Откройте Grafana (http://localhost:3000)
2. Нажмите "+" → "Dashboard"
3. Добавьте панели с метриками
4. Сохраните дашборд

### Импорт готовых дашбордов
1. Перейдите в "Dashboard" → "Import"
2. Вставьте JSON конфигурацию
3. Настройте источник данных
4. Сохраните

## 🔧 Устранение проблем

### Prometheus не собирает метрики
```bash
# Проверьте статус
docker-compose logs prometheus

# Проверьте конфигурацию
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml
```

### Grafana не подключается к Prometheus
```bash
# Проверьте сеть Docker
docker network ls
docker network inspect cottage_default
```

### Логи не отображаются в Loki
```bash
# Проверьте Promtail
docker-compose logs promtail

# Проверьте конфигурацию
docker-compose exec promtail cat /etc/promtail/config.yml
```

## 📚 Полезные ссылки

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

## 🎯 Следующие шаги

1. **Настройте Telegram бота** для уведомлений
2. **Создайте дополнительные дашборды** для ваших нужд
3. **Настройте retention политики** для логов и метрик
4. **Добавьте custom метрики** для бизнес-логики
