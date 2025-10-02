@echo off
REM Скрипт для настройки мониторинга Prometheus + Grafana (Windows)
REM Использование: scripts\setup_monitoring.bat

echo 📊 Настройка мониторинга Prometheus + Grafana...

REM Создаем папки для мониторинга
mkdir monitoring\grafana\provisioning\dashboards 2>nul
mkdir monitoring\grafana\provisioning\datasources 2>nul

REM Создаем конфигурацию источника данных Grafana
echo apiVersion: 1 > monitoring\grafana\provisioning\datasources\prometheus.yml
echo. >> monitoring\grafana\provisioning\datasources\prometheus.yml
echo datasources: >> monitoring\grafana\provisioning\datasources\prometheus.yml
echo   - name: Prometheus >> monitoring\grafana\provisioning\datasources\prometheus.yml
echo     type: prometheus >> monitoring\grafana\provisioning\datasources\prometheus.yml
echo     access: proxy >> monitoring\grafana\provisioning\datasources\prometheus.yml
echo     url: http://prometheus:9090 >> monitoring\grafana\provisioning\datasources\prometheus.yml
echo     isDefault: true >> monitoring\grafana\provisioning\datasources\prometheus.yml
echo     editable: true >> monitoring\grafana\provisioning\datasources\prometheus.yml

REM Создаем конфигурацию источника данных Loki
echo apiVersion: 1 > monitoring\grafana\provisioning\datasources\loki.yml
echo. >> monitoring\grafana\provisioning\datasources\loki.yml
echo datasources: >> monitoring\grafana\provisioning\datasources\loki.yml
echo   - name: Loki >> monitoring\grafana\provisioning\datasources\loki.yml
echo     type: loki >> monitoring\grafana\provisioning\datasources\loki.yml
echo     access: proxy >> monitoring\grafana\provisioning\datasources\loki.yml
echo     url: http://loki:3100 >> monitoring\grafana\provisioning\datasources\loki.yml
echo     editable: true >> monitoring\grafana\provisioning\datasources\loki.yml

echo ✅ Конфигурация мониторинга создана!

echo 🚀 Запуск сервисов мониторинга...
docker-compose up -d prometheus grafana loki promtail alertmanager

echo ⏳ Ожидание запуска сервисов...
timeout /t 30 /nobreak >nul

echo 📊 Мониторинг настроен!
echo.
echo 🌐 Доступные интерфейсы:
echo    • Grafana: http://localhost:3000 (admin/admin123)
echo    • Prometheus: http://localhost:9090
echo    • AlertManager: http://localhost:9093
echo.
echo 📋 Дашборды:
echo    • Django Application Dashboard - автоматически загружен
echo    • System Metrics - доступен в Grafana
echo.
echo 🔔 Алерты настроены для:
echo    • Высокий уровень ошибок 5xx
echo    • Высокое время отклика
echo    • Недоступность сервисов
echo    • Высокое использование ресурсов
echo.
echo 💡 Для настройки уведомлений в Telegram:
echo    1. Получите токен бота: @BotFather
echo    2. Узнайте chat_id: @userinfobot
echo    3. Обновите monitoring\alertmanager.yml
