from django.db import models
from django.conf import settings


class BankStatement(models.Model):
    """Model to store uploaded bank statement PDFs"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='bank_statements/')
    original_filename = models.CharField(max_length=255)
    is_encrypted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_filename} - {self.status}"


class Transaction(models.Model):
    """Model to store parsed bank transactions"""

    bank_statement = models.ForeignKey(
        BankStatement,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    transaction_id_ref = models.CharField(max_length=500)
    cheque_ref_no = models.CharField(max_length=100, blank=True, null=True)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.date} - {self.transaction_id_ref[:50]}"


class DecryptionKey(models.Model):
    """Model to store PDF decryption keys"""

    key = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Key {self.id} - {self.description or 'No description'}"


class Category(models.Model):
    """Model to store expense categories with keyword matching"""

    name = models.CharField(max_length=100)
    keywords = models.JSONField(
        default=list,
        help_text="List of keywords to match in transaction references"
    )
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon/emoji for UI")
    color = models.CharField(max_length=7, blank=True, null=True, help_text="Hex color code (e.g., #FF5733)")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="User who owns this category (null for default categories)"
    )
    is_default = models.BooleanField(default=False, help_text="System-wide default category")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['is_default']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.name} ({'Default' if self.is_default else 'Custom'})"


class Expense(models.Model):
    """Model to store expenses extracted from transactions"""

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='expense',
        help_text="Linked transaction (debit only)"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        help_text="Expense category"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Same as transaction debit")
    date = models.DateField(help_text="Same as transaction date")
    description = models.TextField(help_text="Cleaned up transaction reference")
    notes = models.TextField(blank=True, null=True, help_text="User's custom notes")
    is_auto_categorized = models.BooleanField(default=False, help_text="Auto-categorized or manually set")
    is_recurring = models.BooleanField(default=False, help_text="Mark if recurring expense")
    tags = models.JSONField(default=list, help_text="Custom tags for filtering")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['category']),
            models.Index(fields=['date']),
            models.Index(fields=['is_recurring']),
        ]

    def __str__(self):
        return f"{self.date} - {self.description[:50]} - ₹{self.amount}"
