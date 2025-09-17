from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Booking, BookingStatus


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Админка для бронирований с расширенным функционалом"""

    list_display = [
        'id', 'user_info', 'cottage_info', 'check_in', 'check_out',
        'guests', 'total_price', 'status', 'created_at', 'duration'
    ]
    list_filter = [
        'status', 'check_in', 'check_out', 'created_at',
        'cottage', 'guests'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'cottage__name', 'special_requests'
    ]
    ordering = ['-created_at']

    # Поля для редактирования в списке
    list_editable = ['status']

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'cottage', 'status')
        }),
        ('Даты и гости', {
            'fields': ('check_in', 'check_out', 'guests')
        }),
        ('Стоимость', {
            'fields': ('total_price',)
        }),
        ('Дополнительно', {
            'fields': ('special_requests',),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'total_price']

    # Фильтры для быстрого доступа
    date_hierarchy = 'check_in'

    def user_info(self, obj):
        """Отображает информацию о пользователе с ссылкой"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{} {}</a><br><small>{}</small>',
            url, obj.user.first_name, obj.user.last_name, obj.user.email
        )
    user_info.short_description = 'Пользователь'
    user_info.admin_order_field = 'user__email'

    def cottage_info(self, obj):
        """Отображает информацию о коттедже с ссылкой"""
        url = reverse('admin:cottages_cottage_change', args=[obj.cottage.id])
        return format_html(
            '<a href="{}">{}</a><br><small>{} гостей</small>',
            url, obj.cottage.name, obj.cottage.capacity
        )
    cottage_info.short_description = 'Коттедж'
    cottage_info.admin_order_field = 'cottage__name'


    def duration(self, obj):
        """Показывает продолжительность бронирования"""
        nights = (obj.check_out - obj.check_in).days
        return f"{nights} ночей"
    duration.short_description = 'Продолжительность'
    duration.admin_order_field = 'check_out'

    def get_queryset(self, request):
        """Оптимизация запросов с select_related"""
        return super().get_queryset(request).select_related('user', 'cottage')

    # Кастомные действия
    actions = [
        'confirm_bookings', 'cancel_bookings', 'complete_bookings',
        'send_confirmation_emails'
    ]

    def confirm_bookings(self, request, queryset):
        """Подтвердить выбранные бронирования"""
        updated = queryset.filter(status=BookingStatus.PENDING).update(
            status=BookingStatus.CONFIRMED
        )
        self.message_user(request, f'{updated} бронирований подтверждено.')
    confirm_bookings.short_description = "Подтвердить бронирования"

    def cancel_bookings(self, request, queryset):
        """Отменить выбранные бронирования"""
        updated = queryset.exclude(status=BookingStatus.CANCELLED).update(
            status=BookingStatus.CANCELLED
        )
        self.message_user(request, f'{updated} бронирований отменено.')
    cancel_bookings.short_description = "Отменить выбранные бронирования"

    def complete_bookings(self, request, queryset):
        """Завершить выбранные бронирования"""
        updated = queryset.filter(status=BookingStatus.CONFIRMED).update(
            status=BookingStatus.COMPLETED
        )
        self.message_user(request, f'{updated} бронирований завершено.')
    complete_bookings.short_description = "Завершить выбранные бронирования"

    def send_confirmation_emails(self, request, queryset):
        """Отправить подтверждающие письма (заглушка)"""
        # Здесь можно добавить реальную отправку email
        count = queryset.filter(status=BookingStatus.CONFIRMED).count()
        self.message_user(request, f'Отправлено {count} подтверждающих писем.')
    send_confirmation_emails.short_description = "Отправить письма"

    # Переопределяем save для автоматического пересчета стоимости
    def save_model(self, request, obj, form, change):
        if change:  # При редактировании существующего бронирования
            # Получаем старые значения из базы
            old_obj = Booking.objects.get(pk=obj.pk)
            
            # Проверяем, изменились ли даты или коттедж
            dates_changed = (old_obj.check_in != obj.check_in or 
                           old_obj.check_out != obj.check_out)
            cottage_changed = old_obj.cottage != obj.cottage
            
            if dates_changed or cottage_changed:
                # Пересчитываем стоимость
                nights = (obj.check_out - obj.check_in).days
                obj.total_price = obj.cottage.price_per_night * nights
        else:  # При создании нового бронирования
            nights = (obj.check_out - obj.check_in).days
            obj.total_price = obj.cottage.price_per_night * nights
            
        super().save_model(request, obj, form, change)

    # Добавляем кастомные фильтры в sidebar
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Статистика по статусам
        stats = {}
        for status, _ in BookingStatus.choices:
            count = Booking.objects.filter(status=status).count()
            stats[status] = count

        extra_context['booking_stats'] = stats
        return super().changelist_view(request, extra_context)