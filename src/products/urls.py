from django.conf.urls import url

from .views import ProductDetailView, ProductListView

urlpatterns = [
    url(r'^$', ProductListView.as_view(), name='ProductListView'),
    url(r'^(?P<pk>\d+)/$', ProductDetailView.as_view(), name='product_detail'),
]
