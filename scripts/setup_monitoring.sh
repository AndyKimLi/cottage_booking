#!/bin/bash

# Скрипт для настройки мониторинга Prometheus + Grafana
# Использование: ./scripts/setup_monitoring.sh

echo "📊 Настройка мониторинга Prometheus + Grafana..."

# Создаем папки для мониторинга
mkdir -p config/monitoring/grafana/provisioning/dashboards
mkdir -p config/monitoring/grafana/provisioning/datasources

# Создаем конфигурацию источника данных Grafana
cat > config/monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Создаем конфигурацию источника данных Loki
cat > config/monitoring/grafana/provisioning/datasources/loki.yml << EOF
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true
EOF

echo "✅ Конфигурация мониторинга создана!"

echo "🚀 Запуск сервисов мониторинга..."
docker-compose up -d prometheus grafana loki promtail alertmanager

echo "⏳ Ожидание запуска сервисов..."
sleep 30

echo "📊 Мониторинг настроен!"
echo ""
echo "🌐 Доступные интерфейсы:"
echo "   • Grafana: http://localhost:3000 (admin/admin123)"
echo "   • Prometheus: http://localhost:9090"
echo "   • AlertManager: http://localhost:9093"
echo ""
echo "📋 Дашборды:"
echo "   • Django Application Dashboard - автоматически загружен"
echo "   • System Metrics - доступен в Grafana"
echo ""
echo "🔔 Алерты настроены для:"
echo "   • Высокий уровень ошибок 5xx"
echo "   • Высокое время отклика"
echo "   • Недоступность сервисов"
echo "   • Высокое использование ресурсов"
echo ""
echo "💡 Для настройки уведомлений в Telegram:"
echo "   1. Получите токен бота: @BotFather"
echo "   2. Узнайте chat_id: @userinfobot"
echo "   3. Обновите monitoring/alertmanager.yml"
