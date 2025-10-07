from django import forms
from .models import CallbackRequest


class CallbackRequestForm(forms.ModelForm):
    """Форма заявки на обратный звонок"""
    
    # Временные интервалы для выбора
    TIME_CHOICES = [
        ('', 'Выберите удобное время'),
        ('09:00 - 09:30', '09:00 - 09:30'),
        ('09:30 - 10:00', '09:30 - 10:00'),
        ('10:00 - 10:30', '10:00 - 10:30'),
        ('10:30 - 11:00', '10:30 - 11:00'),
        ('11:00 - 11:30', '11:00 - 11:30'),
        ('11:30 - 12:00', '11:30 - 12:00'),
        ('12:00 - 12:30', '12:00 - 12:30'),
        ('12:30 - 13:00', '12:30 - 13:00'),
        ('13:00 - 13:30', '13:00 - 13:30'),
        ('13:30 - 14:00', '13:30 - 14:00'),
        ('14:00 - 14:30', '14:00 - 14:30'),
        ('14:30 - 15:00', '14:30 - 15:00'),
        ('15:00 - 15:30', '15:00 - 15:30'),
        ('15:30 - 16:00', '15:30 - 16:00'),
        ('16:00 - 16:30', '16:00 - 16:30'),
        ('16:30 - 17:00', '16:30 - 17:00'),
        ('17:00 - 17:30', '17:00 - 17:30'),
        ('17:30 - 18:00', '17:30 - 18:00'),
        ('18:00 - 18:30', '18:00 - 18:30'),
        ('18:30 - 19:00', '18:30 - 19:00'),
        ('19:00 - 19:30', '19:00 - 19:30'),
        ('19:30 - 20:00', '19:30 - 20:00'),
    ]
    
    preferred_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = CallbackRequest
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'message', 'preferred_time', 'cottage']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия',
                'required': True
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Отчество (необязательно)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите номер телефона',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Расскажите о ваших пожеланиях...',
                'rows': 4
            }),
            'cottage': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Делаем поле коттеджа необязательным
        self.fields['cottage'].required = False
        self.fields['email'].required = False
        
        # Добавляем пустой выбор для коттеджа
        self.fields['cottage'].empty_label = "Выберите коттедж (необязательно)"
        
