from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView

from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import AddressForm, UserAddressForm
from .mixins import UserCheckoutAPIMixin, LoginRequiredMixin, CartOrderMixin, UserCheckoutMixin
from .models import UserCheckout, UserAddress, Order
from .serializers import UserAddressSerializer

# Create your views here.


# API CBVs

class UserCheckoutAPI(UserCheckoutAPIMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        data = self.get_checkout_data(user=request.user)
        return Response(data)

    def post(self, request, format=None):
        email = request.data.get('email')
        data = self.get_checkout_data(user=request.user, email=email)
        return Response(data)


class UserAddressCreateAPIView(CreateAPIView):
    model = UserAddress
    serializer_class = UserAddressSerializer


class UserAddressListAPIView(ListAPIView):
    model = UserAddress
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer

    def get_queryset(self, *args, **kwargs):
        user_checkout_id = self.request.GET.get('user_checkout_id')
        if self.request.user.is_authenticated():
            return UserAddress.objects.filter(user_checkout__user=self.request.user)
        elif user_checkout_id:
            return UserAddress.objects.filter(user_checkout__id=int(user_checkout_id))
        else:
            return UserAddress.objects.none()


# CBVs

class AddressSelectFormView(FormView, CartOrderMixin, UserCheckoutMixin):
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
        user_checkout = self.get_user_checkout()
        if user_checkout is None:
            # Return empty UserAddress queryset
            return UserAddress.objects.none(), UserAddress.objects.none()
        address_queryset = UserAddress.objects.filter(user_checkout=user_checkout)
        billing_address = address_queryset.filter(type='billing')
        shipping_address = address_queryset.filter(type='shipping')
        return shipping_address, billing_address

    def get_form(self, *args, **kwargs):
        form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
        shipping_address, billing_address = self.get_addresses()
        order = self.get_order()
        form.fields['billing_address'].queryset = billing_address
        form.fields['shipping_address'].queryset = shipping_address
        return form

    def form_valid(self, form, *args, **kwargs):
        shipping_address = form.cleaned_data['shipping_address']
        billing_address = form.cleaned_data['billing_address']
        order = self.get_order()
        order.shipping_address = shipping_address
        order.billing_address = billing_address
        order.save()
        return super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse('checkout')


class UserAddressCreateView(UserCheckoutMixin, CreateView):
    form_class = UserAddressForm
    template_name = 'forms.html'

    def form_valid(self, form, *args, **kwargs):
        user_checkout = self.get_user_checkout()
        if user_checkout is None:
            messages.success(self.request, 'Please confirm your identity before adding address.')
            return redirect('checkout')
        form.instance.user_checkout = user_checkout
        return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse('order_address')


class OrderListView(LoginRequiredMixin, UserCheckoutMixin, ListView):
    queryset = Order.objects.all()

    def get_queryset(self):
        user_checkout = self.get_user_checkout()
        return super(OrderListView, self).get_queryset().filter(user_checkout=user_checkout)


class OrderDetailView(UserCheckoutMixin, DetailView):
    model = Order

    def dispatch(self, request, *args, **kwargs):
        user_checkout = self.get_user_checkout()
        obj = self.get_object()
        if user_checkout is not None and obj.user_checkout == user_checkout:
            return super(OrderDetailView, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404
