"""
Сигналы для автоматической отправки уведомлений через Celery
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking, BookingStatus
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Booking)
def booking_notification_signal(sender, instance, created, **kwargs):
    """
    Отправляет уведомления при создании или изменении бронирования
    """
    try:
        logger.info(f"Booking {instance.id} signal triggered: created={created}, status={instance.status}")
        
        # Определяем тип уведомления
        if created:
            notification_type = "new"
        elif instance.status == BookingStatus.CANCELLED:
            notification_type = "cancelled"
        else:
            notification_type = "status_change"
        
        # Отправляем Telegram уведомление через Celery
        from apps.notifications.tasks import send_telegram_notification
        send_telegram_notification.delay(instance.id, notification_type)
        
        # Отправляем email уведомление через Celery (только для подтвержденных)
        if instance.status == 'confirmed':
            from apps.notifications.tasks import send_email_notification
            send_email_notification.delay(instance.id, "confirmed")
        elif instance.status == BookingStatus.CANCELLED:
            from apps.notifications.tasks import send_email_notification
            send_email_notification.delay(instance.id, "cancelled")
            
        logger.info(f"Notifications queued for booking {instance.id}")
        
    except Exception as e:
        logger.error(f"Error in booking_notification_signal for booking {instance.id}: {e}")
        import traceback
        traceback.print_exc()


@receiver(post_delete, sender=Booking)
def booking_deleted_signal(sender, instance, **kwargs):
    """
    Отправляет уведомление при удалении бронирования
    """
    try:
        logger.info(f"Booking {instance.id} deleted, sending notification")
        
        # Отправляем Telegram уведомление через Celery
        from apps.notifications.tasks import send_telegram_notification
        send_telegram_notification.delay(instance.id, "cancelled")
        
        logger.info(f"Deletion notification queued for booking {instance.id}")
        
    except Exception as e:
        logger.error(f"Error in booking_deleted_signal for booking {instance.id}: {e}")
        import traceback
        traceback.print_exc()
