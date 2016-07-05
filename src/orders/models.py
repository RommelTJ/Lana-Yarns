from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

import braintree
from carts.models import Cart

# Create your models here.

if settings.DEBUG:
    braintree.Configuration.configure(braintree.Environment.Sandbox,
                                      merchant_id=settings.BRAINTREE_MERCHANT_ID,
                                      public_key=settings.BRAINTREE_PUBLIC,
                                      private_key=settings.BRAINTREE_PRIVATE)

ADDRESS_TYPE = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
    )

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
    ('completed', 'Completed'),
    )


class UserCheckout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True) # optional
    email = models.EmailField(unique=True) # required
    braintree_id = models.CharField(max_length=120, null=True, blank=True)

    def __unicode__(self):
        return self.email

    def get_braintree_id(self):
        if not self.braintree_id:
            result = braintree.Customer.create({
                'email': self.email,
                })
            if result.is_success:
                self.braintree_id = result.customer.id
                self.save()

    def get_client_token(self):
        self.get_braintree_id()
        customer_id = self.braintree_id
        client_token = braintree.ClientToken.generate({
            'customer_id': customer_id
            })
        return client_token


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
    transaction_id = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return str(self.cart.id)

    class Meta:
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

    def mark_paid(self, transaction_id=None):
        if transaction_id:
            self.transaction_id = transaction_id
            self.status = 'paid'
            self.save()
        elif self.transaction_id:
            self.status = 'paid'
            self.save()
