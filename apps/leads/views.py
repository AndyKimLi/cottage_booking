from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from .models import CallbackRequest
from .forms import CallbackRequestForm
from apps.cottages.models import Cottage


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
        """Отправка уведомления в Telegram"""
        try:
            print(f"Попытка отправить уведомление для заявки #{callback_request.id}")
            import asyncio
            from apps.telegram_bot.bot import send_callback_notification
            
            # Запускаем асинхронную функцию
            result = asyncio.run(send_callback_notification(callback_request))
            print(f"Результат отправки уведомления: {result}")
        except Exception as e:
            print(f"Ошибка отправки уведомления в Telegram: {e}")
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
            
            # Отправляем уведомление в Telegram
            try:
                from apps.telegram_bot.bot import send_callback_notification
                send_callback_notification(callback_request)
            except Exception as e:
                print(f"Ошибка отправки уведомления в Telegram: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
