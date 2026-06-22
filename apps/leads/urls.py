from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('callback/', views.CallbackRequestView.as_view(), name='callback_request'),
    path('success/', views.CallbackSuccessView.as_view(), name='success'),
    path('callback-ajax/', views.CallbackRequestAjaxView.as_view(), name='callback_ajax'),
]
