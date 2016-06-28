from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin
from django.shortcuts import render, get_object_or_404, redirect

from orders.forms import GuestCheckoutForm
from orders.models import UserCheckout, UserAddress, Order
from products.models import Variation
from .models import Cart, CartItem

# Create your views here.


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
            # if the cart is not belong to the current login user, start a new cart
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
        flash_message = ""
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
                flash_message = "Item successfully added."
            elif delete_item:
                flash_message = "Item removed successfully."
            elif item_updated:
                flash_message = "Quantity has been updated successfully."
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
        # if update quantity from self page, reload page to recalculate the subtotal
        update_item = request.GET.get('update')
        if update_item:
            return redirect('cart')
        return render(request, template, context)


class CheckoutView(DetailView, FormMixin):
    model = Cart
    template_name = 'carts/checkout_view.html'
    form_class = GuestCheckoutForm

    def get_object(self, *args, **kwargs):
        cart_id = self.request.session.get('cart_id')
        if cart_id is None:
            return redirect('cart')
        cart = Cart.objects.get(id=cart_id)
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

        # # 1. Get shopping cart
        # cart = self.get_object()
        # user_checkout_id = request.session.get('user_checkout_id')
        # if user_checkout_id:
        #     user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        # shipping_address_id = request.session.get('shipping_address_id')
        # billing_address_id = request.session.get('billing_address_id')

        # # 2. Get shipping address and billing address
        # if shipping_address_id is None or billing_address_id is None:
        #     return redirect('checkout_address')
        # shipping_address = UserAddress.objects.get(id=shipping_address_id)
        # billing_address = UserAddress.objects.get(id=billing_address_id)

        # # 3. Get order
        # order_id = request.session.get('order_id')
        # if order_id:
        #     new_order = Order.objects.get(id=order_id)
        # else:
        #     new_order = Order()
        #     new_order.save()
        #     request.session['order_id'] = new_order.id

        # new_order.cart = cart
        # new_order.user_checkout = user_checkout
        # new_order.shipping_address = shipping_address
        # new_order.billing_address = billing_address
        # new_order.save()
        return get_data
