from django.conf.urls import url

from .views import CheckoutView

urlpatterns = [
    url(r'^$', CheckoutView.as_view(), name='checkout'),
]
