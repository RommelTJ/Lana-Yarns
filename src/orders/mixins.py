from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from carts.models import Cart
from .models import Order, UserCheckout


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class CartOrderMixin(object):

    def get_order(self, *args, **kwargs):
        cart = self.get_cart()
        order_id = self.request.session.get('order_id')
        if order_id:
            new_order = Order.objects.get(id=order_id)
        else:
            new_order = Order.objects.create(cart=cart)
            self.request.session['order_id'] = new_order.id
        return new_order

    def get_cart(self, *args, **kwargs):
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


class UserCheckoutMixin(object):

    def get_user_checkout(self, *args, **kwargs):
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