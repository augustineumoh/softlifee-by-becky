from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product  = ProductListSerializer(read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model  = CartItem
        fields = ['id', 'product', 'quantity', 'color_variant', 'size_variant', 'subtotal', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items      = CartItemSerializer(many=True, read_only=True)
    total      = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()

    class Meta:
        model  = Cart
        fields = ['id', 'items', 'total', 'item_count', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    product_id    = serializers.IntegerField()
    quantity      = serializers.IntegerField(min_value=1, default=1)
    color_variant = serializers.CharField(required=False, allow_blank=True, default='')
    size_variant  = serializers.CharField(required=False, allow_blank=True, default='')


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
