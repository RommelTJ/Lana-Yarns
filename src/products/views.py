from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils import timezone
import re

from .models import Product

# Create your views here.

def price_test(query):
    """
    Test if a query string is a price search
    """
    query = query.lstrip().rstrip()
    return re.match('^\d+.\d{1,2}$', query) is not None

class ProductDetailView(DetailView):
    model = Product

class ProductListView(ListView):
    model = Product

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        context['now'] = timezone.now()
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get('q')
        if query:
            if price_test(query):  # search as price
                qs = self.model.objects.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(price=query)
                    )
            else:  # search as title and description
                qs = self.model.objects.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                    )
        return qs

def product_detail_view_func(request, id):
    product_instance = get_object_or_404(Product, id=id)
    template = 'products/product_detail.html'
    context = {
        'object': product_instance,
    }
    return render(request, template, context)