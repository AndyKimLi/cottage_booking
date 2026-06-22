from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_booking_confirmation_email(booking):
    try:
        if not booking.email_address:
            logger.warning(f"У бронирования {booking.id} нет email адреса для отправки")
            return False
            
        if booking.status != 'confirmed':
            logger.warning(f"Бронирование {booking.id} не подтверждено (статус: {booking.status})")
            return False
        
        context = {
            'booking': booking,
            'user': booking.user,
            'cottage': booking.cottage,
        }
        
        html_content = render_to_string('emails/booking_confirmed.html', context)
        text_content = strip_tags(html_content)
        subject = f'✅ Бронирование #{booking.id} подтверждено - {booking.cottage.name}'
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email_address]
        )
        
        email.attach_alternative(html_content, "text/html")
        
        email.send()
        
        logger.info(f"Email уведомление о подтверждении бронирования {booking.id} отправлено на {booking.email_address}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при отправке email уведомления для бронирования {booking.id}: {str(e)}")
        return False


def send_booking_status_change_email(booking, old_status, new_status):
    try:
        if not booking.email_address:
            logger.warning(f"У бронирования {booking.id} нет email адреса для отправки")
            return False
        
        if new_status == 'CONFIRMED':
            return send_booking_confirmation_email(booking)
        else:
            logger.info(f"Статус бронирования {booking.id} изменен на {new_status}, email не отправляется")
            return True
            
    except Exception as e:
        logger.error(f"Ошибка при отправке email уведомления об изменении статуса бронирования {booking.id}: {str(e)}")
        return False
