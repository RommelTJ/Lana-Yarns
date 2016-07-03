from __future__ import unicode_literals

from django.conf import settings
from django.db.models.signals import pre_save, post_save
from decimal import Decimal

from .models import UserCheckout, Order


def update_braintree_id(sender, instance, created, *args, **kwargs):
    instance.get_braintree_id()

post_save.connect(update_braintree_id, sender=UserCheckout)


def order_pre_save(sender, instance, *args, **kwargs):
    shipping_total_price = Decimal(instance.shipping_total_price)
    cart_total = Decimal(instance.cart.total)
    order_total = shipping_total_price + cart_total
    instance.order_price = '%.2f' % (order_total)

pre_save.connect(order_pre_save, sender=Order)