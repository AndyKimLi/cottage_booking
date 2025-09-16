from rest_framework import serializers
from .models import Booking
from apps.cottages.serializers import CottageSerializer


class BookingSerializer(serializers.ModelSerializer):
    """Сериализатор для бронирований"""
    cottage = CottageSerializer(read_only=True)
    cottage_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'cottage', 'cottage_id', 'check_in', 'check_out', 
                 'guests', 'total_price', 'status', 'special_requests', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_price', 'status', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания бронирования"""
    
    class Meta:
        model = Booking
        fields = ['cottage', 'check_in', 'check_out', 'guests', 'special_requests']
    
    def validate(self, attrs):
        check_in = attrs['check_in']
        check_out = attrs['check_out']
        
        if check_in >= check_out:
            raise serializers.ValidationError("Дата заезда должна быть раньше даты выезда")
        
        if check_in < serializers.DateTimeField().to_internal_value('today').date():
            raise serializers.ValidationError("Дата заезда не может быть в прошлом")
        
        return attrs
