from django.contrib import admin
from .models import OrderItem, Order
# Register your models here.
class OrderItemAdmin(admin.ModelAdmin):
    # readonly_fields = ['amount']
    class Meta:
        model = OrderItem
admin.site.register(OrderItem, OrderItemAdmin)

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['total_amt', 'total_qty']
    
    class Meta:
        model = Order
admin.site.register(Order, OrderAdmin)