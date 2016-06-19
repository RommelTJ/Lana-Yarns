from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils import timezone
import re

from .models import Product, Variation, Category
from .forms import VariationInventoryFormSet
from .mixins import StaffRequiredMixin

# Create your views here.


def price_test(query):
    """
    Test if a query string is a price search
    """
    query = query.lstrip().rstrip()
    return re.match('^\d+.\d{1,2}$', query) is not None


class ProductDetailView(DetailView):
    model = Product

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        instance = self.get_object()
        context['related'] = Product.objects.get_related(instance).order_by('?')[:6]
        return context


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


class VariationListView(StaffRequiredMixin, ListView):
    model = Variation

    def get_context_data(self, *args, **kwargs):
        context = super(VariationListView, self).get_context_data(*args, **kwargs)
        context['formset'] = VariationInventoryFormSet(queryset=self.get_queryset())
        return context

    def get_queryset(self, *args, **kwargs):
        product_pk = self.kwargs.get('pk')
        if product_pk:
            product = get_object_or_404(Product, pk=product_pk)
            queryset = Variation.objects.filter(product=product)
        return queryset

    def post(self, request, *args, **kwargs):
        formset = VariationInventoryFormSet(request.POST, request.FILES)
        product_pk = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_pk)
        if formset.is_valid():
            for index, form in enumerate(formset):
                new_item = form.save(commit=False)
                # Test if it is the last form (the extra form)
                if index < len(formset):
                    # Empty data is allowed in extra form
                    if not new_item.title:
                        continue
                new_item.product = product
                new_item.save()
            messages.success(request, 'Your inventory and pricing have been updated.')
            return redirect('product_detail', pk=product_pk)
        raise Http404


class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.all()


class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        product_set = obj.product_set.all()
        default_products = obj.default_category.all()
        products = ( product_set | default_products ).distinct()
        context['products'] = products
        return context


def product_detail_view_func(request, id):
    product_instance = get_object_or_404(Product, id=id)
    template = 'products/product_detail.html'
    context = {
        'object': product_instance,
    }
    return render(request, template, context)