@echo off
REM Скрипт для обновления проекта на сервере (Windows)

echo 🚀 Начало обновления проекта...

REM Переход в директорию проекта
cd /d "%~dp0.."

echo 📥 Получение изменений из GitHub...
git pull origin main || git pull origin master

echo 🔨 Пересборка Docker контейнеров...
docker compose build web

echo 🔄 Перезапуск сервисов...
docker compose up -d

echo 📦 Компиляция переводов...
docker compose exec web python manage.py compilemessages

echo 📊 Проверка статуса сервисов...
docker compose ps

echo ✅ Обновление завершено!
echo 📝 Проверьте логи если что-то пошло не так:
echo    docker compose logs -f web

pause

