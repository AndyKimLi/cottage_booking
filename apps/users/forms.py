from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext_lazy as _
from .models import User


class UserProfileForm(forms.ModelForm):   
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'middle_name', 'email', 'phone',
            'date_of_birth', 'username'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите имя')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите фамилию')
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите отчество (необязательно)')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите email')
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
                'placeholder': _('Введите имя пользователя')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = False
    
    def clean_phone(self):
        """Простая валидация номера телефона"""
        phone = self.cleaned_data.get('phone')
        
        if phone:
            import re
            phone_clean = re.sub(r'[^\d+]', '', phone)
            
            if not phone_clean.startswith('+'):
                phone_clean = '+7' + phone_clean
            
            digits_only = re.sub(r'[^\d]', '', phone_clean)
            if len(digits_only) < 10:
                raise forms.ValidationError(
                    _('Номер телефона должен содержать минимум 10 цифр')
                )
            
            return phone_clean
        
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if self.instance.pk:
                if User.objects.filter(email=email).exclude(
                    pk=self.instance.pk
                ).exists():
                    raise forms.ValidationError(
                        _('Пользователь с таким email уже существует')
                    )
            else:
                if User.objects.filter(email=email).exists():
                    raise forms.ValidationError(
                        _('Пользователь с таким email уже существует')
                    )
        return email


class PasswordChangeForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите ваш email')
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Пользователь с таким email не найден'))
        return email


class CustomPasswordResetForm(PasswordResetForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Введите ваш email')
        })