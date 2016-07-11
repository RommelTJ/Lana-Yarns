import ast
import base64

from .models import Cart


class TokenMixin(object):

    def create_token(self, data_dict):
        if type(data_dict) == type(dict()):
            token = base64.b64encode(str(data_dict))
            return token
        else:
            raise ValueError("Creating a token must use a python dictionary.")

    def parse_token(self, token):
        token_decoded = base64.b64decode(token)
        token_dict = ast.literal_eval(token_decoded)
        return token_dict


class CartTokenMixin(TokenMixin):

    def get_cart_from_token(self, cart_token):
        try:
            cart_dict = self.parse_token(cart_token)
            cart_id = cart_dict.get('cart_id')
            cart = Cart.objects.get(id=cart_id)
        except:
            cart = None
        return cart

    def get_token_with_cart(self, token_param):
        token_data = self.request.GET.get(token_param)
        if token_data:
            cart = self.get_cart_from_token(token_data)
        else:
            cart = Cart()
            if self.request.user.is_authenticated():
                cart.user = self.request.user
            cart.save()
            data = {
                'cart_id': cart.id,
            }
            token_data = self.create_token(data)
        return token_data, cart

    def get_ctxdata_with_cart(self, token_param):
        token_data = self.request.GET.get(token_param)
        if token_data:
            cart = self.get_cart_from_token(token_data)
            if cart is not None:
                data = {
                    'success': True,
                    'cart': cart.id,
                }
            else:
                data = {
                    'success': False,
                    'message': 'The cart token is invalid.',
                }
        else:
            cart = None
            data = {
                'success': False,
                'message': 'This requires a valid cart token.',
            }
        return data, cart
