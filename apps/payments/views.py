from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """API для платежей"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking__user=self.request.user)


class PaymentWebhookView(APIView):
    """Webhook для обработки платежей"""
    
    def post(self, request):
        # Здесь будет логика обработки webhook от платежной системы
        # Например, Stripe, PayPal и т.д.
        return Response({'status': 'ok'})
