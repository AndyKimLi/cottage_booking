from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CallbackRequest


class CallbackRequestForm(forms.ModelForm):   
    TIME_CHOICES = [
        ('', _('Выберите удобное время')),
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
                'placeholder': _('Имя'),
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Фамилия'),
                'required': True
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Отчество (необязательно)')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите номер телефона'),
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Расскажите о ваших пожеланиях...'),
                'rows': 4
            }),
            'cottage': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['cottage'].required = False
        self.fields['email'].required = False
        
        self.fields['cottage'].empty_label = _("Выберите коттедж (необязательно)")