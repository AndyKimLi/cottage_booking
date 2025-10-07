from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import logging
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer
from .forms import UserProfileForm, PasswordChangeForm, CustomPasswordResetForm

logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    """Управление профилями пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RegisterPageView(TemplateView):
    """Веб-страница регистрации"""
    template_name = 'users/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:index')
        return render(request, self.template_name)
    
    def post(self, request):
        """Обработка формы регистрации"""
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        middle_name = request.POST.get('middle_name', '')
        phone = request.POST.get('phone', '')
        
        # Валидация
        errors = {}
        
        if not username:
            errors['username'] = 'Имя пользователя обязательно'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Пользователь с таким именем уже существует'
        
        if not email:
            errors['email'] = 'Email обязателен'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Пользователь с таким email уже существует'
        
        if not password1:
            errors['password1'] = 'Пароль обязателен'
        elif len(password1) < 8:
            errors['password1'] = 'Пароль должен содержать минимум 8 символов'
        
        if password1 != password2:
            errors['password2'] = 'Пароли не совпадают'
        
        if errors:
            context = {
                'errors': errors,
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'middle_name': middle_name,
                'phone': phone,
            }
            return render(request, self.template_name, context)
        
        # Создаем пользователя
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            
            # Устанавливаем отчество отдельно, если оно указано
            if middle_name:
                user.middle_name = middle_name
                user.save()
            
            # Автоматически входим пользователя
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Редирект на страницу откуда пришел пользователь или на главную
            next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                return redirect(next_url)
            return redirect('core_web:index')
            
        except Exception as e:
            context = {
                'error': 'Произошла ошибка при регистрации. Попробуйте еще раз.',
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'middle_name': middle_name,
                'phone': phone,
            }
            return render(request, self.template_name, context)

# class RegisterView(APIView):
#     """Регистрация нового пользователя"""
    
#     def post(self, request):
#         serializer = UserRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             return Response({
#                 'message': 'Пользователь успешно зарегистрирован',
#                 'user_id': user.id
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TemplateView):
    """Вход пользователя"""
    template_name = 'users/login.html'
    
    def get(self, request):
        """Отображение страницы входа"""
        if request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('core:index')
        # поддержка возврата на предыдущую страницу через next и Referer
        next_url = request.GET.get('next')
        if not next_url:
            referer = request.META.get('HTTP_REFERER')
            # избегаем зацикливания на странице логина
            if referer and '/users/login' not in referer:
                next_url = referer
        return render(request, self.template_name, {'next': next_url} )
    
    def post(self, request):
        """Обработка формы входа"""
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                # безопасный редирект обратно
                next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
                # в качестве дефолта — главная
                fallback = reverse('core:index')
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                    return redirect(next_url)
                return redirect(fallback)
            else:
                # Неверные учетные данные
                context = {'error': 'Неверный email или пароль'}
                return render(request, self.template_name, context)
        else:
            # Не заполнены поля
            context = {'error': 'Заполните все поля'}
            return render(request, self.template_name, context)

# class LoginView(APIView):
#     """Вход пользователя"""
    
#     def get(self, request):
#         """Отображение страницы входа"""
#         if request.user.is_authenticated:
#             from django.shortcuts import redirect
#             return redirect('core:index')
#         return render(request, 'users/login.html')
    
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')
        
#         if email and password:
#             user = authenticate(request, username=email, password=password)
#             if user:
#                 login(request, user)
#                 return Response({
#                     'message': 'Успешный вход',
#                     'user': UserSerializer(user).data
#                 })
        
#         return Response({
#             'error': 'Неверные учетные данные'
#         }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """Выход пользователя"""
    
    def post(self, request):
        """API выход"""
        if request.user.is_authenticated:
            logout(request)
            return Response({'message': 'Успешный выход'})
        return Response({'error': 'Пользователь не аутентифицирован'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def get(self, request):
        """Выход через GET запрос (для веб-интерфейса)"""
        if request.user.is_authenticated:
            logout(request)
        from django.shortcuts import redirect
        return redirect('core_web:index')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Страница профиля пользователя"""
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = UserProfileForm(instance=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка формы редактирования профиля"""
        form = UserProfileForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            return redirect('users:profile')
        else:
            context = self.get_context_data()
            context['form'] = form
            context['show_edit_form'] = True  # Флаг для показа формы
            return render(request, self.template_name, context)


class PasswordResetRequestView(TemplateView):
    """Страница запроса смены пароля"""
    template_name = 'users/password_reset_request.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users_web:profile')
        form = PasswordChangeForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Защита: запрет восстановления пароля этим способом для персонала и администраторов
                if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
                    form.add_error('email', 'Этот способ восстановления недоступен для этой учетной записи')
                    return render(request, self.template_name, {'form': form})
                
                # Генерируем новый пароль
                import secrets
                import string
                new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                user.set_password(new_password)
                user.save()

                # Отправляем письмо с новым паролем
                from django.core.mail import send_mail
                from django.template.loader import render_to_string
                
                try:
                    html_message = render_to_string('emails/password_reset.html', {
                        'user': user,
                        'new_password': new_password
                    })
                    
                    send_mail(
                        subject='Новый пароль - Kamchatka Village',
                        message=f'Ваш новый пароль: {new_password}',
                        from_email=None,  # Использует DEFAULT_FROM_EMAIL
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    
                    messages.success(request, f'Новый пароль отправлен на email {email}. Проверьте почту и войдите в систему.')
                    logger.info(f"Password reset email sent to {email}")
                    
                except Exception as e:
                    logger.error(f"Failed to send password reset email to {email}: {str(e)}")
                    messages.error(request, 'Ошибка отправки письма. Попробуйте позже или обратитесь в поддержку.')
                    return render(request, self.template_name, {'form': form})

                # Показываем страницу успеха
                context = {
                    'form': PasswordChangeForm(),
                    'email_sent': True,
                    'email_shown': email,
                }
                return render(request, self.template_name, context)
                
            except User.DoesNotExist:
                form.add_error('email', 'Пользователь с таким email не найден')
        return render(request, self.template_name, {'form': form})


class ChangePasswordView(LoginRequiredMixin, APIView):
    """API для смены пароля с проверкой текущего пароля"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.contrib.auth import authenticate
        
        # Читаем данные
        try:
            data = request.data or {}
        except Exception:
            data = {}

        current_password = (data.get('current_password') or '').strip()
        new_password = (data.get('new_password') or '').strip()
        
        # Валидация
        if not current_password:
            return Response({'success': False, 'error': 'Введите текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not new_password:
            return Response({'success': False, 'error': 'Введите новый пароль'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({'success': False, 'error': 'Новый пароль должен быть не короче 8 символов'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем текущий пароль
        user = authenticate(request, username=request.user.email, password=current_password)
        if not user or user != request.user:
            return Response({'success': False, 'error': 'Неверный текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Устанавливаем новый пароль
        request.user.set_password(new_password)
        request.user.save()
        
        logger.info(f"Password changed for user {request.user.email}")
        
        return Response({'success': True})


class MyBookingsPageView(LoginRequiredMixin, TemplateView):
    """Страница бронирований пользователя"""
    template_name = 'users/bookings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем бронирования пользователя (исключаем отмененные)
        from apps.bookings.models import Booking
        bookings = Booking.objects.filter(
            user=self.request.user
        ).exclude(
            status='cancelled'
        ).select_related('cottage').prefetch_related(
            'cottage__amenities__amenity'
        ).order_by('-created_at')
        
        context['bookings'] = bookings
        return context



