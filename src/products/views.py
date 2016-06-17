from django.shortcuts import render, get_object_or_404
from django.views.generic.detail import DetailView

from .models import Product

# Create your views here.

class ProductDetailView(DetailView):
    model = Product

def product_detail_view_func(request, id):
    product_instance = get_object_or_404(Product, id=id)
    template = 'products/product_detail.html'
    context = {
        'object': product_instance,
    }
    return render(request, template, context)