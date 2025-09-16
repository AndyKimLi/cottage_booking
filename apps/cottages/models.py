from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Cottage(models.Model):
    """Модель коттеджа"""
    
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    address = models.TextField(verbose_name='Адрес')
    capacity = models.PositiveIntegerField(verbose_name='Вместимость')
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Цена за ночь'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Коттедж'
        verbose_name_plural = 'Коттеджи'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CottageImage(models.Model):
    """Изображения коттеджа"""
    
    cottage = models.ForeignKey(
        Cottage, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Коттедж'
    )
    image = models.ImageField(upload_to='cottages/', verbose_name='Изображение')
    is_primary = models.BooleanField(default=False, verbose_name='Основное')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Изображение коттеджа'
        verbose_name_plural = 'Изображения коттеджей'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.cottage.name} - Изображение {self.order}"


class Amenity(models.Model):
    """Удобства коттеджа"""
    
    name = models.CharField(max_length=100, verbose_name='Название')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Иконка')
    
    class Meta:
        verbose_name = 'Удобство'
        verbose_name_plural = 'Удобства'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CottageAmenity(models.Model):
    """Связь коттеджа и удобств"""
    
    cottage = models.ForeignKey(
        Cottage, 
        on_delete=models.CASCADE,
        related_name='amenities',
        verbose_name='Коттедж'
    )
    amenity = models.ForeignKey(
        Amenity, 
        on_delete=models.CASCADE,
        verbose_name='Удобство'
    )
    
    class Meta:
        verbose_name = 'Удобство коттеджа'
        verbose_name_plural = 'Удобства коттеджей'
        unique_together = ['cottage', 'amenity']
    
    def __str__(self):
        return f"{self.cottage.name} - {self.amenity.name}"
