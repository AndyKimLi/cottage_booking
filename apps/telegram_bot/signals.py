import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.bookings.models import Booking, BookingStatus

logger = logging.getLogger(__name__)

# Уведомления теперь отправляются через Celery в apps/notifications/tasks.py
# Этот файл оставлен для совместимости, но сигналы отключены

@receiver(post_save, sender=Booking)
def booking_created_or_updated(sender, instance, created, **kwargs):
    """Отправляет уведомление при создании или изменении бронирования"""
    # Отключено: уведомления теперь отправляются через Celery
    logger.debug(f"Booking {instance.id} {'created' if created else 'updated'}, notifications handled by Celery")
    return


@receiver(post_delete, sender=Booking)
def booking_deleted(sender, instance, **kwargs):
    """Отправляет уведомление при удалении бронирования"""
    # Отключено: уведомления теперь отправляются через Celery
    logger.debug(f"Booking {instance.id} deleted, notifications handled by Celery")
    return