from django.db import models
from apps.bookings.models import Booking


class PaymentStatus(models.TextChoices):
    """Статусы платежа"""
    PENDING = 'pending', 'Ожидает оплаты'
    PROCESSING = 'processing', 'Обрабатывается'
    COMPLETED = 'completed', 'Оплачен'
    FAILED = 'failed', 'Ошибка оплаты'
    REFUNDED = 'refunded', 'Возвращен'


class Payment(models.Model):
    """Модель платежа"""
    
    booking = models.OneToOneField(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='payment',
        verbose_name='Бронирование'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Сумма'
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name='Статус'
    )
    payment_method = models.CharField(
        max_length=50,
        verbose_name='Способ оплаты'
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID транзакции'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Платеж {self.id} - {self.booking} ({self.amount})"
