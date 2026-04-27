from rest_framework import serializers
from .models import ReturnRequest, ReturnItem, OrderItem


class ReturnItemSerializer(serializers.ModelSerializer):
    product_name  = serializers.CharField(source='order_item.product_name', read_only=True)
    product_image = serializers.CharField(source='order_item.product_image', read_only=True)

    class Meta:
        model  = ReturnItem
        fields = ['id', 'order_item', 'product_name', 'product_image', 'quantity']


class ReturnItemCreateSerializer(serializers.Serializer):
    order_item_id = serializers.IntegerField()
    quantity      = serializers.IntegerField(min_value=1)


class ReturnRequestSerializer(serializers.ModelSerializer):
    items          = ReturnItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    order_number   = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model  = ReturnRequest
        fields = [
            'id', 'return_number', 'order', 'order_number', 'reason', 'reason_display',
            'description', 'status', 'status_display', 'admin_notes',
            'refund_amount', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'admin_notes', 'refund_amount', 'return_number']


class ReturnRequestCreateSerializer(serializers.Serializer):
    order_id    = serializers.IntegerField()
    reason      = serializers.ChoiceField(choices=ReturnRequest.REASON_CHOICES)
    description = serializers.CharField()
    items       = ReturnItemCreateSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('At least one item is required.')
        return items


class AdminReturnUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ReturnRequest
        fields = ['status', 'admin_notes', 'refund_amount']
