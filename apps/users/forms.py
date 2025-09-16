from django import forms
from .models import User


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'username'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Делаем поля обязательными
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = False  # Телефон не обязательный
    
    def clean_phone(self):
        """Простая валидация номера телефона"""
        phone = self.cleaned_data.get('phone')
        
        if phone:
            # Убираем все символы кроме цифр и +
            import re
            phone_clean = re.sub(r'[^\d+]', '', phone)
            
            # Проверяем, что номер начинается с + и содержит достаточно цифр
            if not phone_clean.startswith('+'):
                phone_clean = '+7' + phone_clean  # Добавляем +7 по умолчанию
            
            # Проверяем длину (минимум 10 цифр после кода страны)
            digits_only = re.sub(r'[^\d]', '', phone_clean)
            if len(digits_only) < 10:
                raise forms.ValidationError(
                    'Номер телефона должен содержать минимум 10 цифр'
                )
            
            return phone_clean
        
        return phone
    
    def clean_email(self):
        """Валидация email"""
        email = self.cleaned_data.get('email')
        if email:
            # Проверяем, что email уникален (кроме текущего пользователя)
            if self.instance.pk:
                if User.objects.filter(email=email).exclude(
                    pk=self.instance.pk
                ).exists():
                    raise forms.ValidationError(
                        'Пользователь с таким email уже существует'
                    )
            else:
                if User.objects.filter(email=email).exists():
                    raise forms.ValidationError(
                        'Пользователь с таким email уже существует'
                    )
        return email
