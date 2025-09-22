from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import User
from apps.cottages.models import Cottage


class BookingStatus(models.TextChoices):
    """Статусы бронирования"""
    PENDING = 'pending', 'Ожидает подтверждения'
    CONFIRMED = 'confirmed', 'Подтверждено'
    CANCELLED = 'cancelled', 'Отменено'
    COMPLETED = 'completed', 'Завершено'


class Booking(models.Model):
    """Модель бронирования"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    guest_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email гостя'
    )
    guest_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Имя гостя'
    )
    cottage = models.ForeignKey(
        Cottage, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='Коттедж'
    )
    check_in = models.DateField(verbose_name='Дата заезда')
    check_out = models.DateField(verbose_name='Дата выезда')
    guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество гостей'
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Общая стоимость'
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name='Статус'
    )
    special_requests = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Особые пожелания'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.cottage.name} ({self.check_in} - {self.check_out})"
        else:
            return f"{self.guest_email or 'Гость'} - {self.cottage.name} ({self.check_in} - {self.check_out})"
    
    @property
    def nights(self):
        """Количество ночей"""
        return (self.check_out - self.check_in).days
    
    @property
    def email_address(self):
        """Email адрес для отправки уведомлений"""
        if self.user and self.user.email:
            return self.user.email
        elif self.guest_email:
            return self.guest_email
        return None
    
    @property
    def guest_full_name(self):
        """Полное имя гостя"""
        if self.user:
            return self.user.full_name
        elif self.guest_name:
            return self.guest_name
        return "Уважаемый клиент"
    
    def save(self, *args, **kwargs):
        # Автоматический расчет стоимости
        if not self.total_price:
            nights = (self.check_out - self.check_in).days
            self.total_price = self.cottage.price_per_night * nights
        super().save(*args, **kwargs)
