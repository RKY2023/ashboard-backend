from rest_framework import serializers
from .models import BankStatement, Transaction, DecryptionKey, Category, Expense


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


class CategorySerializer(serializers.ModelSerializer):
    expense_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'keywords',
            'icon',
            'color',
            'is_default',
            'created_at',
            'updated_at',
            'expense_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_default']

    def get_expense_count(self, obj) -> int:
        """Get count of expenses in this category"""
        return obj.expenses.count()

    def create(self, validated_data):
        """Set user from request context"""
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['is_default'] = False
        return super().create(validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    transaction_ref = serializers.CharField(source='transaction.transaction_id_ref', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id',
            'transaction',
            'category',
            'category_name',
            'category_icon',
            'category_color',
            'amount',
            'date',
            'description',
            'notes',
            'is_auto_categorized',
            'is_recurring',
            'tags',
            'transaction_ref',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'transaction',
            'amount',
            'date',
            'description',
            'is_auto_categorized',
            'created_at',
            'updated_at'
        ]


class ExpenseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing expenses"""
    category_id = serializers.IntegerField(source='category.id', read_only=True, allow_null=True)
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            'id',
            'amount',
            'description',
            'category_id',
            'date',
            'created_at',
            'updated_at',
            'categories'
        ]

    def get_categories(self, obj):
        """Return nested category object"""
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'color': obj.category.color
            }
        return None


class ExpenseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating expense category and notes"""

    class Meta:
        model = Expense
        fields = ['category', 'notes', 'is_recurring', 'tags']

    def update(self, instance, validated_data):
        """When category is manually updated, set is_auto_categorized to False"""
        if 'category' in validated_data:
            instance.is_auto_categorized = False
        return super().update(instance, validated_data)
