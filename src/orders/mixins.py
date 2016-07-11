from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.utils.decorators import method_decorator

from carts.models import Cart
from .models import Order, UserCheckout

User = get_user_model()

# API Mixins

class UserCheckoutAPIMixin(object):

    def user_failure(self, message=None):
        data = {
            'message': 'There was an error. Please try again.',
            'success': False
        }
        if message:
            data['message'] = message
        return data

    def get_checkout_data(self, user=None, email=None):
        if email:
            email = email.lower()
        data = {}
        user_checkout = None
        if user is not None and user.is_authenticated():
            if email is not None and email != user.email:
                data = self.user_failure(message='The user data conflicts to the authenticated user. Please try again.')
            else:
                user_checkout, created = UserCheckout.objects.get_or_create(user=user, email=user.email)
        elif email:
            user_exists = User.objects.filter(email=email).exists()
            if user_exists:
                data = self.user_failure(message='This user already exists. Please login to continue.')
            else:
                try:
                    validate_email(email)
                    email_is_valid = True
                except:
                    email_is_valid = False
                if email_is_valid:
                    user_checkout, created = UserCheckout.objects.get_or_create(email=email)
                else:
                    data = self.user_failure(message='There was an error when parsing the data. Please enter a valid email.')
        else:
            data = self.user_failure()

        if user_checkout:
            data['token'] = user_checkout.get_client_token()
            data['braintree_id'] = user_checkout.braintree_id
            data['user_checkout_id'] = user_checkout.id
            data['success'] = True
        return data


# Mixins

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