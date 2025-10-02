# ⚡ Настройка CDN (Cloudflare)

## 🌐 Что такое CDN и зачем он нужен

**CDN (Content Delivery Network)** - сеть серверов по всему миру, которая кэширует ваши статические файлы и доставляет их пользователям с ближайшего сервера.

### Преимущества:
- ⚡ **Скорость** - файлы загружаются с ближайшего сервера
- 🌍 **Глобальность** - быстрая загрузка в любой стране
- 💰 **Экономия** - снижение нагрузки на ваш сервер
- 🔒 **Безопасность** - защита от DDoS атак

## 🚀 Настройка Cloudflare CDN

### 1. Регистрация в Cloudflare

1. Перейдите на [cloudflare.com](https://cloudflare.com)
2. Создайте аккаунт
3. Добавьте ваш домен
4. Cloudflare просканирует DNS записи

### 2. Настройка DNS

**Обязательные записи:**
```
A    @           YOUR_SERVER_IP    Proxied (оранжевое облако)
A    www         YOUR_SERVER_IP    Proxied (оранжевое облако)
CNAME api        yourdomain.com    Proxied (оранжевое облако)
```

**Для статики:**
```
CNAME static     yourdomain.com    Proxied (оранжевое облако)
CNAME media      yourdomain.com    Proxied (оранжевое облако)
```

### 3. Настройка Page Rules

**Правило 1: Статические файлы**
- URL: `yourdomain.com/static/*`
- Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 month

**Правило 2: Медиа файлы**
- URL: `yourdomain.com/media/*`
- Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 week
  - Browser Cache TTL: 1 week

**Правило 3: API (НЕ кэшировать)**
- URL: `yourdomain.com/api/*`
- Settings:
  - Cache Level: Bypass

### 4. Настройка Speed

**Auto Minify:**
- ✅ HTML
- ✅ CSS
- ✅ JavaScript

**Brotli Compression:**
- ✅ Включено

**Rocket Loader:**
- ✅ Включено (для JavaScript)

### 5. Настройка Caching

**Caching Level:**
- Standard (рекомендуется)

**Browser Cache TTL:**
- 4 hours

**Always Online:**
- ✅ Включено

## 🔧 Настройка Django для CDN

### 1. Обновите settings.py

```python
# CDN настройки
if not DEBUG:
    # Cloudflare CDN
    STATIC_URL = 'https://static.yourdomain.com/static/'
    MEDIA_URL = 'https://media.yourdomain.com/media/'
    
    # Дополнительные настройки для CDN
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Кэширование статики
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
```

### 2. Обновите nginx.conf

```nginx
# CDN заголовки
location /static/ {
    alias /app/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
    
    # Cloudflare заголовки
    add_header CF-Cache-Status "HIT";
    add_header CF-Ray $http_cf_ray;
}

location /media/ {
    alias /app/media/;
    expires 30d;
    add_header Cache-Control "public";
    add_header Vary "Accept-Encoding";
}
```

## 📊 Мониторинг CDN

### 1. Cloudflare Analytics

**В панели Cloudflare:**
- Analytics → Web Analytics
- Caching → Cache Analytics
- Security → Security Events

### 2. Ключевые метрики

- **Cache Hit Ratio** - процент запросов из кэша
- **Bandwidth Saved** - сэкономленный трафик
- **Requests** - количество запросов
- **Page Load Time** - время загрузки страниц

### 3. Настройка алертов

**В Cloudflare:**
- Notifications → Add Notification
- Выберите события для уведомлений
- Настройте email/Slack уведомления

## 🚀 Оптимизация производительности

### 1. Автоматическая оптимизация

```bash
# Запуск оптимизации
./scripts/optimize_performance.sh    # Linux/Mac
scripts\optimize_performance.bat     # Windows
```

### 2. Проверка производительности

**Инструменты:**
- [GTmetrix](https://gtmetrix.com) - анализ скорости
- [PageSpeed Insights](https://pagespeed.web.dev) - Google анализ
- [WebPageTest](https://webpagetest.org) - детальный анализ

### 3. Оптимизация изображений

```python
# В Django settings.py
PILLOW_OPTIMIZE = True
PILLOW_OPTIMIZE_QUALITY = 85
```

## 🔒 Безопасность CDN

### 1. Настройка Security

**В Cloudflare:**
- Security Level: Medium
- Challenge Passage: 30 minutes
- Browser Integrity Check: ✅

### 2. Firewall Rules

**Блокировка подозрительных запросов:**
```
(http.request.uri.path contains "/admin" and ip.src.country != "RU")
```

**Rate Limiting:**
- 100 requests per minute per IP
- 1000 requests per minute per IP for API

### 3. SSL/TLS

**Настройки:**
- SSL/TLS encryption mode: Full (strict)
- Edge Certificates: Always Use HTTPS
- HSTS: Enabled

## 💰 Стоимость Cloudflare

### Free Plan (достаточно для старта)
- ✅ Unlimited bandwidth
- ✅ Global CDN
- ✅ SSL certificates
- ✅ DDoS protection
- ✅ Basic analytics

### Pro Plan ($20/месяц)
- ✅ Advanced caching
- ✅ Image optimization
- ✅ Advanced analytics
- ✅ Page Rules (20)
- ✅ Priority support

## 🎯 Результаты оптимизации

### До CDN:
- Время загрузки: 3-5 секунд
- Размер страницы: 2-3 MB
- Время до первого байта: 500-800ms

### После CDN:
- Время загрузки: 1-2 секунды
- Размер страницы: 1-2 MB (сжатие)
- Время до первого байта: 50-100ms

## 🛠️ Устранение проблем

### 1. Статика не загружается

**Проверьте:**
```bash
# Проверка DNS
nslookup static.yourdomain.com

# Проверка SSL
curl -I https://static.yourdomain.com/static/css/style.css
```

### 2. Кэш не обновляется

**Очистка кэша:**
- Cloudflare Dashboard → Caching → Purge Cache
- Или используйте API: `curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache"`

### 3. Медленная загрузка

**Проверьте:**
- Cache Hit Ratio в Analytics
- Настройки Page Rules
- Размер файлов (оптимизируйте изображения)

## 📚 Полезные ссылки

- [Cloudflare Documentation](https://developers.cloudflare.com/)
- [Django Static Files](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [Nginx Caching](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache)
- [Web Performance Best Practices](https://web.dev/performance/)
