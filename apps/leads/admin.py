from django.contrib import admin
from .models import CallbackRequest


@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    """Админка для заявок на обратный звонок"""
    
    list_display = [
        'full_name', 'phone', 'email', 'status', 'cottage', 'created_at', 'is_new'
    ]
    list_filter = ['status', 'created_at', 'cottage']
    search_fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Контактные данные', {
            'fields': ('first_name', 'last_name', 'middle_name', 'phone', 'email')
        }),
        ('Дополнительная информация', {
            'fields': ('message', 'preferred_time', 'cottage')
        }),
        ('Статус и метаданные', {
            'fields': ('status', 'created_at', 'updated_at', 'processed_at')
        }),
    )
    
    def is_new(self, obj):
        """Показывает, новая ли заявка"""
        return obj.is_new
    is_new.boolean = True
    is_new.short_description = 'Новая'
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем время обработки"""
        if change and obj.status != 'new' and not obj.processed_at:
            from django.utils import timezone
            obj.processed_at = timezone.now()
        super().save_model(request, obj, form, change)
