from __future__ import unicode_literals

from django.conf import settings
from django.db import models

# Create your models here.


class UserCheckout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True) # optional
    email = models.EmailField(unique=True) # required
    #merchant_id

    def __unicode__(self):
        return self.email


# class Order(models.Model):
    # cart
    # usercheckout
    # shipping address
    # billing address
    # shipping total price
    # order total price
    # order number
