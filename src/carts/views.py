from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404

from products.models import Variation
from .models import Cart, CartItem

# Create your views here.


class CartView(View):
    def get(self, request, *args, **kwargs):
        request.session.set_expiry(300) # 300 sec
        cart_id = request.session.get('cart_id')
        if cart_id is None:
            cart = Cart()
            cart.save()
            cart_id = cart.id
            request.session['cart_id'] = cart_id

        cart = Cart.objects.get(id=cart_id)
        if request.user.is_authenticated(): # Login user
            # if the cart is not belong to the current login user, start a new cart
            if cart.user is not None and cart.user != request.user:
                cart = Cart()
                cart.save()
                request.session['cart_id'] = cart.id
            cart.user = request.user
            cart.save()
        else: # Guest user
            if cart.user:
                pass # Required Login or remind user to start a new session

        item_id = request.GET.get('item_id')
        delete_item = request.GET.get('delete')
        qty = request.GET.get('qty')
        # Check order:
        # 1. item_id -- determine the instance
        # 2. delete_item -- determine whether to delete the instance
        # 3. qty -- determine how many instance will be added to the cart
        #           the 'qty' option would not work when 'delete_item' is set to something
        #           By default, 'qty' is set to 1.
        if item_id:
            item_instance = get_object_or_404(Variation, id=item_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
            if delete_item:
                cart_item.delete()
            elif qty:
                cart_item.quantity = qty
                cart_item.save()

        return HttpResponseRedirect('/')
