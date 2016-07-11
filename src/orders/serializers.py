from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'user_checkout',
            'shipping_address',
            'billing_address',
            'subtotal',
            'shipping_total_price',
            'order_price',
        ]

    def get_subtotal(self, obj):
        return obj.cart.subtotal
