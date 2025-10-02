# 🔒 Настройка безопасности

## ✅ Что уже настроено

### 1. 🔒 HTTPS/SSL с Let's Encrypt
- ✅ Nginx конфигурация с SSL
- ✅ Автоматический редирект HTTP → HTTPS
- ✅ Современные SSL настройки (TLS 1.2/1.3)
- ✅ HSTS заголовки для безопасности

### 2. 🔒 CORS настройки
- ✅ Настроены разрешенные домены
- ✅ Настроены заголовки CORS
- ✅ Поддержка credentials

### 3. 🔒 Rate Limiting
- ✅ API ограничения (100 запросов/час для GET)
- ✅ Создание бронирований (10/час)
- ✅ Обновления (20/час)
- ✅ Удаления (5/час)

### 4. 🔒 Защита от брутфорса
- ✅ Django Axes (5 попыток → блокировка на 1 час)
- ✅ Страница блокировки
- ✅ Логирование попыток входа

## 🚀 Как запустить с безопасностью

### 1. Настройка SSL сертификатов

**Linux/Mac:**
```bash
# Замените на ваш домен и email
./scripts/setup_ssl.sh yourdomain.com your@email.com
```

**Windows:**
```cmd
scripts\setup_ssl.bat yourdomain.com your@email.com
```

### 2. Запуск приложения
```bash
# Сборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps
```

### 3. Проверка безопасности

**HTTPS работает:**
```bash
curl -I https://yourdomain.com
# Должен вернуть 200 OK с SSL сертификатом
```

**Rate limiting работает:**
```bash
# Быстрые запросы к API должны получить 429 Too Many Requests
for i in {1..20}; do curl -X GET https://yourdomain.com/api/bookings/; done
```

## 🛡️ Дополнительные настройки безопасности

### 1. Настройка домена в CORS
Отредактируйте `cottage_booking/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

### 2. Настройка Nginx для вашего домена
Отредактируйте `nginx/nginx.conf`:
```nginx
server_name yourdomain.com www.yourdomain.com;
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

### 3. Обновление переменных окружения
Создайте `.env` файл:
```env
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-super-secret-key-here
```

## 🔍 Мониторинг безопасности

### Логи безопасности
```bash
# Просмотр логов блокировок
docker-compose logs web | grep "AXES"

# Просмотр rate limiting
docker-compose logs nginx | grep "limiting"
```

### Проверка SSL
```bash
# Проверка SSL сертификата
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

## ⚠️ Важные замечания

1. **Не используйте DEBUG=1 в продакшене**
2. **Измените SECRET_KEY на уникальный**
3. **Настройте правильные ALLOWED_HOSTS**
4. **Регулярно обновляйте SSL сертификаты**
5. **Мониторьте логи на подозрительную активность**

## 🆘 В случае проблем

### SSL не работает
```bash
# Проверьте сертификаты
docker-compose exec nginx ls -la /etc/letsencrypt/live/

# Перезапустите nginx
docker-compose restart nginx
```

### Rate limiting слишком строгий
Отредактируйте `apps/bookings/views.py` и измените лимиты:
```python
@method_decorator(ratelimit(key='ip', rate='200/h', method='GET'), name='list')
```

### CORS блокирует запросы
Проверьте `CORS_ALLOWED_ORIGINS` в `settings.py` и добавьте ваш домен.
