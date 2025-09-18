from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.bookings.models import Booking, BookingStatus
from .bot import get_bot
import asyncio
import threading

print("TELEGRAM BOT SIGNALS LOADED!")


def send_notification_async(booking, notification_type):
    """Отправляет уведомление асинхронно в отдельном потоке"""
    def send_in_thread():
        try:
            from apps.telegram_bot.models import TelegramUser
            import requests
            import time
            
            # Получаем активных пользователей
            active_users = TelegramUser.objects.filter(is_active=True)
            
            if not active_users:
                print("No active users for notifications")
                return
            
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

🔗 **Ссылка:** [Открыть в админке](http://localhost:8000/admin/bookings/booking/{booking.id}/)
                """
            elif notification_type == "cancelled":
                message = f"""
❌ **Отмена бронирования**

🏠 **Коттедж:** {booking.cottage.name}
👤 **Клиент:** {booking.user.get_full_name() or booking.user.email}
📅 **Даты:** {booking.check_in} - {booking.check_out}

🔗 **Ссылка:** [Открыть в админке](http://localhost:8000/admin/bookings/booking/{booking.id}/)
                """
            else:
                message = f"""
🔄 **Изменение статуса бронирования**

🏠 **Коттедж:** {booking.cottage.name}
👤 **Клиент:** {booking.user.get_full_name() or booking.user.email}
📅 **Даты:** {booking.check_in} - {booking.check_out}
📝 **Новый статус:** {booking.get_status_display()}

🔗 **Ссылка:** [Открыть в админке](http://localhost:8000/admin/bookings/booking/{booking.id}/)
                """
            
            # Отправляем сообщения параллельно
            import concurrent.futures
            
            def send_to_user(tg_user):
                try:
                    url = f"https://api.telegram.org/bot8454218978:AAFLi7J5C-T5KDxla0fJ278Ohst9qfO2t0Q/sendMessage"
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
                        print(f"Error sending message to user {tg_user.telegram_id}: {response.text}")
                        return False
                        
                except Exception as e:
                    print(f"Error sending message to user {tg_user.telegram_id}: {e}")
                    return False
            
            # Используем ThreadPoolExecutor для параллельной отправки
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(send_to_user, tg_user) for tg_user in active_users]
                sent_count = sum(1 for future in concurrent.futures.as_completed(futures) if future.result())
            
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
    print("=" * 50)
    print("SIGNAL FUNCTION CALLED!")
    print("=" * 50)
    try:
        print("=" * 50)
        print(f"SIGNAL TRIGGERED! Booking {instance.id}")
        print(f"Created: {created}")
        print(f"Status: {instance.status}")
        print(f"BookingStatus.CANCELLED = {BookingStatus.CANCELLED}")
        print(f"Status comparison: {instance.status} == {BookingStatus.CANCELLED} = {instance.status == BookingStatus.CANCELLED}")
        print("=" * 50)
        
        # Перезагружаем объект с связанными данными
        try:
            booking = Booking.objects.select_related('user', 'cottage').get(id=instance.id)
        except Booking.DoesNotExist:
            print(f"Booking {instance.id} not found, skipping notification")
            return
        
        bot = get_bot()
        
        if created:
            # Новое бронирование
            print(f"Sending new booking notification: {booking.id}")
            send_notification_async(booking, "new")
        else:
            # Изменение существующего бронирования
            if booking.status == BookingStatus.CANCELLED:
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
    try:
        bot = get_bot()
        print(f"Sending deletion notification: {instance.id}")
        run_async_in_thread(
            bot.send_booking_notification(instance, "cancelled")
        )
    except Exception as e:
        print(f"Error sending deletion notification: {e}")
