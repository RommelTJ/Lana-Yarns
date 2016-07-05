from django import forms
from django.forms.models import modelformset_factory

from .models import Category, Variation


class ProductFilterForm(forms.Form):
    title = forms.CharField(label='Keyword', required=False)
    category_id = forms.ModelMultipleChoiceField(
        label='Category',
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    min_price = forms.DecimalField(decimal_places=2, max_digits=12, required=False)
    max_price = forms.DecimalField(decimal_places=2, max_digits=12, required=False)


class VariationInventoryForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = [
            'title',
            'price',
            'sale_price',
            'inventory',
            'active',
        ]

VariationInventoryFormSet = modelformset_factory(Variation, form=VariationInventoryForm, extra=1)
