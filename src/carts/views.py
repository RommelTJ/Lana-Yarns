from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin
from django.shortcuts import render, get_object_or_404, redirect

import braintree

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.forms import GuestCheckoutForm
from orders.mixins import CartOrderMixin
from orders.models import UserAddress, UserCheckout, Order
from orders.serializers import OrderSerializer
from products.models import Variation
from .mixins import CartTokenMixin
from .models import Cart, CartItem
from .serializers import CartItemSerializer

# Braintree settings
if settings.DEBUG:
    braintree.Configuration.configure(braintree.Environment.Sandbox,
                                      merchant_id=settings.BRAINTREE_MERCHANT_ID,
                                      public_key=settings.BRAINTREE_PUBLIC,
                                      private_key=settings.BRAINTREE_PRIVATE)


# Create your views here.


# API CBVs

class CartAPIView(CartTokenMixin, APIView):

    def update_cart(self, cart, *args, **kwargs):
        # cart, token = self.get_cart_token()
        if cart is not None:
            item_id = self.request.GET.get('item_id')
            delete_item = self.request.GET.get('delete', False)
            qty = self.request.GET.get('qty')
            flash_message = ''
            # Check order:
            # 1. item_id -- determine the instance
            # 2. delete_item -- determine whether to delete the instance
            # 3. qty -- determine how many instance will be added to the cart
            #           the 'qty' option would not work when 'delete_item' is set to something
            #           By default, 'qty' is set to 1.
            if item_id:
                item_exists = Variation.objects.filter(id=item_id).exists()
                if item_exists:
                    item_instance = Variation.objects.get(id=item_id)
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
                    item_updated = False # For Ajax
                    if delete_item:
                        cart_item.delete()
                        cart.update_subtotal()  # Recalculate subtotal
                    elif qty:
                        if qty.isdigit() and int(qty) > 0:
                            if cart_item.quantity != qty:
                                cart_item.quantity = qty
                                cart_item.save()
                                item_updated = True # For Ajax
                        else:
                            # messages.error(self.request, "The input quantity is not valid. Add to cart operation fails.")
                            if created:
                                cart_item.delete()
                    # Ensure the cart subtotal is recalculated
                    if item_updated:
                        cart.update_subtotal()
                    # Check operation status
                    item_added = cart_item and created
                    if item_added:
                        flash_message = 'Item successfully added.'
                    elif delete_item:
                        flash_message = 'Item removed successfully.'
                    elif item_updated:
                        flash_message = 'Quantity has been update successfully.'

    def get(self, request, format=None):
        token, cart = self.get_token_with_cart('token')
        if cart is not None:
            # only allow update cart which belongs to no one
            if cart.user is None:
                self.update_cart(cart)
            items = CartItemSerializer(cart.cartitem_set.all(), many=True)
            data = {
                'cart': cart.id,
                'sub_total': cart.subtotal,
                'tax_total': cart.tax_total,
                'total': cart.total,
                'count': cart.cartitem_set.count(),
                'items': items.data,
                'token': token,
            }
            return Response(data)
        else:
            data = {
                'success': False,
                'detail': 'invalid token. object not found.',
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class CheckoutAPIView(CartTokenMixin, APIView):
    """
    Currently, this API only supports user checkout token method, instead of user authenticate method
    """
    def get(self, request, format=None):
        # ensure user checkout is required
        user_checkout_token = self.request.GET.get('user_checkout_token')
        try:
            user_checkout_data = self.parse_token(user_checkout_token)
            user_checkout_id = user_checkout_data.get('user_checkout_id')
        except:
            user_checkout_id = None

        try:
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        except:
            user_checkout = None
        if user_checkout is None:
            data = {
                'message': 'Your user account is not authenticated.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data, cart_obj = self.get_ctxdata_with_cart('cart_token')
        get_data_succeed = data.get('success')
        if get_data_succeed:
            if cart_obj.cartitem_set.count() == 0:
                data = {
                    'message': 'Your cart is empty.'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                order, created = Order.objects.get_or_create(cart=cart_obj)
                if created or (not order.user_checkout):
                    order.user_checkout = user_checkout
                    order.save()
                if order.user_checkout != user_checkout:
                    data = {
                        'message': 'There was some errors with user authentication. Please check your user account.',
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if order.is_paid:
                    data = {
                        'message': 'This order has been paid(complete).',
                    }
                    return Response(data)

                # billing and shipping address
                billing_address_id = self.request.GET.get('billing_address_id')
                shipping_address_id = self.request.GET.get('shipping_address_id')
                try:
                    billing_address = UserAddress.objects.get(user_checkout=user_checkout, type='billing', id=int(billing_address_id))
                except:
                    billing_address = None
                try:
                    shipping_address = UserAddress.objects.get(user_checkout=user_checkout, type='shipping', id=int(shipping_address_id))
                except:
                    shipping_address = None

                if billing_address:
                    order.billing_address = billing_address
                    order.save()
                if shipping_address:
                    order.shipping_address = shipping_address
                    order.save()

                if (order.billing_address is None) and (order.shipping_address is None):
                    data = {
                        'message': 'The billing address and shipping address are missing. Please add valid addresses to make the order.',
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                elif order.billing_address is None:
                    data = {
                        'message': 'The billing address is missing. Please add valid address to make the order.',
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                elif order.shipping_address is None:
                    data = {
                        'message': 'The shipping address is missing. Please add valid address to make the order.',
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

                data = OrderSerializer(order).data
                return Response(data)
        else:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

# CBVs

class ItemCountView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
                cartitem_count = cart.cartitem_set.count()
            else:
                cartitem_count = 0
            self.request.session['cartitem_count'] = cartitem_count
            return JsonResponse({'cartitem_count': cartitem_count})
        else:
            raise Http404

class CartView(SingleObjectMixin, View):
    model = Cart
    template_name = 'carts/cart_view.html'

    def get_object(self, *args, **kwargs):
        self.request.session.set_expiry(900) # 900 secs
        cart_id = self.request.session.get('cart_id')
        if cart_id is None:
            cart = Cart()
            cart.save()
            cart_id = cart.id
            self.request.session['cart_id'] = cart_id

        cart = Cart.objects.get(id=cart_id)
        if self.request.user.is_authenticated(): # Login user
            # if the cart is not belong to the current login user,
            # start a new cart
            if cart.user is not None and cart.user != self.request.user:
                cart = Cart()
                cart.save()
                self.request.session['cart_id'] = cart.id
            cart.user = self.request.user
            cart.save()
        else: # Guest user
            if cart.user:
                pass # Required Login or remind user to start a new session
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        item_id = request.GET.get('item_id')
        delete_item = request.GET.get('delete', False)
        qty = request.GET.get('qty')
        flash_message = ''
        # Check order:
        # 1. item_id -- determine the instance
        # 2. delete_item -- determine whether to delete the instance
        # 3. qty -- determine how many instance will be added to the cart
        #           the 'qty' option would not work when 'delete_item' is set to something
        #           By default, 'qty' is set to 1.
        if item_id:
            item_instance = get_object_or_404(Variation, id=item_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
            item_updated = False # For Ajax
            if delete_item:
                cart_item.delete()
                cart.update_subtotal()  # Recalculate subtotal
            elif qty:
                if qty.isdigit() and int(qty) > 0:
                    if cart_item.quantity != qty:
                        cart_item.quantity = qty
                        cart_item.save()
                        item_updated = True # For Ajax
                else:
                    messages.error(request, "The input quantity is not valid. Add to cart operation fails.")
                    if created:
                        cart_item.delete()
            # Check operation status
            item_added = cart_item and created
            if item_added:
                flash_message = 'Item successfully added.'
            elif delete_item:
                flash_message = 'Item removed successfully.'
            elif item_updated:
                flash_message = 'Quantity has been update successfully.'
        if request.is_ajax():
            # Refresh data for Ajax request
            cart.update_subtotal()
            cartitem_count = cart.cartitem_set.count()

            jsondata = {
                'flash_message': flash_message,
                # For cart detail view only
                'line_item_total': cart_item.line_item_total,
                'cart_subtotal': cart.subtotal,
                'cart_tax_total': cart.tax_total,
                'cart_total': cart.total,
                'cartitem_count': cartitem_count,
            }
            return JsonResponse(jsondata)

        context = {
            'object': cart,
        }
        template = self.template_name
        # if update quantity from self page, Reload page to recalculate the subtotal
        update_item = request.GET.get('update')
        if update_item:
            return redirect('cart')
        return render(request, template, context)

class CheckoutView(FormMixin, CartOrderMixin, DetailView):
    model = Cart
    template_name = 'carts/checkout_view.html'
    form_class = GuestCheckoutForm

    def get_object(self, *args, **kwargs):
        cart = self.get_cart()
        return cart

    def get_context_data(self, *args, **kwargs):
        context = super(CheckoutView, self).get_context_data(*args, **kwargs)
        user_checkout_id = self.request.session.get('user_checkout_id')
        if self.request.user.is_authenticated() or user_checkout_id:
            context['user_can_continue'] = True
        else:
            context['user_can_continue'] = False
            context['login_form'] = AuthenticationForm()
            context['next_url'] = self.request.build_absolute_uri()
        if self.request.user.is_authenticated():
            user_checkout, created = UserCheckout.objects.get_or_create(email=self.request.user.email)
            if created:  # Do not validate if the user and the email match
                user_checkout.user = self.request.user
                user_checkout.save()
            self.request.session['user_checkout_id'] = user_checkout.id
            context['client_token'] = user_checkout.get_client_token()
        elif user_checkout_id:
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            context['client_token'] = user_checkout.get_client_token()
        context['order'] = self.get_order()
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Assign the object to the view
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user_checkout, created = UserCheckout.objects.get_or_create(email=email)
            request.session['user_checkout_id'] = user_checkout.id
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('checkout')

    def get(self, request, *args, **kwargs):
        get_data = super(CheckoutView, self).get(request, *args, **kwargs)

        # 1. Get shopping cart
        cart = self.get_object()
        if cart.cartitem_set.count() == 0:
            return redirect('cart')

        # 2. Get order
        new_order = self.get_order()

        # 3. Get user_checkout
        user_checkout_id = request.session.get('user_checkout_id')
        if user_checkout_id:
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        else:
            # If user_checkout_id is None, stop continuing gathering order data
            return get_data

        # 4. Confirm shipping and billing address
        if new_order.shipping_address is None or new_order.billing_address is None:
            return redirect('order_address')

        # 5. Save the order
        new_order.user_checkout = user_checkout
        new_order.save()
        return get_data

class CheckoutFinalView(CartOrderMixin, View):
    def post(self, request, *args, **kwargs):
        # Get the order
        order = self.get_order()
        order_price = order.order_price
        if order.cart.cartitem_set.count == 0:
            return reverse('cart')
        # Validate payment
        nonce = request.POST.get('payment_method_nonce')
        if nonce:
            result = braintree.Transaction.sale({
                'amount': str(order_price),
                'payment_method_nonce': nonce,
                'billing': {
                    'street_address': order.billing_address.street,
                    'locality': order.billing_address.city,
                    'region': order.billing_address.state,
                    'postal_code': order.billing_address.zipcode,
                    'country_code_alpha2': 'US'    # default country
                },
                'shipping': {
                    'street_address': order.shipping_address.street,
                    'locality': order.shipping_address.city,
                    'region': order.shipping_address.state,
                    'postal_code': order.shipping_address.zipcode,
                    'country_code_alpha2': 'US'    # default country
                },
                'options': {
                    'submit_for_settlement': True
                }
            })
            if result.is_success:
                # Add result.transaction.id to order
                order.mark_paid(result.transaction.id)
                del request.session['cart_id']
                del request.session['order_id']
                messages.success(request, 'Your order has been completed. Thank you for your order.')
            else:
                messages.error(request, result.message)
                return redirect('checkout')
        return redirect('order_detail', pk=order.pk)

    def get(self, request, *args, **kwargs):
        return redirect('orders')