from rest_framework import serializers
from .models import OrderItem, Order

class OrderItemSerializer(serializers.ModelSerializer):
    # amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        # fields = ['product', 'quantity', 'amount']
        fields = '__all__'
        # read_only_fields = ['amount']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_date', 'vendor', 'status', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        total_qty = 0
        total_amt = 0.00
        
        for item_data in items_data:
            # total_amt += item_data['amount']
            total_qty += item_data['quantity']
            OrderItemSerializer.create(OrderItemSerializer(), validated_data=item_data)
        
        order.total_qty = total_qty
        order.total_amt = total_amt
        order.save()
        return order