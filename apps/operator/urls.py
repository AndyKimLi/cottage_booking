from django.urls import path
from . import views

app_name = 'operator'

urlpatterns = [
    path('', views.operator_dashboard, name='dashboard'),
    path('quick-booking/', views.quick_booking_view, name='quick_booking'),
    path('api/cottage/<int:cottage_id>/availability/', views.get_cottage_availability, name='cottage_availability'),
    path('api/change-booking-status/', 
         views.change_booking_status, 
         name='change_booking_status'),
    path('api/change-callback-status/', 
         views.change_callback_status, 
         name='change_callback_status'),
]
