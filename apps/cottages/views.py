from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from django_redis.exceptions import ConnectionInterrupted
from datetime import datetime, date
from .models import Cottage
from .serializers import CottageSerializer, CottageDetailSerializer
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)


class CottageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cottage.objects.filter(is_active=True).prefetch_related(
        'images', 'amenities__amenity'
    )
    serializer_class = CottageSerializer
    
    def get_queryset(self):
        cache_key = f"cottages_list_{hash(frozenset(self.request.GET.items()))}"
        cached_result = None
        
        try:
            cached_result = cache.get(cache_key)
        except (ConnectionInterrupted, InvalidCacheBackendError) as e:
            logger.warning(f"Cache read error: {e}")
        
        if cached_result is not None:
            return cached_result
        
        queryset = super().get_queryset()
        
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
        

        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CottageDetailSerializer
        return CottageSerializer
    
    def list(self, request, *args, **kwargs):
        cache_key = 'cottages_list_api'
        cottages_data = None
        
        try:
            cottages_data = cache.get(cache_key)
        except (ConnectionInterrupted, InvalidCacheBackendError) as e:
            logger.warning(f"Cache read error: {e}")
        
        if cottages_data is None:
            cottages = self.get_queryset()
            serializer = self.get_serializer(cottages, many=True)
            cottages_data = serializer.data
            try:
                cache.set(cache_key, cottages_data, 300)
            except (ConnectionInterrupted, InvalidCacheBackendError) as e:
                logger.warning(f"Cache write error: {e}")
        
        return Response(cottages_data)
    
    def retrieve(self, request, *args, **kwargs):
        """Детали коттеджа с кэшированием"""
        cottage_id = kwargs.get('pk')
        cache_key = f'cottage_detail_{cottage_id}'
        cottage_data = None
        
        try:
            cottage_data = cache.get(cache_key)
        except (ConnectionInterrupted, InvalidCacheBackendError) as e:
            logger.warning(f"Cache read error: {e}")
        
        if cottage_data is None:
            cottage = self.get_object()
            serializer = self.get_serializer(cottage)
            cottage_data = serializer.data
            try:
                cache.set(cache_key, cottage_data, 600)
            except (ConnectionInterrupted, InvalidCacheBackendError) as e:
                logger.warning(f"Cache write error: {e}")
        
        return Response(cottage_data)
    
    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        cottage = self.get_object()
        images = cottage.images.all().order_by('order')
        return Response([{
            'id': img.id,
            'image': img.image.url,
            'is_primary': img.is_primary,
            'order': img.order
        } for img in images])


class CottageSearchView(APIView):
    
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
    def get(self, request, cottage_id):
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        
        if not check_in or not check_out:
            return Response({
                'error': _('Check-in and check-out dates must be specified')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': _('Invalid date format. Use YYYY-MM-DD')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if check_in_date >= check_out_date:
            return Response({
                'error': _('Check-in date must be earlier than check-out date')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if check_in_date < date.today():
            return Response({
                'error': _('Check-in date cannot be in the past')
            }, status=status.HTTP_400_BAD_REQUEST)
        

        return Response({
            'available': True,
            'message': _('Cottage is available for booking')
        })


class cottages_page(TemplateView):
    template_name = 'cottages/cottages.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        cache_key = f'cottages_html_{min_price}_{max_price}'
        cottage_ids = None
        
        try:
            cottage_ids = cache.get(cache_key)
        except (ConnectionInterrupted, InvalidCacheBackendError) as e:
            logger.warning(f"Cache read error: {e}")
        
        if cottage_ids is None:
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
            
            cottage_ids = list(cottages.values_list('id', flat=True))
            try:
                cache.set(cache_key, cottage_ids, 300)
            except (ConnectionInterrupted, InvalidCacheBackendError) as e:
                logger.warning(f"Cache write error: {e}")
        
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
    template_name = 'cottages/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        cottage_id = kwargs.get('cottage_id')
        
        cache_key = f'cottage_detail_html_{cottage_id}'
        cottage_data = None
        
        try:
            cottage_data = cache.get(cache_key)
        except (ConnectionInterrupted, InvalidCacheBackendError) as e:
            logger.warning(f"Cache read error: {e}")
        
        if cottage_data is None:
            try:
                cottage = Cottage.objects.prefetch_related(
                    'images', 'amenities__amenity'
                ).get(id=cottage_id, is_active=True)
                
                images = cottage.images.all().order_by('order', 'id')
                
                amenities = cottage.amenities.all()
                
                cottage_data = {
                    "cottage_id": cottage.id,
                    'cottage': cottage,
                    'images': list(images),
                    'amenities': list(amenities),
                }
                
                # cache.set(cache_key, cottage_data, 600)
                
            except Cottage.DoesNotExist:
                from django.http import Http404
                raise Http404(_("Cottage with ID %(id)s not found or inactive") % {'id': cottage_id})
        
        context.update(cottage_data)
        return context


class CottageDebugView(APIView):
    def get(self, request):
        all_cottages = Cottage.objects.all()
        active_cottages = Cottage.objects.filter(is_active=True)
        
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