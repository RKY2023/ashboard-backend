from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import BankStatement, Transaction, DecryptionKey
from .services import BankStatementProcessorService

User = get_user_model()


class BankStatementModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_bank_statement(self):
        """Test creating a bank statement"""
        statement = BankStatement.objects.create(
            user=self.user,
            original_filename='test.pdf',
            status='pending'
        )
        self.assertEqual(statement.status, 'pending')
        self.assertFalse(statement.is_encrypted)

    def test_bank_statement_str(self):
        """Test string representation"""
        statement = BankStatement.objects.create(
            user=self.user,
            original_filename='test.pdf',
            status='completed'
        )
        expected = 'test.pdf - completed'
        self.assertEqual(str(statement), expected)


class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.statement = BankStatement.objects.create(
            user=self.user,
            original_filename='test.pdf',
            status='completed'
        )

    def test_create_transaction(self):
        """Test creating a transaction"""
        transaction = Transaction.objects.create(
            bank_statement=self.statement,
            user=self.user,
            date='2024-01-01',
            transaction_id_ref='TEST123',
            credit=1000.00,
            debit=0.00,
            balance=5000.00
        )
        self.assertEqual(transaction.credit, 1000.00)
        self.assertEqual(transaction.balance, 5000.00)


class DecryptionKeyModelTest(TestCase):
    def test_create_decryption_key(self):
        """Test creating a decryption key"""
        key = DecryptionKey.objects.create(
            key='testkey123',
            description='Test Key',
            is_active=True
        )
        self.assertTrue(key.is_active)
        self.assertEqual(key.key, 'testkey123')


# Add more tests for views and services as needed
