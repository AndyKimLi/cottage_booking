from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""
    
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'status', 'payment_method', 
                 'transaction_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
