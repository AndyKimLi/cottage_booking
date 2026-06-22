from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging

from apps.cottages.models import Cottage
from apps.bookings.models import Booking, BookingStatus
from apps.users.models import User
from apps.leads.models import CallbackRequest
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


def is_operator(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_operator)
def quick_booking_view(request):
    cottages = Cottage.objects.all()
    
    selected_cottage_id = request.GET.get('cottage')
    calendar_html = ""
    if selected_cottage_id:
        try:
            cottage = Cottage.objects.get(id=selected_cottage_id)
            calendar_html = generate_availability_calendar(cottage)
        except Cottage.DoesNotExist:
            pass
    
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            email = request.POST.get('email', '')
            cottage_id = request.POST.get('cottage')
            check_in = request.POST.get('check_in')
            check_out = request.POST.get('check_out')
            guests = int(request.POST.get('guests', 1))
            special_requests = request.POST.get('special_requests', '')
            
            if not all([first_name, last_name, phone, cottage_id, check_in, check_out]):
                return render(request, 'operator/quick_booking.html', {'cottages': cottages})
            
            user = None
            try:
                user = User.objects.get(phone=phone)
                user.first_name = first_name
                user.last_name = last_name
                if email and user.email != email:
                    if not User.objects.filter(email=email).exists():
                        user.email = email
                user.save()
            except User.DoesNotExist:
                if email:
                    try:
                        user = User.objects.get(email=email)
                        user.first_name = first_name
                        user.last_name = last_name
                        user.phone = phone
                        user.save()
                    except User.DoesNotExist:
                        username = f"client_{phone.replace('+', '').replace(' ', '').replace('-', '')}"
                        user = User.objects.create(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            phone=phone
                        )
                else:
                    username = f"client_{phone.replace('+', '').replace(' ', '').replace('-', '')}"
                    user = User.objects.create(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=f"{username}@example.com",
                        phone=phone
                    )
            
            cottage = Cottage.objects.get(id=cottage_id)
            
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            

            conflicting_bookings = Booking.objects.filter(
                cottage=cottage,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                check_in__lt=check_out_date,
                check_out__gt=check_in_date
            )
            
            logger.debug(f"Проверяем конфликты для коттеджа {cottage.name}")
            logger.debug(f"Новое бронирование: {check_in_date} - {check_out_date}")
            logger.debug(f"Найдено конфликтующих бронирований: {conflicting_bookings.count()}")
            
            if conflicting_bookings.exists():
                conflict_dates = []
                for booking in conflicting_bookings:
                    conflict_dates.append(f"{booking.check_in} - {booking.check_out}")
                    logger.debug(f"Конфликт с бронированием {booking.id}: {booking.check_in} - {booking.check_out} (статус: {booking.status})")
                
                form_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'email': email
                }
                
                calendar_html = generate_availability_calendar(cottage)
                
                return render(request, 'operator/quick_booking.html', {
                    'cottages': cottages,
                    'form_data': form_data,
                    'selected_cottage_id': cottage_id,
                    'calendar_html': calendar_html
                })
            
            booking = Booking.objects.create(
                user=user,
                cottage=cottage,
                check_in=check_in_date,
                check_out=check_out_date,
                guests=guests,
                special_requests=special_requests,
                status=BookingStatus.CONFIRMED,
                guest_email=email if email else None,
                guest_name=f"{first_name} {last_name}" if not user else None
            )
            
            logger.debug(f"BookingStatus.CONFIRMED = {BookingStatus.CONFIRMED}")
            logger.debug(f"Создано бронирование {booking.id} со статусом '{booking.status}' в {booking.created_at}")
            logger.debug(f"get_status_display() = '{booking.get_status_display()}'")
            
            return redirect('operator:dashboard')
            
        except Exception as e:
            logger.error(f"ERROR: Ошибка при создании бронирования: {str(e)}")
            import traceback
            traceback.print_exc()
    
    form_data = {
        'first_name': request.GET.get('first_name', ''),
        'last_name': request.GET.get('last_name', ''),
        'phone': request.GET.get('phone', ''),
        'email': request.GET.get('email', '')
    }
    
    return render(request, 'operator/quick_booking.html', {
        'cottages': cottages,
        'calendar_html': calendar_html,
        'selected_cottage_id': selected_cottage_id,
        'form_data': form_data
    })


@login_required
@user_passes_test(is_operator)
def get_cottage_availability(request, cottage_id):
    try:
        cottage = Cottage.objects.get(id=cottage_id)
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=365)
        
        booked_dates = Booking.objects.filter(
            cottage=cottage,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            check_in__lte=end_date,
            check_out__gte=start_date
        ).values_list('check_in', 'check_out')
        
        unavailable_dates = []
        for check_in, check_out in booked_dates:
            current_date = check_in
            while current_date <= check_out:  # Включаем последний день
                # Используем ISO формат даты
                unavailable_dates.append(current_date.isoformat())
                current_date += timedelta(days=1)
        
        logger.debug(f"Коттедж {cottage.name}, забронированные даты: {unavailable_dates}")
        
        return JsonResponse({
            'success': True,
            'unavailable_dates': unavailable_dates,
            'cottage_name': cottage.name,
            'price_per_night': float(cottage.price_per_night)
        })
        
    except Cottage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Коттедж не найден'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@user_passes_test(is_operator)
