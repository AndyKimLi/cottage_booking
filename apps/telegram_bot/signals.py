from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.bookings.models import Booking, BookingStatus
from .bot import get_bot
import threading

print("TELEGRAM BOT SIGNALS LOADED!")


def send_notification_async(booking, notification_type):
    """Отправляет уведомление асинхронно в отдельном потоке"""
    def send_in_thread():
        try:
            from apps.telegram_bot.models import TelegramUser
            import requests
            
            # Получаем только активных пользователей с правами персонала
            active_users = TelegramUser.objects.filter(
                is_active=True,
                user__is_staff=True
            )
            
            if not active_users:
                print("No active staff users for notifications")
                return
            
            print(f"Sending notifications to {len(active_users)} staff users")
            
            # Формируем сообщение
            if notification_type == "new":
                message = f"""
🆕 **Новое бронирование!**

👤 **Клиент:** {booking.user.get_full_name() or booking.user.email}
📞 **Телефон:** {booking.user.phone or 'Не указан'}
🏠 **Коттедж:** {booking.cottage.name}
📅 **Даты:** {booking.check_in} - {booking.check_out}
👥 **Гостей:** {booking.guests}
💰 **Стоимость:** {booking.total_price} ₽
                """
            elif notification_type == "cancelled":
                message = f"""
❌ **Отмена бронирования**

🏠 **Коттедж:** {booking.cottage.name}
👤 **Клиент:** {booking.user.get_full_name() or booking.user.email}
📅 **Даты:** {booking.check_in} - {booking.check_out}
                """
            else:
                message = f"""
🔄 **Изменение статуса бронирования**

🏠 **Коттедж:** {booking.cottage.name}
👤 **Клиент:** {booking.user.get_full_name() or booking.user.email}
📅 **Даты:** {booking.check_in} - {booking.check_out}
📝 **Новый статус:** {booking.get_status_display()}
                """
            
            # Отправляем сообщения параллельно
            import concurrent.futures
            
            def send_to_user(tg_user):
                try:
                    url = ("https://api.telegram.org/bot8454218978:"
                           "AAFLi7J5C-T5KDxla0fJ278Ohst9qfO2t0Q/sendMessage")
                    data = {
                        'chat_id': tg_user.telegram_id,
                        'text': message,
                        'parse_mode': 'Markdown'
                    }
                    
                    response = requests.post(url, data=data, timeout=10)
                    if response.status_code == 200:
                        print(f"Message sent to user {tg_user.telegram_id}")
                        return True
                    else:
                        print(f"Error sending message to user "
                              f"{tg_user.telegram_id}: {response.text}")
                        return False
                        
                except Exception as e:
                    print(f"Error sending message to user "
                          f"{tg_user.telegram_id}: {e}")
                    return False
            
            # Используем ThreadPoolExecutor для параллельной отправки
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(send_to_user, tg_user) 
                          for tg_user in active_users]
                sent_count = sum(1 for future in 
                                concurrent.futures.as_completed(futures) 
                                if future.result())
            
            print(f"Sent {sent_count} of {len(active_users)} notifications")
            
        except Exception as e:
            print(f"Error in async notification: {e}")
            import traceback
            traceback.print_exc()
    
    # Запускаем в отдельном потоке
    thread = threading.Thread(target=send_in_thread)
    thread.daemon = True
    thread.start()


@receiver(post_save, sender=Booking)
def booking_created_or_updated(sender, instance, created, **kwargs):
    """Отправляет уведомление при создании или изменении бронирования"""
    # Отключено: уведомления теперь отправляются через Celery в apps/bookings/signals.py
    return
    # Защита от дублирования уведомлений
    if hasattr(instance, '_notification_sent'):
        return
    
    print("=" * 50)
    print("SIGNAL FUNCTION CALLED!")
    print("=" * 50)
    try:
        print("=" * 50)
        print(f"SIGNAL TRIGGERED! Booking {instance.id}")
        print(f"Created: {created}")
        print(f"Status: {instance.status}")
        print(f"BookingStatus.CANCELLED = {BookingStatus.CANCELLED}")
        print(f"Status comparison: {instance.status} == "
              f"{BookingStatus.CANCELLED} = "
              f"{instance.status == BookingStatus.CANCELLED}")
        print("=" * 50)
        
        # Перезагружаем объект с связанными данными
        try:
            booking = Booking.objects.select_related(
                'user', 'cottage').get(id=instance.id)
        except Booking.DoesNotExist:
            print(f"Booking {instance.id} not found, skipping notification")
            return
        
        # Помечаем что уведомление отправлено
        instance._notification_sent = True
        
        # Отправляем уведомление ТОЛЬКО через этот сигнал (убедитесь, что другие источники отключены)
        if created:
            print(f"Sending new booking notification: {booking.id}")
            send_notification_async(booking, "new")
        elif booking.status == BookingStatus.CANCELLED:
            print(f"Sending cancellation notification: {booking.id}")
            send_notification_async(booking, "cancelled")
        else:
            print(f"Sending status change notification: {booking.id}")
            send_notification_async(booking, "status_change")
    except Exception as e:
        print(f"Error sending notification: {e}")
        import traceback
        traceback.print_exc()


@receiver(post_delete, sender=Booking)
def booking_deleted(sender, instance, **kwargs):
    """Отправляет уведомление при удалении бронирования"""
    # Отключено: уведомления теперь отправляются через Celery в apps/bookings/signals.py
    return
