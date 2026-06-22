from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from apps.bookings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('api/v1/', include(('apps.core.urls', 'core'), namespace='core_api')),
    path('api/v1/auth/', include(('apps.users.urls', 'users'), namespace='users_api')),
    path('api/v1/cottages/', include(('apps.cottages.urls', 'cottages'), namespace='cottages_api')),
    path('api/v1/bookings/', include(('apps.bookings.urls', 'bookings'), namespace='bookings_api')),
    path('api/v1/payments/', include(('apps.payments.urls', 'payments'), namespace='payments_api')),
    path('api/v1/contacts/', include(('apps.info.urls', 'info'), namespace='info_api')),
    path('accounts/', include('allauth.urls')),
    path('', include(('apps.core.urls', 'core'), namespace='core_web')),
    path('cottages/', include(('apps.cottages.urls', 'cottages'), namespace='cottages_web')),
    path('bookings/', include(('apps.bookings.web_urls', 'bookings'), namespace='bookings_web')),
    path('users/', include(('apps.users.urls', 'users'), namespace='users_web')),
    path('operator/', include(('apps.operator.urls', 'operator'), namespace='operator_web')),
    path('leads/', include(('apps.leads.urls', 'leads'), namespace='leads_web')),
    path(
        'booking/create/', 
        views.BookingCreateView.as_view(), 
        name='booking_create'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
