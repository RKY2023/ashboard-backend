from rest_framework import serializers
from .models import BankStatement, Transaction, DecryptionKey


class BankStatementSerializer(serializers.ModelSerializer):
    transaction_count = serializers.SerializerMethodField()

    class Meta:
        model = BankStatement
        fields = [
            'id',
            'file',
            'original_filename',
            'is_encrypted',
            'status',
            'error_message',
            'processed_at',
            'created_at',
            'updated_at',
            'transaction_count'
        ]
        read_only_fields = [
            'is_encrypted',
            'status',
            'error_message',
            'processed_at',
            'created_at',
            'updated_at'
        ]

    def get_transaction_count(self, obj) -> int:
        return obj.transactions.count()

    def create(self, validated_data):
        # Set user from request context
        user = self.context['request'].user
        validated_data['user'] = user

        # Set original filename from uploaded file
        if 'file' in validated_data:
            validated_data['original_filename'] = validated_data['file'].name

        return super().create(validated_data)


class BankStatementUploadSerializer(serializers.Serializer):
    """Serializer for uploading bank statement files"""
    file = serializers.FileField()

    def validate_file(self, value):
        # Validate file extension
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")

        # Validate file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")

        return value


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'bank_statement',
            'date',
            'transaction_id_ref',
            'cheque_ref_no',
            'credit',
            'debit',
            'balance',
            'created_at'
        ]
        read_only_fields = ['bank_statement', 'created_at']


class TransactionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing transactions"""

    class Meta:
        model = Transaction
        fields = [
            'id',
            'date',
            'transaction_id_ref',
            'credit',
            'debit',
            'balance'
        ]


class DecryptionKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = DecryptionKey
        fields = ['id', 'key', 'description', 'is_active', 'created_at']
        extra_kwargs = {
            'key': {'write_only': True}  # Don't expose keys in responses
        }
