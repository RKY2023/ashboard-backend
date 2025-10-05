from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BankStatementViewSet,
    TransactionViewSet,
    DecryptionKeyViewSet,
    CategoryViewSet,
    ExpenseViewSet
)

router = DefaultRouter()
router.register(r'bank-statements', BankStatementViewSet, basename='bank-statement')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'decryption-keys', DecryptionKeyViewSet, basename='decryption-key')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]
