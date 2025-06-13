from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status, filters, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.decorators import api_view, permission_classes, action
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from .models import Payment
from .serializers import PaymentSerializer

import csv
import datetime
import logging

User = get_user_model()

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(pagination.PageNumberPagination):
    """
    Standard pagination for payment views.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class PaymentListCreateView(generics.ListCreateAPIView):
    """
    List all payments for the authenticated user or create a new payment.
    Supports filtering, searching, and ordering.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'reference', 'method']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.filter(user=user)
        # Optional filtering by status or date
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a payment for the authenticated user.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(user=user)

    def delete(self, request, *args, **kwargs):
        payment = self.get_object()
        if payment.status == 'processed':
            return Response({'error': 'Cannot delete processed payment.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().delete(request, *args, **kwargs)

class ProcessPaymentView(APIView):
    """
    Custom endpoint to process a payment (simulate payment gateway).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        if not payment_id:
            return Response({'error': 'payment_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        if payment.status == 'processed':
            return Response({'error': 'Payment already processed.'}, status=status.HTTP_400_BAD_REQUEST)
        # ... process payment logic ...
        payment.status = 'processed'
        payment.processed_at = datetime.datetime.now()
        payment.save()
        logger.info(f"Payment {payment.id} processed for user {request.user.id}")
        return Response({'status': 'Payment processed'}, status=status.HTTP_200_OK)

class PaymentReportView(APIView):
    """
    Generate a summary report of payments for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        total_paid = Payment.objects.filter(user=user, status='processed').aggregate(total=Sum('amount'))['total'] or 0
        count = Payment.objects.filter(user=user).count()
        pending = Payment.objects.filter(user=user, status='pending').aggregate(total=Sum('amount'))['total'] or 0
        failed = Payment.objects.filter(user=user, status='failed').aggregate(total=Sum('amount'))['total'] or 0
        return Response({
            'total_paid': total_paid,
            'pending_amount': pending,
            'failed_amount': failed,
            'payment_count': count,
        })

class PaymentExportCSVView(APIView):
    """
    Export all payments for the authenticated user as a CSV file.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        payments = Payment.objects.filter(user=user)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Amount', 'Status', 'Method', 'Reference', 'Created At'])
        for payment in payments:
            writer.writerow([
                payment.id,
                payment.amount,
                payment.status,
                payment.method,
                payment.reference,
                payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        return response

class AdminPaymentListView(generics.ListAPIView):
    """
    Admin-only: List all payments in the system.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'status', 'reference', 'method']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

class AdminPaymentReportView(APIView):
    """
    Admin-only: Generate a summary report of all payments in the system.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        total_paid = Payment.objects.filter(status='processed').aggregate(total=Sum('amount'))['total'] or 0
        total_pending = Payment.objects.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
        total_failed = Payment.objects.filter(status='failed').aggregate(total=Sum('amount'))['total'] or 0
        count = Payment.objects.count()
        processed_count = Payment.objects.filter(status='processed').count()
        return Response({
            'total_paid': total_paid,
            'total_pending': total_pending,
            'total_failed': total_failed,
            'payment_count': count,
            'processed_count': processed_count,
        })

class AdminPaymentExportCSVView(APIView):
    """
    Admin-only: Export all payments in the system as a CSV file.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        payments = Payment.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="all_payments.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'User', 'Amount', 'Status', 'Method', 'Reference', 'Created At'])
        for payment in payments:
            writer.writerow([
                payment.id,
                payment.user.username if payment.user else '',
                payment.amount,
                payment.status,
                payment.method,
                payment.reference,
                payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_status_choices(request):
    """
    Return available payment status choices.
    """
    # Assuming Payment.STATUS_CHOICES is a list of tuples
    return Response({'choices': getattr(Payment, 'STATUS_CHOICES', [])})

# ...existing code...
