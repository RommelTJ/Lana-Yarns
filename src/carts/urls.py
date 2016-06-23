from django.conf.urls import url

from .views import CartView, ItemCountView

urlpatterns = [
    url(r'^$', CartView.as_view(), name='cart'),
    url(r'^count$', ItemCountView.as_view(), name='cartitem_count'),
    ]