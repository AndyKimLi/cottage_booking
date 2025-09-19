from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from datetime import datetime, date
from .models import Cottage
from .serializers import CottageSerializer, CottageDetailSerializer
from django.views.generic import TemplateView
from django.http import JsonResponse


class CottageViewSet(viewsets.ReadOnlyModelViewSet):
    """API для коттеджей"""
    queryset = Cottage.objects.filter(is_active=True).prefetch_related(
        'images', 'amenities__amenity'
    )
    serializer_class = CottageSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CottageDetailSerializer
        return CottageSerializer
    
    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """Получить изображения коттеджа"""
        cottage = self.get_object()
        images = cottage.images.all().order_by('order')
        return Response([{
            'id': img.id,
            'image': img.image.url,
            'is_primary': img.is_primary,
            'order': img.order
        } for img in images])


class CottageSearchView(APIView):
    """Поиск коттеджей"""
    
    def get(self, request):
        query = request.GET.get('q', '')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        capacity = request.GET.get('capacity')
        
        cottages = Cottage.objects.filter(is_active=True)
        
        if query:
            cottages = cottages.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )
        
        if min_price:
            cottages = cottages.filter(price_per_night__gte=min_price)
        
        if max_price:
            cottages = cottages.filter(price_per_night__lte=max_price)
        
        if capacity:
            cottages = cottages.filter(capacity__gte=capacity)
        
        serializer = CottageSerializer(cottages, many=True)
        return Response(serializer.data)


class CottageAvailabilityView(APIView):
    """Проверка доступности коттеджа"""
    
    def get(self, request, cottage_id):
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        
        if not check_in or not check_out:
            return Response({
                'error': 'Необходимо указать даты заезда и выезда'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Неверный формат даты. Используйте YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if check_in_date >= check_out_date:
            return Response({
                'error': 'Дата заезда должна быть раньше даты выезда'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if check_in_date < date.today():
            return Response({
                'error': 'Дата заезда не может быть в прошлом'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Здесь будет логика проверки доступности
        # Пока возвращаем True
        return Response({
            'available': True,
            'message': 'Коттедж доступен для бронирования'
        })


class cottages_page(TemplateView):
    """HTML-страница со списком коттеджей"""
    template_name = 'cottages/cottages.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем коттеджи из базы данных
        cottages = Cottage.objects.filter(is_active=True).prefetch_related(
            'images', 'amenities__amenity'
        )
        
        # Получаем параметры фильтрации
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        # Применяем фильтры
        if min_price:
            try:
                cottages = cottages.filter(
                    price_per_night__gte=float(min_price)
                )
            except ValueError:
                pass
        
        if max_price:
            try:
                cottages = cottages.filter(
                    price_per_night__lte=float(max_price)
                )
            except ValueError:
                pass
        
        context.update({
            'cottages': cottages,
            'min_price': min_price,
            'max_price': max_price,
        })
        
        return context


class CottageDetailView(TemplateView):
    """Страница детального просмотра коттеджа"""
    template_name = 'cottages/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем ID коттеджа из URL
        cottage_id = kwargs.get('cottage_id')
        
        try:
            # Получаем коттедж с изображениями и удобствами
            cottage = Cottage.objects.prefetch_related(
                'images', 'amenities__amenity'
            ).get(id=cottage_id, is_active=True)
            
            # Получаем изображения, отсортированные по порядку
            images = cottage.images.all().order_by('order', 'id')
            
            # Получаем удобства
            amenities = cottage.amenities.all()
            
            context.update({
                'cottage': cottage,
                'images': images,
                'amenities': amenities,
            })
            
        except Cottage.DoesNotExist:
            from django.http import Http404
            raise Http404(f"Коттедж с ID {cottage_id} не найден или неактивен")
        
        return context


class CottageDebugView(APIView):
    """Отладочное представление для проверки коттеджей"""
    
    def get(self, request):
        # Получаем все коттеджи
        all_cottages = Cottage.objects.all()
        active_cottages = Cottage.objects.filter(is_active=True)
        
        # Формируем данные для отображения
        debug_data = {
            'total_cottages': all_cottages.count(),
            'active_cottages': active_cottages.count(),
            'all_cottages': [
                {
                    'id': cottage.id,
                    'name': cottage.name,
                    'is_active': cottage.is_active,
                    'created_at': cottage.created_at.isoformat(),
                }
                for cottage in all_cottages
            ],
            'active_cottages_list': [
                {
                    'id': cottage.id,
                    'name': cottage.name,
                    'price_per_night': float(cottage.price_per_night),
                    'capacity': cottage.capacity,
                }
                for cottage in active_cottages
            ]
        }
        
        return JsonResponse(
            debug_data,
            json_dumps_params={'ensure_ascii': False, 'indent': 2}
        )