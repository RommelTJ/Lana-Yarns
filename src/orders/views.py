from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView

from .forms import AddressForm, UserAddressForm
from .models import UserCheckout, UserAddress

# Create your views here.


class AddressSelectFormView(FormView):
    form_class = AddressForm
    template_name = 'orders/address_select.html'

    def dispatch(self, *args, **kwargs):
        shipping_address, billing_address = self.get_addresses()
        if billing_address.count() == 0:
            messages.success(self.request, 'Please add a billing address before continuing.')
            return redirect('order_address_create')
        elif shipping_address.count() == 0:
            messages.success(self.request, 'Please add a shipping address before continuing.')
            return redirect('order_address_create')
        return super(AddressSelectFormView, self).dispatch(*args, **kwargs)

    def get_addresses(self, *args, **kwargs):
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
            # Return empty UserAddress queryset
            return UserAddress.objects.none(), UserAddress.objects.none()
        address_queryset = UserAddress.objects.filter(user_checkout=user_checkout)
        billing_address = address_queryset.filter(type='billing')
        shipping_address = address_queryset.filter(type='shipping')
        return shipping_address, billing_address

    def get_form(self, *args, **kwargs):
        form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
        shipping_address, billing_address = self.get_addresses()
        form.fields['billing_address'].queryset = billing_address
        form.fields['shipping_address'].queryset = shipping_address
        return form

    def form_valid(self, form, *args, **kwargs):
        shipping_address = form.cleaned_data['shipping_address']
        billing_address = form.cleaned_data['billing_address']
        self.request.session['shipping_address_id'] = shipping_address.id
        self.request.session['billing_address_id'] = billing_address.id
        return super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse('checkout')


class UserAddressCreateView(CreateView):
    form_class = UserAddressForm
    template_name = 'forms.html'

    def get_user_checkout(self):
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
            return None
        return user_checkout

    def form_valid(self, form, *args, **kwargs):
        user_checkout = self.get_user_checkout()
        if user_checkout is None:
            messages.success(self.request, 'Please confirm your identity before adding address.')
            return redirect('checkout')
        form.instance.user_checkout = user_checkout
        return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse('order_address')
