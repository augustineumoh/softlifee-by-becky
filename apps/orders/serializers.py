from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_price',
            'product_image', 'color_variant', 'quantity', 'subtotal'
        ]
        read_only_fields = ['subtotal']


class OrderItemCreateSerializer(serializers.Serializer):
    product_id    = serializers.IntegerField()
    quantity      = serializers.IntegerField(min_value=1)
    color_variant = serializers.CharField(required=False, allow_blank=True)


class OrderCreateSerializer(serializers.Serializer):
    # Customer info
    customer_name  = serializers.CharField(max_length=200)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20)

    # Delivery
    delivery_address = serializers.CharField()
    delivery_city    = serializers.CharField(max_length=100)
    delivery_state   = serializers.CharField(max_length=100)
    delivery_notes   = serializers.CharField(required=False, allow_blank=True)

    # Payment
    payment_method = serializers.ChoiceField(choices=['card', 'transfer', 'ussd', 'pod'])

    # Items
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('At least one item is required.')
        return items


class OrderSerializer(serializers.ModelSerializer):
    items          = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(
        source='get_payment_status_display', read_only=True
    )

    class Meta:
        model  = Order
        fields = [
            'id', 'order_number', 'customer_name', 'customer_email',
            'customer_phone', 'delivery_address', 'delivery_city',
            'delivery_state', 'delivery_notes', 'subtotal', 'delivery_fee',
            'total', 'status', 'status_display', 'payment_method',
            'payment_status', 'payment_status_display', 'paystack_ref',
            'paid_at', 'items', 'created_at',
        ]