from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render
from django.views.generic.edit import FormView

from .forms import AddressForm
from .models import UserCheckout, UserAddress

# Create your views here.


class AddressSelectFormView(FormView):
    form_class = AddressForm
    template_name = 'orders/address_select.html'

    def get_form(self, *args, **kwargs):
        form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
        user_checkout_id = self.request.session.get('user_checkout_id')
        if self.request.user.is_authenticated():
            user_checkout, created = UserCheckout.objects.get_or_create(email=self.request.user.email)
            if created:  # Do not validate if the user and the email match
                user_checkout.user = self.request.user
                user_checkout.save()
            if user_checkout_id != user_checkout.id:
                self.request.session['user_checkout_id'] = user_checkout.id
        elif user_checkout_id:
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        else:
            raise Http404
        address_queryset = UserAddress.objects.filter(user_checkout__email=user_checkout.email)
        billing_address = address_queryset.filter(type='billing')
        shipping_address = address_queryset.filter(type='shipping')
        form.fields['billing_address'].queryset = billing_address
        form.fields['shipping_address'].queryset = shipping_address
        return form

    def form_valid(self, form, *args, **kwargs):
        return super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse('checkout')
