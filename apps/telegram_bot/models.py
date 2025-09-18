from django.db import models
from apps.users.models import User


class TelegramUser(models.Model):
    """Модель для хранения Telegram пользователей персонала"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_profile',
        verbose_name='Пользователь'
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID'
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Telegram Username'
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Имя в Telegram'
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Фамилия в Telegram'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'
    
    def __str__(self):
        return f"{self.user.email} ({self.telegram_id})"
