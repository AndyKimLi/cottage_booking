from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_telegram_notification(self, booking_id, notification_type):
    try:
        from apps.bookings.models import Booking
        from apps.telegram_bot.models import TelegramUser
        
        booking = Booking.objects.select_related('user', 'cottage').get(id=booking_id)
        
        active_users = TelegramUser.objects.filter(
            is_active=True,
            user__is_staff=True
        )
        
        if not active_users:
            logger.warning("No active staff users for notifications")
            return False
        
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
        else:  # status_change
            message = f"""
🔄 **Изменение статуса бронирования**

🏠 **Коттедж:** {booking.cottage.name}
👤 **Клиент:** {booking.user.get_full_name() or booking.user.email}
📅 **Даты:** {booking.check_in} - {booking.check_out}
📝 **Новый статус:** {booking.get_status_display()}
            """
        
        sent_count = 0
        for tg_user in active_users:
            try:
                url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': tg_user.telegram_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, data=data, timeout=10)
                if response.status_code == 200:
                    sent_count += 1
                    logger.info(f"Message sent to user {tg_user.telegram_id}")
                else:
                    logger.error(f"Error sending message to user {tg_user.telegram_id}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error sending message to user {tg_user.telegram_id}: {e}")
        
        logger.info(f"Sent {sent_count} of {len(active_users)} notifications")
        return sent_count > 0
        
    except Exception as e:
        logger.error(f"Error in send_telegram_notification: {e}")
        raise self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, booking_id, notification_type):
    try:
        from apps.bookings.models import Booking
        
        booking = Booking.objects.select_related('user', 'cottage').get(id=booking_id)
        
        email_address = booking.email_address
        if not email_address:
            logger.warning(f"Booking {booking_id} has no email address")
            return False
        
        if notification_type == "confirmed":
            subject = f'🎉 Бронирование подтверждено - {booking.cottage.name}'
            template = 'emails/booking_confirmed.html'
        elif notification_type == "cancelled":
            subject = f'❌ Бронирование отменено - {booking.cottage.name}'
            template = 'emails/booking_cancelled.html'
        else:
            subject = f'🔄 Статус бронирования изменен - {booking.cottage.name}'
            template = 'emails/booking_confirmed.html'  # Используем существующий шаблон
        
        context = {
            'booking': booking,
            'user': booking.user,
            'cottage': booking.cottage,
        }
        
        html_content = render_to_string(template, context)
        
        send_mail(
            subject=subject,
            message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_address],
            html_message=html_content,
            fail_silently=False,
        )
        
        logger.info(f"Email notification sent to {email_address} for booking {booking_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error in send_email_notification: {e}")
        raise self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def send_callback_request_notification(self, callback_id):
    try:
        from apps.leads.models import CallbackRequest
        from apps.telegram_bot.models import TelegramUser
        
        callback = CallbackRequest.objects.select_related('cottage').get(id=callback_id)
        
        active_users = TelegramUser.objects.filter(
            is_active=True,
            user__is_staff=True
        )
        
        if not active_users:
            logger.warning("No active staff users for callback notifications")
            return False
        
        message = f"""
📞 **Новая заявка на звонок!**

👤 **Клиент:** {callback.full_name}
📞 **Телефон:** {callback.phone}
📧 **Email:** {callback.email}
🏠 **Коттедж:** {callback.cottage.name if callback.cottage else 'Не указан'}
💬 **Сообщение:** {callback.message}

🔗 **Ссылка:** [Открыть в админке](http://localhost:8000/admin/leads/callbackrequest/{callback.id}/)
        """
        
        sent_count = 0
        for tg_user in active_users:
            try:
                url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': tg_user.telegram_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, data=data, timeout=10)
                if response.status_code == 200:
                    sent_count += 1
                    logger.info(f"Callback notification sent to user {tg_user.telegram_id}")
                else:
                    logger.error(f"Error sending callback notification to user {tg_user.telegram_id}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error sending callback notification to user {tg_user.telegram_id}: {e}")
        
        logger.info(f"Sent {sent_count} of {len(active_users)} callback notifications")
        return sent_count > 0
        
    except Exception as e:
        logger.error(f"Error in send_callback_request_notification: {e}")
        raise self.retry(countdown=60, exc=e)
