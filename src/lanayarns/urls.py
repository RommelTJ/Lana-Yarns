"""django_ecommerce2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from newsletter import views as newsletter_views
from . import views as main_views

from orders.views import (
    UserCheckoutAPI,
)

from products.views import (
    APIHomeView,
    ProductListAPIView,
    ProductRetrieveAPIView,
    CategoryListAPIView,
    CategoryRetrieveAPIView,
)

urlpatterns = [
    url(r'^$', newsletter_views.home, name='home'),
    url(r'^contact/$', newsletter_views.contact, name='contact'),
    url(r'^about/$', main_views.about, name='about'),
    url(r'^cart/', include('carts.urls')),
    url(r'^checkout/', include('carts.urls_checkout')),
    url(r'^orders/', include('orders.urls')),
    url(r'^products/', include('products.urls')),
    url(r'^categories/', include('products.urls_categories')),

    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),
]

urlpatterns += [
    url(r'^api/$', APIHomeView.as_view(), name='home_api'),
    url(r'^api/auth/token/$', obtain_jwt_token),
    url(r'^api/auth/token/refresh/$', refresh_jwt_token),
    url(r'^api/user/checkout/$', UserCheckoutAPI.as_view(), name='user_checkout_api'),
    url(r'^api/products/$', ProductListAPIView.as_view(), name='products_api'),
    url(r'^api/products/(?P<pk>\d+)/$', ProductRetrieveAPIView.as_view(), name='product_detail_api'),
    url(r'^api/categories/$', CategoryListAPIView.as_view(), name='categories_api'),
    url(r'^api/categories/(?P<pk>\d+)/$', CategoryRetrieveAPIView.as_view(), name='category_detail_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)