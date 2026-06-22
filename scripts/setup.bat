@echo off
REM Скрипт для быстрой настройки проекта (Windows)

echo 🚀 Настройка проекта Cottage Booking...

REM Создание виртуального окружения
echo 📦 Создание виртуального окружения...
python -m venv venv

REM Активация виртуального окружения
echo 🔧 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo 📚 Установка зависимостей...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Создание .env файла
echo ⚙️ Создание .env файла...
if not exist .env (
    copy env.example .env
    echo ✅ .env файл создан. Не забудьте отредактировать его!
) else (
    echo ⚠️ .env файл уже существует
)

REM Создание папок
echo 📁 Создание необходимых папок...
if not exist logs mkdir logs
if not exist media\avatars mkdir media\avatars
if not exist media\cottages mkdir media\cottages
if not exist staticfiles mkdir staticfiles

REM Применение миграций
echo 🗄️ Применение миграций...
python manage.py makemigrations
python manage.py migrate

REM Создание суперпользователя
echo 👤 Создание суперпользователя...
echo Введите данные для суперпользователя:
python manage.py createsuperuser

REM Сбор статических файлов
echo 📦 Сбор статических файлов...
python manage.py collectstatic --noinput

echo ✅ Настройка завершена!
echo 🎉 Теперь вы можете запустить проект:
echo    python manage.py runserver

pause
