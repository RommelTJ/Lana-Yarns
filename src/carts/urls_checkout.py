from django.conf.urls import url

from orders.views import AddressSelectFormView, UserAddressCreateView
from .views import CheckoutView

urlpatterns = [
    url(r'^$', CheckoutView.as_view(), name='checkout'),
    url(r'^address/$', AddressSelectFormView.as_view(), name='order_address'),
    url(r'^address/add/$', UserAddressCreateView.as_view(), name='order_address_create'),
]
