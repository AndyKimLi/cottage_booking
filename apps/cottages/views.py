from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.core.cache import cache
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
    
    def get_queryset(self):
        """Оптимизированный queryset с кэшированием"""
        cache_key = f"cottages_list_{hash(frozenset(self.request.GET.items()))}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        queryset = super().get_queryset()
        
        # Применяем фильтры
        is_available = self.request.query_params.get('is_available')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        min_guests = self.request.query_params.get('min_guests')
        
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        if min_guests:
            queryset = queryset.filter(max_guests__gte=min_guests)
        
        # Кэшируем на 5 минут (не кэшируем QuerySet, только результаты)
        # cache.set(cache_key, queryset, 300)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CottageDetailSerializer
        return CottageSerializer
    
    def list(self, request, *args, **kwargs):
        """Список коттеджей с кэшированием"""
        cache_key = 'cottages_list_api'
        cottages_data = cache.get(cache_key)
        
        if cottages_data is None:
            cottages = self.get_queryset()
            serializer = self.get_serializer(cottages, many=True)
            cottages_data = serializer.data
            cache.set(cache_key, cottages_data, 300)
        
        return Response(cottages_data)
    
    def retrieve(self, request, *args, **kwargs):
        """Детали коттеджа с кэшированием"""
        cottage_id = kwargs.get('pk')
        cache_key = f'cottage_detail_{cottage_id}'
        cottage_data = cache.get(cache_key)
        
        if cottage_data is None:
            cottage = self.get_object()
            serializer = self.get_serializer(cottage)
            cottage_data = serializer.data
            # cache.set(cache_key, cottage_data, 600)
        
        return Response(cottage_data)
    
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
        
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        cache_key = f'cottages_html_{min_price}_{max_price}'
        cottage_ids = cache.get(cache_key)
        
        if cottage_ids is None:
            # Получаем коттеджи из БД
            cottages = Cottage.objects.filter(is_active=True).prefetch_related(
                'images', 'amenities__amenity'
            )
            
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
            
            # Кэшируем только ID коттеджей (сериализуемые)
            cottage_ids = list(cottages.values_list('id', flat=True))
            cache.set(cache_key, cottage_ids, 300)
        
        # Получаем объекты коттеджей по ID
        cottages = Cottage.objects.filter(
            id__in=cottage_ids, 
            is_active=True
        ).prefetch_related('images', 'amenities__amenity')
        
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
        
        # Кэшируем детали коттеджа
        cache_key = f'cottage_detail_html_{cottage_id}'
        cottage_data = cache.get(cache_key)
        
        if cottage_data is None:
            try:
                # Получаем коттедж с изображениями и удобствами
                cottage = Cottage.objects.prefetch_related(
                    'images', 'amenities__amenity'
                ).get(id=cottage_id, is_active=True)
                
                # Получаем изображения, отсортированные по порядку
                images = cottage.images.all().order_by('order', 'id')
                
                # Получаем удобства
                amenities = cottage.amenities.all()
                
                cottage_data = {
                    "cottage_id": cottage.id,
                    'cottage': cottage,
                    'images': list(images),  # Конвертируем QuerySet в список
                    'amenities': list(amenities),  # Конвертируем QuerySet в список
                }
                
                # cache.set(cache_key, cottage_data, 600)
                
            except Cottage.DoesNotExist:
                from django.http import Http404
                raise Http404(f"Коттедж с ID {cottage_id} не найден или неактивен")
        
        context.update(cottage_data)
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