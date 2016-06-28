from __future__ import unicode_literals

from django.db.models.signals import pre_save
from decimal import Decimal

from .models import Order


def order_pre_save(sender, instance, *args, **kwargs):
    shipping_total_price = Decimal(instance.shipping_total_price)
    cart_total = Decimal(instance.cart.total)
    order_total = shipping_total_price + cart_total
    instance.order_price = '%.2f' % (order_total)


pre_save.connect(order_pre_save, sender=Order)