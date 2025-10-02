from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BankStatementViewSet, TransactionViewSet, DecryptionKeyViewSet

router = DefaultRouter()
router.register(r'bank-statements', BankStatementViewSet, basename='bank-statement')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'decryption-keys', DecryptionKeyViewSet, basename='decryption-key')

urlpatterns = [
    path('', include(router.urls)),
]
