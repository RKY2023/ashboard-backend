from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model


class CanViewModelPermission(BasePermission):
    def has_permission(self, request, view):
        # return True
        user = request.user
        # perm = Permission.objects.get(codename='view_product')
        # User = get_user_model()
        # user1 = User.objects.get(username='rky')
        
        # for group in user1.groups.all():
        #     print(group.name, list(group.permissions.values_list("codename", flat=True)))

        #     group.permissions.remo
        # user = request.user
        # user1.user_permissions.remove(perm)
        # user1.save()
        # print(f"User: {user},{user1.groups} Is Authenticated: {user.is_authenticated}", user.has_perm('Product.view_product'), user.has_perm('view_product'))
        # if not user or not user.is_authenticated:
        #     return False

        return user.has_perm('view_product')

class CanAddModelPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
    
class CanLockModelPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        
        # print(f"User: {user}, Is Authenticated: {user.is_authenticated}", user.has_perm('product.lock_product'), user.has_module_perms('product'))
        # return user.has_module_perms('product.lock_product')
        return user.has_perm('product.lock_product')