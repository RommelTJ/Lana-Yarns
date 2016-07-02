from __future__ import unicode_literals

from django.conf import settings
from django.db.models.signals import pre_save, post_save
from decimal import Decimal

import braintree
from .models import UserCheckout, Order


if settings.DEBUG:
    braintree.Configuration.configure(braintree.Environment.Sandbox,
                                      merchant_id=settings.BRAINTREE_MERCHANT_ID,
                                      public_key=settings.BRAINTREE_PUBLIC,
                                      private_key=settings.BRAINTREE_PRIVATE)


def update_braintree_id(sender, instance, created, *args, **kwargs):
    if not instance.braintree_id:
        result = braintree.Customer.create({
            'email': instance.email,
            })
        if result.is_success:
            instance.braintree_id = result.customer.id
            instance.save()

post_save.connect(update_braintree_id, sender=UserCheckout)


def order_pre_save(sender, instance, *args, **kwargs):
    shipping_total_price = Decimal(instance.shipping_total_price)
    cart_total = Decimal(instance.cart.total)
    order_total = shipping_total_price + cart_total
    instance.order_price = '%.2f' % (order_total)

pre_save.connect(order_pre_save, sender=Order)