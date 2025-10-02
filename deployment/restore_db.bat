@echo off
REM Скрипт для восстановления базы данных из бэкапа (Windows)
REM Использование: restore_db.bat backup_file.sql

if "%1"=="" (
    echo ❌ Ошибка: Укажите файл бэкапа
    echo Использование: restore_db.bat backup_file.sql
    echo.
    echo Доступные бэкапы:
    dir backups\*.sql 2>nul || echo Бэкапы не найдены
    exit /b 1
)

set BACKUP_FILE=%1

if not exist "backups\%BACKUP_FILE%" (
    echo ❌ Файл бэкапа не найден: backups\%BACKUP_FILE%
    exit /b 1
)

echo 🔄 Восстановление базы данных из файла: %BACKUP_FILE%
echo ⚠️  ВНИМАНИЕ: Это удалит все текущие данные!

set /p confirm="Продолжить? (y/N): "
if /i not "%confirm%"=="y" (
    echo ❌ Отменено
    exit /b 1
)

REM Останавливаем приложение
echo 🛑 Остановка приложения...
docker-compose stop web celery telegram_bot

REM Удаляем текущую базу данных
echo 🗑️  Удаление текущей базы данных...
docker-compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS cottage_booking;"
docker-compose exec -T db psql -U postgres -c "CREATE DATABASE cottage_booking;"

REM Восстанавливаем из бэкапа
echo 📥 Восстановление из бэкапа...

REM Проверяем, сжат ли файл
echo %BACKUP_FILE% | findstr /C:".gz" >nul
if %errorlevel%==0 (
    echo 📦 Распаковка сжатого файла...
    gunzip -c "backups\%BACKUP_FILE%" | docker-compose exec -T db psql -U postgres -d cottage_booking
) else (
    docker-compose exec -T db psql -U postgres -d cottage_booking < "backups\%BACKUP_FILE%"
)

REM Запускаем приложение
echo 🚀 Запуск приложения...
docker-compose up -d

echo ✅ База данных успешно восстановлена!
echo 🌐 Приложение доступно по адресу: http://localhost:8000
