"""
URL configuration for cottage_booking project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.bookings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # API маршруты
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/cottages/', include('apps.cottages.urls')),
    path('api/v1/bookings/', include('apps.bookings.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/contacts/', include('apps.info.urls')),
    path('accounts/', include('allauth.urls')),
    # Веб-маршруты
    path('', include('apps.core.urls')),
    path('cottages/', include('apps.cottages.urls')),
    path('bookings/', include('apps.bookings.web_urls')),
    path('users/', include('apps.users.urls')),
    path('operator/', include('apps.operator.urls')),
    # Прямые веб-маршруты для бронирований
    path(
        'booking/create/', 
        views.BookingCreateView.as_view(), 
        name='booking_create'
    ),
]

# Статические и медиа файлы для разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
