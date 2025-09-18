from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Админка для управления Telegram пользователями"""
    
    list_display = [
        'user', 'telegram_id', 'first_name', 'last_name', 
        'is_active', 'is_staff', 'created_at'
    ]
    list_filter = ['is_active', 'user__is_staff', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'telegram_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'telegram_id', 'is_active')
        }),
        ('Telegram данные', {
            'fields': ('username', 'first_name', 'last_name')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Показываем только пользователей персонала"""
        return super().get_queryset(request).filter(
            user__is_staff=True
        )
    
    def has_add_permission(self, request):
        """Только суперпользователи могут добавлять новых пользователей"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Только суперпользователи могут изменять пользователей"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Только суперпользователи могут удалять пользователей"""
        return request.user.is_superuser
    
    def is_staff(self, obj):
        """Отображает статус персонала"""
        return obj.user.is_staff
    is_staff.boolean = True
    is_staff.short_description = 'Персонал'