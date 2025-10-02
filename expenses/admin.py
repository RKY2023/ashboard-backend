from django.contrib import admin
from .models import BankStatement, Transaction, DecryptionKey


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_filename', 'user', 'status', 'is_encrypted', 'created_at']
    list_filter = ['status', 'is_encrypted', 'created_at']
    search_fields = ['original_filename', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'processed_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'transaction_id_ref', 'credit', 'debit', 'balance', 'user']
    list_filter = ['date', 'user']
    search_fields = ['transaction_id_ref', 'cheque_ref_no']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'


@admin.register(DecryptionKey)
class DecryptionKeyAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['description']
