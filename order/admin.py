from django.contrib import admin
from .models import OrderItem, Order
# Register your models here.
class OrderItemAdmin(admin.ModelAdmin):
    # readonly_fields = ['amount']
    class Meta:
        model = OrderItem
admin.site.register(OrderItem, OrderItemAdmin)

class OrderAdmin(admin.ModelAdmin):
    # readonly_fields = ['total_amt', 'total_qty']
    # fields = ['id', 'vendor', 'order_date', 'status', 'items', 'total_amt']
    list_display = ('id', 'vendor', 'status', 'order_date', 'total_amt')
    
    # def total_amt(self, obj):
    
    class Meta:
        model = Order
admin.site.register(Order, OrderAdmin)