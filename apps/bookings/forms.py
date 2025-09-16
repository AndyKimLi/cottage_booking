from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Booking, BookingStatus


class BookingForm(forms.ModelForm):
    """Форма для бронирования коттеджа"""
    
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests', 'special_requests']
        widgets = {
            'check_in': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'check_out': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
            }),
            'guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Особые пожелания, требования к размещению...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.cottage = kwargs.pop('cottage', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Делаем поля обязательными
        self.fields['check_in'].required = True
        self.fields['check_out'].required = True
        self.fields['guests'].required = True
        self.fields['special_requests'].required = False
        
        # Устанавливаем максимальное количество гостей
        if self.cottage:
            self.fields['guests'].widget.attrs['max'] = self.cottage.capacity
            self.fields['guests'].widget.attrs['placeholder'] = f'Максимум {self.cottage.capacity} гостей'
    
    def clean_check_in(self):
        """Валидация даты заезда"""
        check_in = self.cleaned_data.get('check_in')
        
        if check_in:
            if check_in < date.today():
                raise ValidationError('Дата заезда не может быть в прошлом')
            
            # Проверяем, что дата не слишком далеко в будущем (максимум 1 год)
            max_date = date.today() + timedelta(days=365)
            if check_in > max_date:
                raise ValidationError('Бронирование возможно максимум на год вперед')
        
        return check_in
    
    def clean_check_out(self):
        """Валидация даты выезда"""
        check_out = self.cleaned_data.get('check_out')
        check_in = self.cleaned_data.get('check_in')
        
        if check_out:
            if check_out <= date.today():
                raise ValidationError('Дата выезда должна быть в будущем')
            
            if check_in and check_out <= check_in:
                raise ValidationError('Дата выезда должна быть позже даты заезда')
            
            # Проверяем максимальную продолжительность (30 дней)
            if check_in:
                duration = (check_out - check_in).days
                if duration > 30:
                    raise ValidationError('Максимальная продолжительность бронирования - 30 дней')
                if duration < 1:
                    raise ValidationError('Минимальная продолжительность - 1 день')
        
        return check_out
    
    def clean_guests(self):
        """Валидация количества гостей"""
        guests = self.cleaned_data.get('guests')
        
        if guests:
            if guests < 1:
                raise ValidationError('Количество гостей должно быть больше 0')
            
            if self.cottage and guests > self.cottage.capacity:
                raise ValidationError(
                    f'Максимальная вместимость коттеджа: {self.cottage.capacity} гостей'
                )
        
        return guests
    
    def clean(self):
        """Общая валидация формы"""
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        
        # Проверяем доступность коттеджа
        if self.cottage and check_in and check_out:
            # Проверяем пересечения с существующими бронированиями
            conflicting_bookings = Booking.objects.filter(
                cottage=self.cottage,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                check_in__lt=check_out,
                check_out__gt=check_in
            )
            
            if conflicting_bookings.exists():
                raise ValidationError(
                    'Выбранные даты недоступны. Пожалуйста, выберите другие даты.'
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Сохранение бронирования"""
        booking = super().save(commit=False)
        
        if self.user:
            booking.user = self.user
        
        if self.cottage:
            booking.cottage = self.cottage
        
        # Автоматический расчет стоимости
        if booking.check_in and booking.check_out and booking.cottage:
            nights = (booking.check_out - booking.check_in).days
            booking.total_price = booking.cottage.price_per_night * nights
        
        # Устанавливаем статус "Ожидает подтверждения"
        booking.status = BookingStatus.PENDING
        
        if commit:
            booking.save()
        
        return booking
