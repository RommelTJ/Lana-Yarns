from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from carts.models import Cart

# Create your models here.

ADDRESS_TYPE = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
    )

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('completed', 'Completed'),
    )


class UserCheckout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True) # optional
    email = models.EmailField(unique=True) # required
    braintree_id = models.CharField(max_length=120, null=True, blank=True)

    def __unicode__(self):
        return self.email


class UserAddress(models.Model):
    user_checkout = models.ForeignKey(UserCheckout)
    type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    zipcode = models.CharField(max_length=120)

    def __unicode__(self):
        return self.street

    def get_address(self):
        return '%s\n%s, %s %s' % (self.street, self.city, self.state, self.zipcode)

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"


class Order(models.Model):
    cart = models.OneToOneField(Cart)
    user_checkout = models.ForeignKey(UserCheckout, null=True)
    status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='created')
    shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', null=True)
    billing_address = models.ForeignKey(UserAddress, related_name='billing_address', null=True)
    shipping_total_price = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)
    order_price = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)

    def __unicode__(self):
        return str(self.cart.id)

    def mark_completed(self):
        self.status = 'completed'
        self.save()

