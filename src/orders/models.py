from __future__ import unicode_literals

from django.conf import settings
from django.db import models

# Create your models here.

ADDRESS_TYPE = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
    )


class UserCheckout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True) # optional
    email = models.EmailField(unique=True) # required
    #merchant_id

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

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"


# class Order(models.Model):
    # cart
    # usercheckout
    # shipping address
    # billing address
    # shipping total price
    # order total price
    # order number
