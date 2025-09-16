from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'bookings'

# API маршруты
router = DefaultRouter()
router.register(r'', views.BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('my/', views.MyBookingsView.as_view(), name='my_bookings'),
]
