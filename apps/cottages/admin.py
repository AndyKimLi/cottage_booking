from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
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
        ('Календарь доступности', {
            'fields': ('availability_calendar',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['availability_calendar']
    
    def availability_calendar(self, obj):
        """Показывает календарь доступности коттеджа"""
        if not obj.pk:
            return mark_safe("Сохраните коттедж для просмотра календаря")
        
        # Получаем бронирования на год вперед
        from apps.bookings.models import Booking, BookingStatus
        from datetime import date, timedelta
        
        today = date.today()
        end_date = today + timedelta(days=365)  # Год вперед
        
        bookings = Booking.objects.filter(
            cottage=obj,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            check_out__gte=today
        ).order_by('check_in')
        
        # Создаем HTML календаря
        calendar_html = self._generate_calendar_html(obj, bookings, today, end_date)
        print(f"DEBUG: Генерируем календарь для коттеджа {obj.name}, бронирований: {bookings.count()}")
        return mark_safe(calendar_html)
    
    availability_calendar.short_description = 'Календарь доступности'
    
    def _generate_calendar_html(self, cottage, bookings, start_date, end_date):
        """Генерирует HTML календаря"""
        # Создаем список занятых дат
        booked_dates = set()
        for booking in bookings:
            current_date = booking.check_in
            while current_date < booking.check_out:
                booked_dates.add(current_date)
                current_date += timedelta(days=1)
        
        # Уникальные ID для каждого коттеджа
        cottage_id = cottage.pk
        container_id = "calendarContainer_" + str(cottage_id)
        button_id = "calendarToggleText_" + str(cottage_id)
        function_name = "toggleCalendar_" + str(cottage_id)
        
        # Генерируем компактный календарь
        calendar_html = '''
        <div style="margin: 20px 0;">
            <h3>📅 Календарь доступности: ''' + cottage.name + '''</h3>
            
            <div style="margin-bottom: 15px;">
                <button type="button" onclick="''' + function_name + '''()" style="
                    background: #007bff; 
                    color: white; 
                    border: none; 
                    padding: 8px 16px; 
                    border-radius: 4px; 
                    cursor: pointer;
                    font-size: 14px;
                ">
                    <span id="''' + button_id + '''">Скрыть календарь</span>
                </button>
            </div>
            
            <div id="''' + container_id + '''" style="display: block;">
                <div style="display: flex; gap: 15px; flex-wrap: wrap; max-width: 100%; overflow-x: auto;">
        '''
        
        current_date = start_date
        month_count = 0
        
        while current_date <= end_date and month_count < 12:
            # Начало месяца
            month_start = current_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            calendar_html += self._generate_month_calendar(month_start, month_end, booked_dates, current_date)
            
            # Переходим к следующему месяцу
            current_date = month_end + timedelta(days=1)
            month_count += 1
        
        calendar_html += '''
                </div>
                <div style="margin-top: 15px; display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <div style="width: 16px; height: 16px; background: #28a745; border: 1px solid #ddd;"></div>
                        <span style="font-size: 12px;">Свободно</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <div style="width: 16px; height: 16px; background: #dc3545; border: 1px solid #ddd;"></div>
                        <span style="font-size: 12px;">Занято</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <div style="width: 16px; height: 16px; background: #6c757d; border: 1px solid #ddd;"></div>
                        <span style="font-size: 12px;">Прошедшая дата</span>
                    </div>
                </div>
            </div>
            
            <script>
                function ''' + function_name + '''() {
                    console.log('Кнопка нажата!');
                    const container = document.getElementById('''' + container_id + '''');
                    const button = document.getElementById('''' + button_id + '''');
                    
                    console.log('Container:', container);
                    console.log('Button:', button);
                    
                    if (container && button) {
                        if (container.style.display === 'none' || container.style.display === '') {
                            container.style.display = 'block';
                            button.textContent = 'Скрыть календарь';
                            console.log('Календарь показан');
                        } else {
                            container.style.display = 'none';
                            button.textContent = 'Показать календарь';
                            console.log('Календарь скрыт');
                        }
                    } else {
                        console.log('Элементы не найдены!');
                    }
                }
            </script>
        </div>
        '''
        
        return calendar_html
    
    def _generate_month_calendar(self, month_start, month_end, booked_dates, today):
        """Генерирует компактный календарь для одного месяца"""
        month_name = month_start.strftime('%B %Y')
        
        # Начало недели (понедельник)
        calendar_start = month_start - timedelta(days=month_start.weekday())
        
        calendar_html = '''
        <div style="border: 1px solid #ddd; border-radius: 6px; padding: 10px; background: white; min-width: 200px; max-width: 220px;">
            <h4 style="text-align: center; margin: 0 0 10px 0; color: #2c3e50; font-size: 14px;">''' + month_name + '''</h4>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 1px; text-align: center;">
        '''
        
        # Дни недели (компактные)
        days_of_week = ['П', 'В', 'С', 'Ч', 'П', 'С', 'В']
        for day in days_of_week:
            calendar_html += '<div style="font-weight: bold; padding: 3px; background: #f8f9fa; font-size: 10px;">' + day + '</div>'
        
        # Дни месяца
        current_date = calendar_start
        for week in range(6):  # Максимум 6 недель
            for day in range(7):
                if current_date.month == month_start.month or (current_date < month_start and current_date >= calendar_start):
                    # Определяем стиль дня
                    if current_date in booked_dates:
                        style = "background: #dc3545; color: white;"
                        title = "Занято - " + current_date.strftime('%d.%m.%Y')
                    elif current_date < today:
                        style = "background: #6c757d; color: white;"
                        title = "Прошедшая дата - " + current_date.strftime('%d.%m.%Y')
                    else:
                        style = "background: #28a745; color: white;"
                        title = "Свободно - " + current_date.strftime('%d.%m.%Y')
                    
                    calendar_html += '''
                    <div style="''' + style + ''' padding: 4px; border-radius: 3px; font-size: 10px; min-height: 20px; display: flex; align-items: center; justify-content: center;" title="''' + title + '''">
                        ''' + str(current_date.day) + '''
                    </div>
                    '''
                else:
                    calendar_html += '<div style="padding: 4px; min-height: 20px;"></div>'
                
                current_date += timedelta(days=1)
            
            # Если мы прошли весь месяц, выходим
            if current_date > month_end:
                break
        
        calendar_html += '''
            </div>
        </div>
        '''
        
        return calendar_html


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
