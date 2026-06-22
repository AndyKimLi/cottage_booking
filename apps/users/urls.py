from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterPageView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('bookings/', views.MyBookingsPageView.as_view(), name='bookings'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
]
