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
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views import View
from datetime import timedelta, datetime
import logging
from .models import Booking, BookingStatus
from .serializers import BookingSerializer, BookingCreateSerializer
from .forms import BookingForm
from apps.cottages.models import Cottage

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='100/h', method='GET'), name='list')
@method_decorator(ratelimit(key='ip', rate='10/h', method='POST'), name='create')
@method_decorator(ratelimit(key='ip', rate='20/h', method='PUT'), name='update')
@method_decorator(ratelimit(key='ip', rate='20/h', method='PATCH'), name='partial_update')
@method_decorator(ratelimit(key='ip', rate='5/h', method='DELETE'), name='destroy')
class BookingViewSet(viewsets.ModelViewSet):
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
        booking = self.get_object()
        if booking.status == Booking.BookingStatus.CONFIRMED:
            booking.status = Booking.BookingStatus.CANCELLED
            booking.save()
            return Response({'message': _('Booking cancelled')})
        return Response(
            {'error': _('Cannot cancel this booking')}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'bookings/create.html'
    
    def get(self, request, *args, **kwargs):
        list(messages.get_messages(request))
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        cottage_id = self.request.GET.get('cottage')
        if cottage_id:
            try:
                cottage = get_object_or_404(Cottage, id=cottage_id, is_active=True)
                context['cottage'] = cottage
                
                form = BookingForm(cottage=cottage, user=self.request.user)
                context['form'] = form
                
                check_in = self.request.GET.get('check_in')
                check_out = self.request.GET.get('check_out')
                if check_in:
                    form.fields['check_in'].initial = check_in
                if check_out:
                    form.fields['check_out'].initial = check_out
                
                booked_dates = self.get_booked_dates(cottage_id)
                context['booked_dates'] = booked_dates
                    
            except Cottage.DoesNotExist:
                messages.error(self.request, _('Cottage not found'))
                return redirect('cottages:page')
        else:
            messages.error(self.request, _('Cottage not specified for booking'))
            return redirect('cottages:page')
        
        return context
    
    def get_booked_dates(self, cottage_id):
        """Получает забронированные даты для коттеджа"""
        from datetime import date, timedelta
        
        bookings = Booking.objects.filter(
            cottage_id=cottage_id,
            status__in=[BookingStatus.CONFIRMED, BookingStatus.PENDING]
        ).exclude(
            check_out__lte=date.today()  # Исключаем уже завершенные бронирования
        )
        
        booked_dates = []
        for booking in bookings:
            current_date = booking.check_in
            while current_date <= booking.check_out:
                booked_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
        
        logger.debug(f"Забронированные даты для коттеджа {cottage_id}: {booked_dates}")
        return booked_dates
    
    def post(self, request, *args, **kwargs):
        cottage_id = request.GET.get('cottage')
        if not cottage_id:
            messages.error(request, _('Cottage not specified for booking'))
            return redirect('cottages:page')
        
        try:
            cottage = get_object_or_404(Cottage, id=cottage_id, is_active=True)
        except Cottage.DoesNotExist:
            messages.error(request, _('Cottage not found'))
            return redirect('cottages:page')
        
        form = BookingForm(request.POST, cottage=cottage, user=request.user)
        
        if form.is_valid():
            try:
                booking = form.save()
                return redirect('users:bookings')
            except Exception as e:
                messages.error(request, _('Error creating booking: %(error)s') % {'error': str(e)})
        else:
            messages.error(request, _('Please correct errors in the form'))
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


class BookingDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'bookings/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = kwargs.get('booking_id')
        
        try:
            booking = get_object_or_404(
                Booking.objects.select_related('cottage').prefetch_related(
                    'cottage__amenities__amenity'
                ), 
                id=booking_id
            )
            
            if not (self.request.user == booking.user or self.request.user.is_staff):
                messages.error(self.request, _('You do not have permission to view this booking'))
                return redirect('users:bookings')
            
            from datetime import date, timedelta
            context['booking'] = booking
            context['today'] = date.today()
            context['tomorrow'] = date.today() + timedelta(days=1)
            
            booked_dates = self.get_booked_dates(booking.cottage.id, booking.id)
            context['booked_dates'] = booked_dates
            
            return context
            
        except Booking.DoesNotExist:
            messages.error(self.request, _('Booking not found'))
            return redirect('users:bookings')
    
    def get_booked_dates(self, cottage_id, current_booking_id):
        from datetime import date
        
        bookings = Booking.objects.filter(
            cottage_id=cottage_id,
            status__in=['confirmed', 'pending']
        ).exclude(
            id=current_booking_id
        ).exclude(
            check_out__lte=date.today()
        )
        
        booked_dates = []
        for booking in bookings:
            current_date = booking.check_in
            while current_date < booking.check_out:
                booked_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
        
        return booked_dates




class BookingEditView(LoginRequiredMixin, View):    
    def post(self, request, booking_id):
        try:
            booking = get_object_or_404(Booking, id=booking_id)
            
            if not (request.user == booking.user or request.user.is_staff):
                messages.error(request, _('You do not have permission to edit this booking'))
                return redirect('users:bookings')
            
            if booking.status != BookingStatus.PENDING:
                if booking.status == BookingStatus.CONFIRMED:
                    messages.error(
                        request,
                        _('Confirmed bookings cannot be edited. You can cancel the booking and create a new one.')
                    )
                elif booking.status == BookingStatus.CANCELLED:
                    messages.error(
                        request, _('Cannot edit cancelled booking')
                    )
                elif booking.status == BookingStatus.COMPLETED:
                    messages.error(
                        request, _('Cannot edit completed booking')
                    )
                else:
                    messages.error(
                        request, _('This booking cannot be edited')
                    )
                return redirect(f'/bookings/{booking.id}/')
            
            check_in = request.POST.get('check_in')
            check_out = request.POST.get('check_out')
            guests = request.POST.get('guests')
            special_requests = request.POST.get('special_requests', '')
            
            if not all([check_in, check_out, guests]):
                messages.error(request, _('All fields are required'))
                return redirect(f'/bookings/{booking.id}/')
            
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, _('Invalid date format'))
                return redirect(f'/bookings/{booking.id}/')
            
            if check_out_date <= check_in_date:
                messages.error(request, _('Check-out date must be later than check-in date'))
                return redirect(f'/bookings/{booking.id}/')
            
            if int(guests) > booking.cottage.capacity:
                messages.error(request, _('Maximum cottage capacity: %(capacity)s guests') % {'capacity': booking.cottage.capacity})
                return redirect(f'/bookings/{booking.id}/')
            
            booking.check_in = check_in_date
            booking.check_out = check_out_date
            booking.guests = int(guests)
            booking.special_requests = special_requests
            
            nights = (check_out_date - check_in_date).days
            booking.total_price = nights * booking.cottage.price_per_night
            
            booking.save()
            
            return redirect(f'/bookings/{booking.id}/')
            
        except Exception as e:
            messages.error(request, _('An error occurred while updating the booking'))
            return redirect(f'/bookings/{booking_id}/')


class CancelBookingView(LoginRequiredMixin, View):
    
    def post(self, request, booking_id):
        try:
            booking = get_object_or_404(
                Booking, 
                id=booking_id, 
                user=request.user
            )
            
            if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
                messages.error(
                    request, 
                    _('This booking cannot be cancelled')
                )
                return redirect('users:bookings')
            
            logger.debug(f"Cancelling booking {booking.id}, current status: {booking.status}")
            booking.status = BookingStatus.CANCELLED
            booking.save()
            logger.debug(f"Booking {booking.id} cancelled, new status: {booking.status}")
            
            messages.success(request, _('Booking successfully cancelled'))
            
        except Exception as e:
            logger.error(f"Error cancelling booking: {e}")
            messages.error(
                request, 
                _('Error cancelling booking: %(error)s') % {'error': str(e)}
            )
        
        return redirect('users:bookings')
