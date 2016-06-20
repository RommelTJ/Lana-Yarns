from __future__ import unicode_literals

from django.db.models.signals import pre_save, post_save
from decimal import Decimal

from .models import CartItem


def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    qty = int(instance.quantity)
    price = instance.item.get_price()
    line_item_total = Decimal(price * qty)
    instance.line_item_total = line_item_total


pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)


def cart_item_post_save_receiver(sender, instance, created, *args, **kwargs):
    instance.cart.update_subtotal()


post_save.connect(cart_item_post_save_receiver, sender=CartItem)
