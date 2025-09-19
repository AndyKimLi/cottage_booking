from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer
from .forms import UserProfileForm


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
            
            # Автоматически входим пользователя
            from django.contrib.auth import login
            login(request, user)
            
            return redirect('core:index')
            
        except Exception as e:
            context = {
                'error': 'Произошла ошибка при регистрации. Попробуйте еще раз.',
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
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
        return render(request, self.template_name)
    
    def post(self, request):
        """Обработка формы входа"""
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                from django.shortcuts import redirect
                return redirect('core:index')
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



