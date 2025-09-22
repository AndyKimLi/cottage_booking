from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bookings'
    verbose_name = 'Бронирования'
    
    def ready(self):
        """
        Подключаем сигналы при запуске приложения
        """
        import apps.bookings.signals