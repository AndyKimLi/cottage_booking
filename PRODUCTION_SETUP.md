# Production Setup Guide

## 🚀 Production Environment Variables

Create `.env` file with the following variables:

```bash
# Production Environment Variables
TELEGRAM_BOT_TOKEN=8454218978:AAFLi7J5C-T5KDxla0fJ278Ohst9qfO2t0Q
DEBUG=0
SECRET_KEY=django-insecure-my-super-secret-key-for-cottage-booking-2024
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,51.250.113.151
DB_PASSWORD=strong-production-password-2024
RABBITMQ_PASSWORD=strong-rabbitmq-password-2024
MONITORING_ENABLED=true

# Database Settings
DB_HOST=db
DB_NAME=cottage_booking
DB_USER=postgres
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://redis:6379/0

# Celery Settings
CELERY_BROKER_URL=amqp://admin:${RABBITMQ_PASSWORD}@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## 🔧 Production Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/cottage-booking.git
cd cottage-booking
```

### 2. Create .env file
```bash
cp .env.production .env
# Edit .env with your domain and passwords
```

### 3. Start Services
```bash
# Start basic services first
docker-compose up -d db redis rabbitmq

# Wait for services to start
sleep 30

# Start application
docker-compose up -d web celery telegram_bot backup

# Start monitoring (optional)
docker-compose up -d prometheus grafana loki promtail alertmanager

# Start nginx (after SSL setup)
docker-compose up -d nginx
```

### 4. Run Migrations
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py createsuperuser
```

### 5. Setup SSL (if domain available)
```bash
./scripts/setup_ssl.sh yourdomain.com your@email.com
```

## 🛡️ Security Checklist

- [ ] Change default passwords
- [ ] Set DEBUG=0
- [ ] Configure ALLOWED_HOSTS
- [ ] Setup SSL certificates
- [ ] Configure firewall
- [ ] Enable monitoring
- [ ] Setup backups

## 📊 Monitoring

- **Prometheus**: http://yourdomain.com:9090
- **Grafana**: http://yourdomain.com:3000 (admin/admin123)
- **AlertManager**: http://yourdomain.com:9093

## 🔄 Backup & Restore

### Automatic Backups
Backups are created every 24 hours and stored in `./backups/`

### Manual Backup
```bash
docker-compose exec backup pg_dump -h db -U postgres cottage_booking > backup_manual.sql
```

### Restore Backup
```bash
docker-compose exec db psql -U postgres -d cottage_booking < backup_manual.sql
```
