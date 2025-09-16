from django.core.management.base import BaseCommand
from apps.bookings.models import Booking
from apps.cottages.models import Cottage
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Проверяет забронированные даты для всех коттеджей'

    def handle(self, *args, **options):
        self.stdout.write('Проверка забронированных дат...\n')
        
        cottages = Cottage.objects.filter(is_active=True)
        
        for cottage in cottages:
            self.stdout.write(f'Коттедж: {cottage.name} (ID: {cottage.id})')
            
            # Получаем активные бронирования
            bookings = Booking.objects.filter(
                cottage_id=cottage.id,
                status__in=['confirmed', 'pending']
            ).exclude(
                check_out__lte=date.today()
            )
            
            self.stdout.write(f'  Найдено активных бронирований: {bookings.count()}')
            
            booked_dates = []
            for booking in bookings:
                self.stdout.write(f'    Бронирование {booking.id}: {booking.check_in} - {booking.check_out}, статус: {booking.status}')
                
                # Добавляем все даты в диапазоне бронирования
                current_date = booking.check_in
                while current_date < booking.check_out:
                    booked_dates.append(current_date.strftime('%Y-%m-%d'))
                    current_date += timedelta(days=1)
            
            self.stdout.write(f'  Забронированные даты: {booked_dates}')
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('Проверка завершена!'))
