from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum, Q
from datetime import datetime

from .models import BankStatement, Transaction, DecryptionKey
from .serializers import (
    BankStatementSerializer,
    BankStatementUploadSerializer,
    TransactionSerializer,
    TransactionListSerializer,
    DecryptionKeySerializer
)
from .services import BankStatementProcessorService


class BankStatementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bank statements.
    Supports uploading, processing, and viewing bank statements.
    """
    serializer_class = BankStatementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_encrypted']
    search_fields = ['original_filename']
    ordering_fields = ['created_at', 'processed_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter bank statements by current user"""
        return BankStatement.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload a new bank statement PDF.
        The file will be queued for processing.
        """
        serializer = BankStatementUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']

            # Create bank statement record
            bank_statement = BankStatement.objects.create(
                user=request.user,
                file=file,
                original_filename=file.name,
                status='pending'
            )

            return Response({
                'id': bank_statement.id,
                'message': 'Bank statement uploaded successfully',
                'status': 'pending'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Process a bank statement to extract transactions.
        """
        bank_statement = self.get_object()

        if bank_statement.status == 'processing':
            return Response({
                'error': 'Bank statement is already being processed'
            }, status=status.HTTP_400_BAD_REQUEST)

        if bank_statement.status == 'completed':
            return Response({
                'error': 'Bank statement has already been processed'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Process the statement
        processor = BankStatementProcessorService(bank_statement)
        success = processor.process_statement()

        if success:
            serializer = self.get_serializer(bank_statement)
            return Response({
                'message': 'Bank statement processed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Failed to process bank statement',
                'message': bank_statement.error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Get all transactions for a specific bank statement.
        """
        bank_statement = self.get_object()
        transactions = bank_statement.transactions.all()

        serializer = TransactionListSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics about bank statements and transactions.
        """
        user_statements = self.get_queryset()

        stats = {
            'total_statements': user_statements.count(),
            'pending': user_statements.filter(status='pending').count(),
            'processing': user_statements.filter(status='processing').count(),
            'completed': user_statements.filter(status='completed').count(),
            'failed': user_statements.filter(status='failed').count(),
        }

        return Response(stats)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing transactions.
    Transactions are created automatically when processing bank statements.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['date', 'bank_statement']
    search_fields = ['transaction_id_ref', 'cheque_ref_no']
    ordering_fields = ['date', 'created_at', 'credit', 'debit', 'balance']
    ordering = ['-date', '-created_at']

    def get_queryset(self):
        """Filter transactions by current user"""
        return Transaction.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get transaction summary (total credits, debits, etc.)
        Supports optional date filtering via query params:
        - start_date: YYYY-MM-DD
        - end_date: YYYY-MM-DD
        """
        queryset = self.get_queryset()

        # Apply date filters if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Calculate summary
        summary = queryset.aggregate(
            total_credit=Sum('credit'),
            total_debit=Sum('debit'),
            transaction_count=Count('id')
        )

        # Get latest balance
        latest_transaction = queryset.order_by('-date', '-created_at').first()
        summary['latest_balance'] = latest_transaction.balance if latest_transaction else 0

        return Response(summary)

    @action(detail=False, methods=['get'])
    def by_month(self, request):
        """
        Get transactions grouped by month.
        Requires year parameter (e.g., ?year=2024)
        """
        year = request.query_params.get('year')
        if not year:
            return Response({
                'error': 'Year parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except ValueError:
            return Response({
                'error': 'Invalid year format'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(date__year=year)

        # Group by month
        monthly_data = []
        for month in range(1, 13):
            month_transactions = queryset.filter(date__month=month)
            month_summary = month_transactions.aggregate(
                total_credit=Sum('credit'),
                total_debit=Sum('debit'),
                transaction_count=Count('id')
            )
            month_summary['month'] = month
            month_summary['month_name'] = datetime(year, month, 1).strftime('%B')
            monthly_data.append(month_summary)

        return Response(monthly_data)


class DecryptionKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing PDF decryption keys.
    Only accessible by admin users.
    """
    queryset = DecryptionKey.objects.all()
    serializer_class = DecryptionKeySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering = ['created_at']

    def get_queryset(self):
        """Only admins can view decryption keys"""
        if self.request.user.is_staff:
            return DecryptionKey.objects.all()
        return DecryptionKey.objects.none()


# Import Count for summary action
from django.db.models import Count
