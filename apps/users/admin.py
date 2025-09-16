from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import User
from apps.bookings.models import Booking


class BookingInline(admin.TabularInline):
    """Inline для отображения бронирований пользователя"""
    model = Booking
    extra = 0
    readonly_fields = [
        'cottage', 'check_in', 'check_out', 'guests',
        'total_price', 'created_at'
    ]
    fields = [
        'cottage', 'check_in', 'check_out', 'guests',
        'total_price', 'status', 'created_at'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request, obj=None):
        """Запрещаем добавление новых бронирований через inline"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление бронирований через inline"""
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей с расширенным функционалом"""

    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'phone', 'is_verified', 'is_active', 'is_staff',
        'date_joined', 'bookings_count'
    ]
    list_filter = [
        'is_verified', 'is_active', 'is_staff', 'is_superuser',
        'date_joined', 'date_of_birth'
    ]
    search_fields = [
        'email', 'username', 'first_name', 'last_name', 'phone'
    ]
    ordering = ['-date_joined']

    # Поля для отображения в списке
    list_editable = ['is_verified', 'is_active']

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'email', 'password')
        }),
        ('Персональная информация', {
            'fields': (
                'first_name', 'last_name', 'phone', 'date_of_birth'
            )
        }),
        ('Права доступа', {
            'fields': (
                'is_active', 'is_verified', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Inline для бронирований
    inlines = [BookingInline]

    # Поля для создания нового пользователя
    add_fieldsets = (
        ('Основная информация', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Персональная информация', {
            'fields': (
                'first_name', 'last_name', 'phone', 'date_of_birth'
            )
        }),
        ('Права доступа', {
            'fields': (
                'is_active', 'is_verified', 'is_staff', 'is_superuser'
            )
        }),
    )

    readonly_fields = ['date_joined', 'last_login']

    def bookings_count(self, obj):
        """Показывает количество бронирований пользователя"""
        count = obj.bookings.count()
        if count > 0:
            url = reverse('admin:bookings_booking_changelist') + \
                f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} бронирований</a>', url, count)
        return '0 бронирований'
    bookings_count.short_description = 'Бронирования'
    bookings_count.admin_order_field = 'bookings__count'

    def get_queryset(self, request):
        """Оптимизация запросов с prefetch_related"""
        return super().get_queryset(request).prefetch_related('bookings')

    # Кастомные действия
    actions = [
        'verify_users', 'unverify_users', 'activate_users', 'deactivate_users'
    ]

    def verify_users(self, request, queryset):
        """Подтвердить выбранных пользователей"""
        updated = queryset.update(is_verified=True)
        self.message_user(
            request, f'{updated} пользователей подтверждено.'
        )
    verify_users.short_description = "Подтвердить выбранных пользователей"

    def unverify_users(self, request, queryset):
        """Отменить подтверждение выбранных пользователей"""
        updated = queryset.update(is_verified=False)
        self.message_user(
            request, f'{updated} пользователей не подтверждено.'
        )
    unverify_users.short_description = "Отменить подтверждение пользователей"

    def activate_users(self, request, queryset):
        """Активировать выбранных пользователей"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f'{updated} пользователей активировано.'
        )
    activate_users.short_description = "Активировать выбранных пользователей"

    def deactivate_users(self, request, queryset):
        """Деактивировать выбранных пользователей"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f'{updated} пользователей деактивировано.'
        )
    deactivate_users.short_description = "Деактивировать пользователей"