"""
Celery configuration for cottage_booking project.
"""
import os
from celery import Celery

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cottage_booking.settings')

app = Celery('cottage_booking')

# Используем строку конфигурации Django для настройки Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
