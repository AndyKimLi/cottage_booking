from django.db import models
from django.core.validators import RegexValidator


class CallbackRequest(models.Model):
    """Заявка на обратный звонок"""
    
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    
    # Контактные данные
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    phone = models.CharField(
        max_length=20, 
        verbose_name='Телефон'
    )
    email = models.EmailField(blank=True, verbose_name='Email')
    
    # Дополнительная информация
    message = models.TextField(blank=True, verbose_name='Сообщение')
    preferred_time = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='Удобное время для звонка'
    )
    
    # Статус и метаданные
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name='Обработано')
    
    # Связь с коттеджем (опционально)
    cottage = models.ForeignKey(
        'cottages.Cottage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Интересующий коттедж'
    )
    
    class Meta:
        verbose_name = 'Заявка на обратный звонок'
        verbose_name_plural = 'Заявки на обратный звонок'
        ordering = ['-created_at']
    
    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        return f"{full_name} - {self.phone} ({self.get_status_display()})"
    
    @property
    def full_name(self):
        """Полное ФИО"""
        full_name = f"{self.last_name} {self.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        return full_name
    
    @property
    def is_new(self):
        return self.status == 'new'
    
    @property
    def is_processed(self):
        return self.status in ['completed', 'cancelled']
