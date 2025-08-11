from rest_framework import serializers
from .models import OrderItem, Order
from product.views import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    # amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    # product = ProductSerializer(read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    selling_price = serializers.DecimalField(
        source='product.selling_price',
        read_only=True,
        decimal_places=2,
        max_digits=10
    )
    

    class Meta:
        model = OrderItem
        # fields = ['product', 'quantity', 'amount']
        # fields = '__all__'
        exclude = ['order']
        # read_only_fields = ['amount']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amt = serializers.DecimalField(
        # source='total_amt',
        read_only=True,
        decimal_places=2,
        max_digits=10
    )
    
    class Meta:
        model = Order
        fields = ['id', 'order_date', 'vendor', 'status', 'items', 'total_amt']
    
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