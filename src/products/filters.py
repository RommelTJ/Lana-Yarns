from django_filters import FilterSet, CharFilter, NumberFilter

from .models import Product

# Filter Class


class ProductFilter(FilterSet):
    title = CharFilter(name='title', lookup_type='icontains')
    category = CharFilter(name='categories__title', lookup_type='icontains', distinct=True)
    category_id = CharFilter(name='categories__id', lookup_type='iexact', distinct=True)
    min_price = NumberFilter(name='variation__price', lookup_type='gte', distinct=True)
    max_price = NumberFilter(name='variation__price', lookup_type='lte', distinct=True)

    class Meta:
        model = Product
        fields = [
            'title',
            'description',
            'category',
            'min_price',
            'max_price',
        ]
