from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/', views.BookingCreateView.as_view(), name='create'),
    path(
        '<int:booking_id>/', 
        views.BookingDetailView.as_view(), 
        name='detail'
    ),
    path(
        '<int:booking_id>/edit/', 
        views.BookingEditView.as_view(), 
        name='edit'
    ),
    path(
        '<int:booking_id>/cancel/', 
        views.CancelBookingView.as_view(), 
        name='cancel'
    ),
]
