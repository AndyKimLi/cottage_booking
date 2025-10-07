from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
import logging
from .models import CallbackRequest
from .forms import CallbackRequestForm
from apps.cottages.models import Cottage

logger = logging.getLogger(__name__)


class CallbackRequestView(TemplateView):
    """Страница заявки на обратный звонок"""
    template_name = 'leads/callback_request.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем ID коттеджа из параметров (если есть)
        cottage_id = self.request.GET.get('cottage')
        cottage = None
        if cottage_id:
            try:
                cottage = Cottage.objects.get(id=cottage_id, is_active=True)
            except Cottage.DoesNotExist:
                pass
        
        # Создаем форму с предзаполненным коттеджем
        form = CallbackRequestForm()
        if cottage:
            form.fields['cottage'].initial = cottage
        
        context.update({
            'form': form,
            'cottage': cottage,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка формы заявки"""
        form = CallbackRequestForm(request.POST)
        
        if form.is_valid():
            callback_request = form.save()
            
            # Отправляем уведомление в Telegram
            self.send_telegram_notification(callback_request)
            
            messages.success(
                request, 
                'Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.'
            )
            
            # Перенаправляем на страницу успеха
            return redirect('leads:success')
        else:
            # Если форма невалидна, показываем ошибки
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)
    
    def send_telegram_notification(self, callback_request):
        """Отправка уведомления в Telegram через Celery"""
        try:
            from apps.notifications.tasks import send_callback_request_notification
            # Отправляем задачу в очередь RabbitMQ
            send_callback_request_notification.delay(callback_request.id)
            logger.info(f"Callback notification queued for request #{callback_request.id}")
        except Exception as e:
            logger.error(f"Ошибка постановки уведомления в очередь: {e}")
            import traceback
            traceback.print_exc()


class CallbackSuccessView(TemplateView):
    """Страница успешной отправки заявки"""
    template_name = 'leads/success.html'


@method_decorator(csrf_exempt, name='dispatch')
class CallbackRequestAjaxView(TemplateView):
    """AJAX обработка заявки на обратный звонок"""
    
    def post(self, request, *args, **kwargs):
        """Обработка AJAX запроса"""
        form = CallbackRequestForm(request.POST)
        
        if form.is_valid():
            callback_request = form.save()
            
            # Отправляем уведомление в Telegram через Celery
            try:
                from apps.notifications.tasks import send_callback_request_notification
                send_callback_request_notification.delay(callback_request.id)
                logger.info(f"Callback notification queued for request #{callback_request.id}")
            except Exception as e:
                logger.error(f"Ошибка постановки уведомления в очередь: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
