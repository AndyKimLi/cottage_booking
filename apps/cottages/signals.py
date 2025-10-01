"""
Сигналы для очистки кэша при изменении коттеджей
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Cottage, CottageImage, CottageAmenity


@receiver(post_save, sender=Cottage)
def clear_cottage_cache_on_save(sender, instance, **kwargs):
    """Очищает кэш при сохранении коттеджа"""
    cache.delete('cottages_list_api')
    cache.delete(f'cottage_detail_{instance.id}')
    cache.delete(f'cottage_detail_html_{instance.id}')
    
    # Очищаем HTML кэш для всех возможных фильтров
    cache.delete_pattern('cottages_html_*')


@receiver(post_delete, sender=Cottage)
def clear_cottage_cache_on_delete(sender, instance, **kwargs):
    """Очищает кэш при удалении коттеджа"""
    cache.delete('cottages_list_api')
    cache.delete(f'cottage_detail_{instance.id}')
    cache.delete(f'cottage_detail_html_{instance.id}')
    cache.delete_pattern('cottages_html_*')


@receiver(post_save, sender=CottageImage)
@receiver(post_delete, sender=CottageImage)
def clear_cottage_cache_on_image_change(sender, instance, **kwargs):
    """Очищает кэш при изменении изображений коттеджа"""
    cache.delete(f'cottage_detail_{instance.cottage.id}')
    cache.delete(f'cottage_detail_html_{instance.cottage.id}')


@receiver(post_save, sender=CottageAmenity)
@receiver(post_delete, sender=CottageAmenity)
def clear_cottage_cache_on_amenity_change(sender, instance, **kwargs):
    """Очищает кэш при изменении удобств коттеджа"""
    cache.delete(f'cottage_detail_{instance.cottage.id}')
    cache.delete(f'cottage_detail_html_{instance.cottage.id}')
