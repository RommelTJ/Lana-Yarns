from django.conf.urls import url

from .views import OrderListView, OrderDetailView

urlpatterns = [
    url(r'^$', OrderListView.as_view(), name='orders'),
    url(r'^(?P<pk>\d+)$', OrderDetailView.as_view(), name='order_detail'),
    ]