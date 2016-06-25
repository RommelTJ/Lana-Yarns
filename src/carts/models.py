from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from products.models import Variation

# Create your models here.


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    items = models.ManyToManyField(Variation, through='CartItem')
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    subtotal = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)
    tax_total = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)

    def __unicode__(self):
        return str(self.id)

    def update_subtotal(self):
        items = self.cartitem_set.all()
        subtotal_list = [item.line_item_total for item in items]
        self.subtotal = sum(subtotal_list)
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart)
    item = models.ForeignKey(Variation)
    quantity = models.PositiveIntegerField(default=1)
    line_item_total = models.DecimalField(decimal_places=2, max_digits=20)

    def __unicode__(self):
        return self.item.title

    def remove_url(self):
        return self.item.remove_from_cart()

