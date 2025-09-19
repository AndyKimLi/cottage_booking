from django import forms
from .models import CallbackRequest


class CallbackRequestForm(forms.ModelForm):
    """Форма заявки на обратный звонок"""
    
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
            'preferred_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: с 10:00 до 18:00'
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
        
