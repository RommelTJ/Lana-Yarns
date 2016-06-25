from __future__ import unicode_literals

from django.db.models.signals import pre_save, post_save
from decimal import Decimal

from .models import Cart, CartItem


def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    qty = int(instance.quantity)
    price = instance.item.get_price()
    line_item_total = Decimal(price * qty)
    instance.line_item_total = line_item_total

pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)


def cart_item_post_save_receiver(sender, instance, created, *args, **kwargs):
    instance.cart.update_subtotal()

post_save.connect(cart_item_post_save_receiver, sender=CartItem)


def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
    subtotal = Decimal(instance.subtotal)
    tax_rate = Decimal(0.085) # 8.5% tax rate
    tax_total = subtotal * tax_rate
    total = subtotal + tax_total
    instance.tax_total = '%.2f' % (tax_total)
    instance.total = '%.2f' % (total)

pre_save.connect(do_tax_and_total_receiver, sender=Cart)
