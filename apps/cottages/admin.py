from django.contrib import admin
from .models import Cottage, CottageImage, Amenity, CottageAmenity


@admin.register(Cottage)
class CottageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_night', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active', 'capacity', 'created_at']
    search_fields = ['name', 'description', 'address']
    list_editable = ['is_active', 'price_per_night']
    ordering = ['name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'address')
        }),
        ('Характеристики', {
            'fields': ('capacity', 'price_per_night', 'is_active')
        }),
    )


@admin.register(CottageImage)
class CottageImageAdmin(admin.ModelAdmin):
    list_display = ['cottage', 'is_primary', 'order']
    list_filter = ['is_primary', 'cottage']
    ordering = ['cottage', 'order']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']
    ordering = ['name']


@admin.register(CottageAmenity)
class CottageAmenityAdmin(admin.ModelAdmin):
    list_display = ['cottage', 'amenity']
    list_filter = ['cottage', 'amenity']
    search_fields = ['cottage__name', 'amenity__name']
