"""
Сигналы для автоматической отправки email уведомлений
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Booking
from .email_utils import send_booking_status_change_email
import logging

logger = logging.getLogger(__name__)


# Убираем проблемные сигналы с кешем


# Альтернативный подход - сигнал только при подтверждении
@receiver(post_save, sender=Booking)
def booking_confirmed_signal(sender, instance, created, **kwargs):
    """
    Отправляет email уведомление при подтверждении бронирования
    """
    try:
        print(f"=== EMAIL SIGNAL TRIGGERED ===")
        print(f"DEBUG SIGNAL: Бронирование {instance.id} сохранено, статус={instance.status}, created={created}")
        
        # Отправляем email только если бронирование подтверждено
        if instance.status == 'confirmed':
            # Проверяем, что есть email для отправки
            email_address = instance.email_address
            print(f"DEBUG: Бронирование {instance.id} подтверждено, email_address = {email_address}")
            
            if email_address:
                print(f"INFO: Бронирование {instance.id} подтверждено, отправляем email на {email_address}")
                
                from .email_utils import send_booking_confirmation_email
                success = send_booking_confirmation_email(instance)
                
                if success:
                    print(f"INFO: Email уведомление о подтверждении бронирования {instance.id} отправлено")
                else:
                    print(f"WARNING: Не удалось отправить email уведомление для бронирования {instance.id}")
            else:
                print(f"WARNING: У бронирования {instance.id} нет email адреса для отправки")
        else:
            print(f"DEBUG: Бронирование {instance.id} не подтверждено (статус: {instance.status})")
            
    except Exception as e:
        print(f"ERROR: Ошибка в сигнале booking_confirmed_signal для бронирования {instance.id}: {str(e)}")
        import traceback
        traceback.print_exc()
