from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from django.views import View
from datetime import timedelta, datetime
from .models import Booking, BookingStatus
from .serializers import BookingSerializer, BookingCreateSerializer
from .forms import BookingForm
from apps.cottages.models import Cottage


@method_decorator(ratelimit(key='ip', rate='100/h', method='GET'), name='list')
@method_decorator(ratelimit(key='ip', rate='10/h', method='POST'), name='create')
@method_decorator(ratelimit(key='ip', rate='20/h', method='PUT'), name='update')
@method_decorator(ratelimit(key='ip', rate='20/h', method='PATCH'), name='partial_update')
@method_decorator(ratelimit(key='ip', rate='5/h', method='DELETE'), name='destroy')
class BookingViewSet(viewsets.ModelViewSet):
    """API для бронирований"""
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отменить бронирование"""
        booking = self.get_object()
        if booking.status == Booking.BookingStatus.CONFIRMED:
            booking.status = Booking.BookingStatus.CANCELLED
            booking.save()
            return Response({'message': 'Бронирование отменено'})
        return Response(
            {'error': 'Невозможно отменить это бронирование'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class MyBookingsView(APIView):
    """Мои бронирования"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingCreateView(LoginRequiredMixin, TemplateView):
    """Страница создания бронирования"""
    template_name = 'bookings/create.html'
    
    def get(self, request, *args, **kwargs):
        """Очищаем сообщения при загрузке страницы создания бронирования"""
        # Очищаем все сообщения, чтобы не показывать уведомления от других страниц
        list(messages.get_messages(request))
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем ID коттеджа из параметров
        cottage_id = self.request.GET.get('cottage')
        if cottage_id:
            try:
                cottage = get_object_or_404(Cottage, id=cottage_id, is_active=True)
                context['cottage'] = cottage
                
                # Создаем форму с коттеджем
                form = BookingForm(cottage=cottage, user=self.request.user)
                context['form'] = form
                
                # Предзаполняем даты если переданы в параметрах
                check_in = self.request.GET.get('check_in')
                check_out = self.request.GET.get('check_out')
                if check_in:
                    form.fields['check_in'].initial = check_in
                if check_out:
                    form.fields['check_out'].initial = check_out
                
                # Получаем забронированные даты для этого коттеджа
                booked_dates = self.get_booked_dates(cottage_id)
                context['booked_dates'] = booked_dates
                    
            except Cottage.DoesNotExist:
                messages.error(self.request, 'Коттедж не найден')
                return redirect('cottages:page')
        else:
            messages.error(self.request, 'Не указан коттедж для бронирования')
            return redirect('cottages:page')
        
        return context
    
    def get_booked_dates(self, cottage_id):
        """Получает забронированные даты для коттеджа"""
        from datetime import date, timedelta
        
        # Получаем активные бронирования для коттеджа
        bookings = Booking.objects.filter(
            cottage_id=cottage_id,
            status__in=[BookingStatus.CONFIRMED, BookingStatus.PENDING]
        ).exclude(
            check_out__lte=date.today()  # Исключаем уже завершенные бронирования
        )
        
        booked_dates = []
        for booking in bookings:
            # Добавляем все даты в диапазоне бронирования (включая дату заезда И дату выезда)
            current_date = booking.check_in
            while current_date <= booking.check_out:
                booked_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
        
        print(f"DEBUG: Забронированные даты для коттеджа {cottage_id}: {booked_dates}")
        return booked_dates
    
    def post(self, request, *args, **kwargs):
        cottage_id = request.GET.get('cottage')
        if not cottage_id:
            messages.error(request, 'Не указан коттедж для бронирования')
            return redirect('cottages:page')
        
        try:
            cottage = get_object_or_404(Cottage, id=cottage_id, is_active=True)
        except Cottage.DoesNotExist:
            messages.error(request, 'Коттедж не найден')
            return redirect('cottages:page')
        
        form = BookingForm(request.POST, cottage=cottage, user=request.user)
        
        if form.is_valid():
            try:
                booking = form.save()
                return redirect('users:bookings')
            except Exception as e:
                messages.error(request, f'Ошибка при создании бронирования: {str(e)}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


class BookingDetailView(LoginRequiredMixin, TemplateView):
    """Страница детального просмотра бронирования"""
    template_name = 'bookings/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = kwargs.get('booking_id')
        
        try:
            # Получаем бронирование с предзагруженными данными коттеджа и удобств
            booking = get_object_or_404(
                Booking.objects.select_related('cottage').prefetch_related(
                    'cottage__amenities__amenity'
                ), 
                id=booking_id
            )
            
            # Проверяем права доступа
            if not (self.request.user == booking.user or self.request.user.is_staff):
                messages.error(self.request, 'У вас нет прав для просмотра этого бронирования')
                return redirect('users:bookings')
            
            from datetime import date, timedelta
            context['booking'] = booking
            context['today'] = date.today()
            context['tomorrow'] = date.today() + timedelta(days=1)
            
            # Получаем забронированные даты для этого коттеджа
            booked_dates = self.get_booked_dates(booking.cottage.id, booking.id)
            context['booked_dates'] = booked_dates
            
            return context
            
        except Booking.DoesNotExist:
            messages.error(self.request, 'Бронирование не найдено')
            return redirect('users:bookings')
    
    def get_booked_dates(self, cottage_id, current_booking_id):
        """Получает забронированные даты для коттеджа (исключая текущее бронирование)"""
        from datetime import date
        
        # Получаем активные бронирования для коттеджа, исключая текущее
        bookings = Booking.objects.filter(
            cottage_id=cottage_id,
            status__in=['confirmed', 'pending']
        ).exclude(
            id=current_booking_id  # Исключаем текущее бронирование
        ).exclude(
            check_out__lte=date.today()  # Исключаем уже завершенные бронирования
        )
        
        booked_dates = []
        for booking in bookings:
            # Добавляем все даты в диапазоне бронирования
            current_date = booking.check_in
            while current_date < booking.check_out:
                booked_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
        
        return booked_dates




class BookingEditView(LoginRequiredMixin, View):
    """Редактирование бронирования"""
    
    def post(self, request, booking_id):
        try:
            booking = get_object_or_404(Booking, id=booking_id)
            
            # Проверяем права доступа
            if not (request.user == booking.user or request.user.is_staff):
                messages.error(request, 'У вас нет прав для редактирования этого бронирования')
                return redirect('users:bookings')
            
            # Проверяем, можно ли редактировать (только неподтвержденные брони)
            if booking.status != BookingStatus.PENDING:
                if booking.status == BookingStatus.CONFIRMED:
                    messages.error(
                        request,
                        'Подтвержденные бронирования нельзя редактировать. '
                        'Вы можете отменить бронирование и создать новое.'
                    )
                elif booking.status == BookingStatus.CANCELLED:
                    messages.error(
                        request, 'Нельзя редактировать отмененное бронирование'
                    )
                elif booking.status == BookingStatus.COMPLETED:
                    messages.error(
                        request, 'Нельзя редактировать завершенное бронирование'
                    )
                else:
                    messages.error(
                        request, 'Это бронирование нельзя редактировать'
                    )
                return redirect(f'/bookings/{booking.id}/')
            
            # Получаем данные из формы
            check_in = request.POST.get('check_in')
            check_out = request.POST.get('check_out')
            guests = request.POST.get('guests')
            special_requests = request.POST.get('special_requests', '')
            
            # Валидация
            if not all([check_in, check_out, guests]):
                messages.error(request, 'Все поля обязательны для заполнения')
                return redirect(f'/bookings/{booking.id}/')
            
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Неверный формат даты')
                return redirect(f'/bookings/{booking.id}/')
            
            if check_out_date <= check_in_date:
                messages.error(request, 'Дата выезда должна быть позже даты заезда')
                return redirect(f'/bookings/{booking.id}/')
            
            if int(guests) > booking.cottage.capacity:
                messages.error(request, f'Максимальная вместимость коттеджа: {booking.cottage.capacity} гостей')
                return redirect(f'/bookings/{booking.id}/')
            
            # Обновляем бронирование
            booking.check_in = check_in_date
            booking.check_out = check_out_date
            booking.guests = int(guests)
            booking.special_requests = special_requests
            
            # Пересчитываем стоимость
            nights = (check_out_date - check_in_date).days
            booking.total_price = nights * booking.cottage.price_per_night
            
            booking.save()
            
            return redirect(f'/bookings/{booking.id}/')
            
        except Exception as e:
            messages.error(request, 'Произошла ошибка при обновлении бронирования')
            return redirect(f'/bookings/{booking_id}/')


class CancelBookingView(LoginRequiredMixin, View):
    """Отмена бронирования"""
    
    def post(self, request, booking_id):
        """Обработка отмены бронирования"""
        try:
            booking = get_object_or_404(
                Booking, 
                id=booking_id, 
                user=request.user
            )
            
            # Проверяем, можно ли отменить бронирование
            if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
                messages.error(
                    request, 
                    'Это бронирование нельзя отменить'
                )
                return redirect('users:bookings')
            
            # Отменяем бронирование
            print(f"DEBUG: Cancelling booking {booking.id}, current status: {booking.status}")
            booking.status = BookingStatus.CANCELLED
            booking.save()
            print(f"DEBUG: Booking {booking.id} cancelled, new status: {booking.status}")
            
            messages.success(request, 'Бронирование успешно отменено')
            
        except Exception as e:
            print(f"DEBUG: Error cancelling booking: {e}")
            messages.error(
                request, 
                f'Ошибка при отмене бронирования: {str(e)}'
            )
        
        return redirect('users:bookings')
