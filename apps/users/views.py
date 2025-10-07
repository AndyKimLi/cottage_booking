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
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Успешный выход'})
    
    def get(self, request):
        """Выход через GET запрос (для веб-интерфейса)"""
        logout(request)
        from django.shortcuts import redirect
        return redirect('core:index')


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
            return redirect('users:profile')
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
                # Генерируем новый пароль и сразу показываем на странице
                import secrets
                import string
                new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                user.set_password(new_password)
                user.save()

                context = {
                    'form': PasswordChangeForm(),
                    'new_password': new_password,
                    'email_shown': email,
                }
                return render(request, self.template_name, context)
            except User.DoesNotExist:
                form.add_error('email', 'Пользователь с таким email не найден')
        return render(request, self.template_name, {'form': form})


class ChangePasswordView(LoginRequiredMixin, APIView):
    """API для смены пароля без ввода текущего пароля (по активной сессии)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Позволяем либо сгенерировать пароль, либо установить свой (если передан в запросе)
        import json
        import secrets
        import string

        # Надежно читаем данные через DRF парсеры (JSON/Form)
        try:
            data = request.data or {}
        except Exception:
            data = {}

        raw_new_password = (data.get('new_password') or '').strip()
        
        # Отладочная информация
        logger.debug(f"ChangePasswordView: new_password present={bool(raw_new_password)} length={len(raw_new_password)}")

        if raw_new_password:
            # Пользователь задал свой пароль — валидируем минимальные требования
            if len(raw_new_password) < 8:
                return Response({'success': False, 'error': 'Пароль должен быть не короче 8 символов'}, status=status.HTTP_400_BAD_REQUEST)
            new_password = raw_new_password
            echo_password = False
        else:
            # Генерируем одноразовый пароль
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            echo_password = True

        request.user.set_password(new_password)
        request.user.save()

        # Принудительно разлогиниваем пользователя после смены пароля
        logout(request)

        resp = {'success': True, 'logout_required': True}
        if echo_password:
            resp['new_password'] = new_password
        return Response(resp)


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



