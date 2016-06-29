from carts.models import Cart
from .models import Order


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