def operator_dashboard(request):
    today = timezone.now().date()
    
    today_bookings = Booking.objects.filter(
        created_at__date=today
    ).count()
    
    pending_bookings = Booking.objects.filter(
        status=BookingStatus.PENDING
    ).count()
    
    total_cottages = Cottage.objects.count()
    
    week_ago = today - timedelta(days=7)
    recent_bookings = Booking.objects.filter(
        created_at__gte=week_ago
    ).select_related('user', 'cottage').order_by('-created_at')[:20]
    
    new_callbacks = CallbackRequest.objects.filter(status='new').count()
    recent_callbacks = CallbackRequest.objects.filter(
        created_at__gte=week_ago
    ).select_related('cottage').order_by('-created_at')[:20]
    
    logger.debug(f"Найдено бронирований за 7 дней: {recent_bookings.count()}")
    for booking in recent_bookings:
        logger.debug(f"Бронирование {booking.id}: статус='{booking.status}', создано={booking.created_at}, get_status_display='{booking.get_status_display()}'")
    
    context = {
        'today_bookings': today_bookings,
        'pending_bookings': pending_bookings,
        'total_cottages': total_cottages,
        'recent_bookings': recent_bookings,
        'status_choices': BookingStatus.choices,
        'new_callbacks': new_callbacks,
        'recent_callbacks': recent_callbacks,
        'callback_status_choices': CallbackRequest.STATUS_CHOICES,
    }
    
    return render(request, 'operator/dashboard.html', context)


@login_required
@user_passes_test(is_operator)
@require_POST
@csrf_exempt
def change_callback_status(request):
    try:
        data = json.loads(request.body)
        callback_id = data.get('callback_id')
        new_status = data.get('status')
        
        if not callback_id or not new_status:
            return JsonResponse({'success': False, 'error': 'Не указаны ID заявки или статус'})
        
        callback = get_object_or_404(CallbackRequest, id=callback_id)
        callback.status = new_status
        
        if new_status in ['completed', 'cancelled']:
            callback.processed_at = timezone.now()
        
        callback.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Статус заявки #{callback_id} изменен на "{callback.get_status_display()}"'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def generate_availability_calendar(cottage):
    from datetime import date, timedelta
    
    today = date.today()
    end_date = today + timedelta(days=365)  # Год вперед
    
    bookings = Booking.objects.filter(
        cottage=cottage,
        status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        check_out__gte=today
    ).order_by('check_in')
    
    booked_dates = set()
    for booking in bookings:
        current_date = booking.check_in
        while current_date <= booking.check_out:  # Включаем последний день
            booked_dates.add(current_date)
            current_date += timedelta(days=1)
    
    calendar_html = f'''
    <div style="margin: 20px 0;">
        <h5>📅 Календарь доступности: {cottage.name}</h5>
        <div style="display: flex; gap: 15px; flex-wrap: wrap; max-width: 100%; overflow-x: auto;">
    '''
    
    current_date = today
    month_count = 0
    
    while current_date <= end_date and month_count < 12:
        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        calendar_html += _generate_month_calendar(month_start, month_end, booked_dates, today)
        
        current_date = month_end + timedelta(days=1)
        month_count += 1
    
    calendar_html += '''
        </div>
    </div>
    '''
    
    return mark_safe(calendar_html)


def _generate_month_calendar(month_start, month_end, booked_dates, today):
    russian_months = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    month_name = f"{russian_months[month_start.month]} {month_start.year}"
    
    calendar_start = month_start - timedelta(days=month_start.weekday())
    
    calendar_html = f'''
    <div style="border: 1px solid #ddd; border-radius: 6px; padding: 10px; background: white; min-width: 200px; max-width: 220px;">
        <h4 style="text-align: center; margin: 0 0 10px 0; color: #2c3e50; font-size: 14px;">{month_name}</h4>
        <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 1px; text-align: center;">
    '''
    
    days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    for day in days_of_week:
        calendar_html += f'<div style="font-weight: bold; padding: 3px; background: #f8f9fa; font-size: 10px; color: #000000;">{day}</div>'
    
    current_date = calendar_start
    for week in range(6):
        for day in range(7):
            if current_date.month == month_start.month or (current_date < month_start and current_date >= calendar_start):
                if current_date in booked_dates:
                    style = "background: #dc3545; color: white;"
                    title = "Занято - " + current_date.strftime('%d.%m.%Y')
                elif current_date < today:
                    style = "background: #6c757d; color: white;"
                    title = "Прошедшая дата - " + current_date.strftime('%d.%m.%Y')
                else:
                    style = "background: #28a745; color: white;"
                    title = "Свободно - " + current_date.strftime('%d.%m.%Y')
                
                calendar_html += f'''
                <div style="{style} padding: 4px; border-radius: 3px; font-size: 10px; min-height: 20px; display: flex; align-items: center; justify-content: center;" title="{title}">
                    {current_date.day}
                </div>
                '''
            else:
                calendar_html += '<div style="padding: 4px; min-height: 20px;"></div>'
            
            current_date += timedelta(days=1)
    
    calendar_html += '</div></div>'
    return calendar_html


@login_required
@user_passes_test(is_operator)
@require_POST
@csrf_exempt
def change_booking_status(request):
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        new_status = data.get('status')
        
        if not booking_id or not new_status:
            return JsonResponse({'success': False, 'error': 'Не указаны ID бронирования или статус'})
        
        booking = get_object_or_404(Booking, id=booking_id)
        
        valid_statuses = [choice[0] for choice in BookingStatus.choices]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Неверный статус'})
        
        old_status = booking.status
        booking.status = new_status
        booking.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Статус изменен с {booking.get_status_display()} на {booking.get_status_display()}',
            'new_status': new_status,
            'new_status_display': booking.get_status_display()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ошибка: {str(e)}'})
