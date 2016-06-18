from __future__ import unicode_literals

from django.db.models.signals import post_save

from .models import Product, Variation

def product_saved_receiver(sender, instance, created, *args, **kwargs):
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product = product
        new_var.price = product.price
        new_var.save()

post_save.connect(product_saved_receiver, sender=Product)