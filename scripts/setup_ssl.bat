@echo off
REM Скрипт для настройки SSL сертификатов с Let's Encrypt (Windows)
REM Использование: scripts\setup_ssl.bat yourdomain.com your@email.com

if "%1"=="" (
    echo ❌ Ошибка: Укажите домен
    echo Использование: scripts\setup_ssl.bat yourdomain.com your@email.com
    exit /b 1
)

if "%2"=="" (
    echo ❌ Ошибка: Укажите email
    echo Использование: scripts\setup_ssl.bat yourdomain.com your@email.com
    exit /b 1
)

set DOMAIN=%1
set EMAIL=%2

echo 🔒 Настройка SSL сертификатов для домена: %DOMAIN%
echo 📧 Email: %EMAIL%

REM Создаем папки для certbot
mkdir certbot\www 2>nul
mkdir certbot\conf 2>nul

REM Временно запускаем nginx без SSL для получения сертификатов
echo 🚀 Запуск временного nginx...
docker-compose up -d nginx

REM Ждем запуска nginx
timeout /t 10 /nobreak >nul

REM Получаем сертификат
echo 📜 Получение SSL сертификата...
docker run --rm ^
    -v "%cd%\certbot\conf:/etc/letsencrypt" ^
    -v "%cd%\certbot\www:/var/www/certbot" ^
    certbot/certbot certonly ^
    --webroot ^
    --webroot-path=/var/www/certbot ^
    --email %EMAIL% ^
    --agree-tos ^
    --no-eff-email ^
    -d %DOMAIN%

if %errorlevel%==0 (
    echo ✅ SSL сертификат получен успешно!
    
    REM Обновляем nginx.conf с правильным доменом
    powershell -Command "(Get-Content config\nginx\nginx.conf) -replace 'yourdomain.com', '%DOMAIN%' | Set-Content config\nginx\nginx.conf"
    
    REM Перезапускаем nginx с SSL
    echo 🔄 Перезапуск nginx с SSL...
    docker-compose restart nginx
    
    echo 🎉 HTTPS настроен! Ваш сайт доступен по адресу: https://%DOMAIN%
    echo 💡 Не забудьте настроить DNS для домена %DOMAIN%
) else (
    echo ❌ Ошибка получения SSL сертификата
    exit /b 1
)
