from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

router = DefaultRouter()
router.register(r'', views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', views.PaymentWebhookView.as_view(), name='webhook'),
]
