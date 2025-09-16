#!/bin/bash

# Скрипт для быстрой настройки проекта

echo "🚀 Настройка проекта Cottage Booking..."

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python -m venv venv

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📚 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env файла
echo "⚙️ Создание .env файла..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ .env файл создан. Не забудьте отредактировать его!"
else
    echo "⚠️ .env файл уже существует"
fi

# Создание папок
echo "📁 Создание необходимых папок..."
mkdir -p logs
mkdir -p media/avatars
mkdir -p media/cottages
mkdir -p staticfiles

# Применение миграций
echo "🗄️ Применение миграций..."
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
echo "👤 Создание суперпользователя..."
echo "Введите данные для суперпользователя:"
python manage.py createsuperuser

# Сбор статических файлов
echo "📦 Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "✅ Настройка завершена!"
echo "🎉 Теперь вы можете запустить проект:"
echo "   python manage.py runserver"
