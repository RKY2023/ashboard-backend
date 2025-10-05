from django.contrib import admin
from .models import BankStatement, Transaction, DecryptionKey, Category, Expense


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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_default', 'user', 'icon', 'color', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'icon', 'color', 'is_default', 'user')
        }),
        ('Keywords', {
            'fields': ('keywords',),
            'description': 'JSON list of keywords to match in transaction references'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'description', 'amount', 'category', 'user', 'is_auto_categorized', 'is_recurring']
    list_filter = ['date', 'category', 'is_auto_categorized', 'is_recurring', 'user']
    search_fields = ['description', 'notes', 'transaction__transaction_id_ref']
    readonly_fields = ['transaction', 'amount', 'date', 'description', 'is_auto_categorized', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    fieldsets = (
        ('Transaction Info', {
            'fields': ('transaction', 'user', 'date', 'amount', 'description')
        }),
        ('Categorization', {
            'fields': ('category', 'is_auto_categorized')
        }),
        ('User Notes', {
            'fields': ('notes', 'is_recurring', 'tags')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
