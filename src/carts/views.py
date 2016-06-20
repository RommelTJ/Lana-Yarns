from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import render, get_object_or_404, redirect

from products.models import Variation
from .models import Cart, CartItem

# Create your views here.


class CartView(SingleObjectMixin, View):
    model = Cart
    template_name = 'carts/cart_view.html'

    def get_object(self, *args, **kwargs):
        self.request.session.set_expiry(300) # 300 secs
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
        if request.is_ajax():
            cart.update_subtotal() # Refresh data for Ajax
            item_added = cart_item and created
            jsondata = {
                # For product detail view
                'item_added': item_added,
                'item_updated': item_updated,
                'item_deleted': delete_item,
                # For cart detail view
                'line_item_total': cart_item.line_item_total,
                'subtotal': cart.subtotal,
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
