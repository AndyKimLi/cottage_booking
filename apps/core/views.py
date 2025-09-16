from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse


class IndexView(TemplateView):
    """Главная страница"""
    template_name = 'core/index_2.html'


class HealthCheckView(TemplateView):
    """Проверка здоровья приложения"""
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'ok',
            'message': 'Cottage Booking API is running'
        })
